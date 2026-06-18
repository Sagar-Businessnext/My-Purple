"""The voice loop: wait for the wake word, record the spoken command until silence,
transcribe it, run it through the agent, and speak the reply.

The continuous mic capture runs in a background thread; async work (STT, the agent,
TTS) is scheduled onto the main event loop. The command-processing logic
(process_command) is fully testable with fakes — no audio hardware required.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import threading
from typing import Any

import numpy as np

from purple.config import settings
from purple.tools.permissions import auto_deny
from purple.utils.logging import get_logger
from purple.voice.vad import is_speech
from purple.voice.wake import WakeListener

log = get_logger("voice.loop")

FRAME = 1280  # 80 ms at 16 kHz
EmitFn = Callable[[dict[str, Any]], Awaitable[None]]


class VoiceLoop:
    def __init__(
        self,
        agent: Any,
        speech: Any,
        emit: EmitFn | None = None,
        wake: WakeListener | None = None,
    ) -> None:
        self.agent = agent
        self.speech = speech
        self.emit = emit
        self.wake = wake or WakeListener()
        self.main_loop: asyncio.AbstractEventLoop | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._player: Any | None = None  # current StreamingVoice (for barge-in cancel)

    # --- async work (testable) ---
    async def _emit(self, event: dict[str, Any]) -> None:
        if self.emit:
            await self.emit(event)

    async def process_command(self, audio_int16: np.ndarray) -> tuple[str, str]:
        from purple import speaker

        gate = await asyncio.to_thread(speaker.authorize, audio_int16, settings.sample_rate)
        if not gate["allow"]:
            log.info("voice_gated", reason=gate["reason"])
            await self._emit({"type": "voice", "state": "not_recognized", "reason": gate["reason"]})
            if gate["reason"] == "verifier_unavailable":  # fail-closed: warn loudly
                await self._emit(
                    {"type": "alert", "priority": "important", "source": "self",
                     "title": "Voice locked", "detail": "can't verify your voice — voice is off"}
                )
            await self._emit({"type": "voice", "state": "listening"})
            return "", ""

        path = self._write_wav(audio_int16)
        transcript = await self.speech.transcribe(path)
        await self._emit({"type": "voice", "state": "heard", "text": transcript})
        if not transcript.strip():
            await self._emit({"type": "voice", "state": "listening"})
            return "", ""
        reply = await self.agent.respond(transcript, approver=auto_deny)
        await self._emit({"type": "voice", "state": "reply", "text": reply})
        await self._speak_reply(reply)
        await self._emit({"type": "voice", "state": "listening"})
        return transcript, reply

    async def _speak_reply(self, reply: str) -> None:
        """Speak a reply sentence-by-sentence so long answers start playing immediately
        and can be cancelled mid-stream (barge-in). Falls back to one-shot on config off."""
        if not reply.strip():
            return
        if not settings.stream_voice:
            self._play(await self.speech.synthesize(reply))
            return
        from purple.voice.streaming import StreamingVoice, flush_sentences

        sentences, tail = flush_sentences(reply)
        if tail.strip():
            sentences.append(tail.strip())

        async def _aiter() -> Any:
            for s in sentences:
                yield s

        async def _play(audio: bytes) -> None:
            await asyncio.to_thread(self._play, audio)

        self._player = StreamingVoice(self.speech.synthesize, _play)
        if not settings.enable_barge_in:
            await self._player.speak(_aiter())
            return
        monitor = asyncio.create_task(self._barge_monitor())
        try:
            await self._player.speak(_aiter())
        finally:
            monitor.cancel()

    async def _barge_monitor(self) -> None:
        """While Purple speaks, listen for an interruption; cancel playback if heard.
        Best-effort (its own short mic stream) — the interrupting utterance is still
        speaker-gated before anything is acted on. Live behaviour verified on the PC."""

        def _watch() -> bool:
            try:
                import sounddevice as sd

                with sd.InputStream(
                    samplerate=settings.sample_rate, channels=1, dtype="int16", blocksize=FRAME
                ) as s:
                    for _ in range(int(30_000 / 80)):  # watch up to 30 s of speaking
                        if self._player is None or self._player.cancelled:
                            return False
                        data, _flag = s.read(FRAME)
                        if is_speech(np.asarray(data).reshape(-1), settings.vad_threshold):
                            return True
            except Exception as exc:
                log.warning("barge_monitor_failed", error=str(exc))
            return False

        heard = await asyncio.to_thread(_watch)
        if heard and self._player is not None:
            self._player.cancel()
            await self._emit({"type": "voice", "state": "barge_in"})

    # --- audio helpers ---
    @staticmethod
    def _write_wav(audio_int16: np.ndarray) -> str:
        import tempfile
        import wave

        fh = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)  # noqa: SIM115
        with wave.open(fh, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(settings.sample_rate)
            wf.writeframes(np.asarray(audio_int16, dtype=np.int16).tobytes())
        fh.close()
        return fh.name

    def _play(self, wav_bytes: bytes) -> None:
        from purple import audio

        audio.play_wav(wav_bytes)  # routes to the current default output device, best-effort

    # --- mic capture (thread) ---
    def _record_command(self, stream: Any, start_timeout_frames: int | None = None) -> np.ndarray:
        """Capture one utterance. If start_timeout_frames is set and no speech begins in
        that window, return empty (used to end a conversation after silence)."""
        frames: list[np.ndarray] = []
        max_silence = max(1, int(settings.silence_ms / 80))
        max_frames = int(15_000 / 80)  # 15 s ceiling
        silence = 0
        spoke = False
        waited = 0
        for _ in range(max_frames):
            data, _flag = stream.read(FRAME)
            frame = np.asarray(data).reshape(-1)
            speaking = is_speech(frame, settings.vad_threshold)
            if not spoke:  # still waiting for the user to start
                if speaking:
                    spoke = True
                else:
                    waited += 1
                    if start_timeout_frames and waited >= start_timeout_frames:
                        return np.zeros(0, dtype=np.int16)
                    continue
            frames.append(frame)
            if speaking:
                silence = 0
            else:
                silence += 1
                if silence >= max_silence:
                    break
        return np.concatenate(frames) if frames else np.zeros(0, dtype=np.int16)

    def _schedule(self, coro: Awaitable[None]) -> None:
        if self.main_loop is not None:
            asyncio.run_coroutine_threadsafe(coro, self.main_loop)

    def _run(self) -> None:
        try:
            import sounddevice as sd

            import sounddevice as _sd

            try:
                dev = _sd.query_devices(kind="input")
                log.info("voice_input_device", name=dev.get("name", "?"))
            except Exception as exc:
                log.warning("voice_no_input_device", error=str(exc))
            with sd.InputStream(
                samplerate=settings.sample_rate, channels=1, dtype="int16", blocksize=FRAME
            ) as stream:
                self._schedule(self._emit({"type": "voice", "state": "listening"}))
                peak = 0.0
                frames = 0
                while not self._stop.is_set():
                    data, _flag = stream.read(FRAME)
                    frame = np.asarray(data).reshape(-1)
                    score = self.wake.score(frame)
                    peak = max(peak, score)
                    frames += 1
                    if frames >= 150:  # ~12s: prove the mic is heard + how close to waking
                        log.info("wake_listening", peak=round(peak, 3), threshold=self.wake.threshold)
                        peak = 0.0
                        frames = 0
                    if score >= self.wake.threshold:
                        log.info("wake_detected", score=round(score, 3))
                        self._schedule(self._emit({"type": "voice", "state": "woke"}))
                        self._converse(stream)
                        self.wake.reset()
                        peak = 0.0
                        frames = 0
        except Exception as exc:
            log.warning("voice_loop_stopped", error=str(exc))

    def _converse(self, stream: Any) -> None:
        """One wake → a back-and-forth: listen → reply → listen, until the user goes quiet
        (conversation mode). With conversation mode off this runs exactly one exchange."""
        from purple.voice.streaming import conversation_continues

        idle = max(1, int(settings.conversation_idle_seconds * 1000 / 80))
        first = True
        while not self._stop.is_set() and self.main_loop is not None:
            audio = self._record_command(stream, None if first else idle)
            if audio.size == 0:  # idle timeout — end the conversation
                break
            transcript = ""
            fut = asyncio.run_coroutine_threadsafe(self.process_command(audio), self.main_loop)
            try:
                transcript, _reply = fut.result(timeout=120)
            except Exception as exc:
                log.warning("voice_command_failed", error=str(exc))
            first = False
            if not conversation_continues(transcript, settings.conversation_mode):
                break

    def push_to_talk(self) -> None:
        """One-shot capture + process for a hotkey press (own short-lived thread).
        Skips the wake word — pressing the hotkey is the trigger."""

        def _job() -> None:
            try:
                import sounddevice as sd

                with sd.InputStream(
                    samplerate=settings.sample_rate, channels=1, dtype="int16", blocksize=FRAME
                ) as stream:
                    self._schedule(self._emit({"type": "voice", "state": "woke"}))
                    audio = self._record_command(stream)
                if self.main_loop is not None:
                    asyncio.run_coroutine_threadsafe(self.process_command(audio), self.main_loop)
            except Exception as exc:
                log.warning("ptt_failed", error=str(exc))

        threading.Thread(target=_job, name="ptt", daemon=True).start()

    def start(self, main_loop: asyncio.AbstractEventLoop | None = None) -> None:
        self.main_loop = main_loop or asyncio.get_event_loop()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="voice-loop", daemon=True)
        self._thread.start()
        log.info("voice_loop_started", wake=self.wake.wake_model)

    def stop(self) -> None:
        self._stop.set()
