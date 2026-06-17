"""Fully-local speech: faster-whisper for STT, a natural neural voice for TTS.

TTS engine is chosen by PURPLE_TTS_ENGINE:
  - "kokoro" (default): Kokoro — natural, warm, CPU-light ("her"-style af_bella voice).
  - "xtts": Coqui XTTS-v2 — zero-shot voice cloning from a reference clip (backup).
Piper is gone — no robotic voice. Models load lazily, so importing this is cheap.
"""

from __future__ import annotations

import asyncio
import io
import wave

from purple.config import settings
from purple.speech.base import SpeechProvider
from purple.utils.logging import get_logger

log = get_logger("speech.local")


def _to_wav(samples: object, sample_rate: int) -> bytes:
    """Float32 [-1,1] samples -> 16-bit mono WAV bytes."""
    import numpy as np

    pcm = (np.clip(np.asarray(samples, dtype="float32"), -1.0, 1.0) * 32767).astype("int16")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(int(sample_rate))
        wav.writeframes(pcm.tobytes())
    return buf.getvalue()


class LocalSpeech(SpeechProvider):
    def __init__(self) -> None:
        self._whisper = None
        self._kokoro = None
        self._xtts = None

    # --- STT (faster-whisper) ---
    def _ensure_whisper(self) -> object:
        if self._whisper is None:
            from faster_whisper import WhisperModel

            log.info("loading_whisper", model=settings.whisper_model, device=settings.whisper_device)
            self._whisper = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute,
            )
        return self._whisper

    def _transcribe_sync(self, audio_path: str) -> str:
        segments, _info = self._ensure_whisper().transcribe(audio_path, vad_filter=True)
        return " ".join(seg.text.strip() for seg in segments).strip()

    async def transcribe(self, audio_path: str) -> str:
        return await asyncio.to_thread(self._transcribe_sync, audio_path)

    # --- TTS ---
    def _ensure_kokoro(self) -> object:
        if self._kokoro is None:
            from kokoro_onnx import Kokoro

            d = settings.models_dir / "kokoro"
            onnx, voices = d / "kokoro-v1.0.onnx", d / "voices-v1.0.bin"
            if not onnx.exists() or not voices.exists():
                raise FileNotFoundError(
                    f"Kokoro model files missing in {d} (kokoro-v1.0.onnx + voices-v1.0.bin) — "
                    "setup.ps1 downloads them."
                )
            log.info("loading_kokoro", voice=settings.kokoro_voice)
            self._kokoro = Kokoro(str(onnx), str(voices))
        return self._kokoro

    def _kokoro_sync(self, text: str) -> bytes:
        kok = self._ensure_kokoro()
        samples, sr = kok.create(
            text, voice=settings.kokoro_voice, speed=settings.kokoro_speed, lang="en-us"
        )
        return _to_wav(samples, sr)

    def _xtts_sync(self, text: str) -> bytes:
        if self._xtts is None:
            from TTS.api import TTS

            log.info("loading_xtts")
            self._xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        samples = self._xtts.tts(
            text=text, speaker_wav=settings.xtts_speaker_wav or None, language="en"
        )
        return _to_wav(samples, 24000)

    def _synthesize_sync(self, text: str) -> bytes:
        if settings.tts_engine == "xtts":
            return self._xtts_sync(text)
        return self._kokoro_sync(text)

    async def synthesize(self, text: str) -> bytes:
        return await asyncio.to_thread(self._synthesize_sync, text)
