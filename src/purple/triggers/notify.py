"""Notifier — gets your attention by priority.

Channels: the UI activity feed (always), a Windows toast, and the voice (top layer).
Voice and toast are suppressed during Focus mode (gaming/rendering) and quiet hours,
EXCEPT for important/urgent events, which break through with one short, gentle spoken
line — because mid-game you won't see a toast, so voice is the only thing that reaches
you. Breakthroughs are debounced so Purple never nags.
"""

from __future__ import annotations

import time

from purple import audio, focus
from purple.events import bus
from purple.triggers.priority import Event, in_quiet_hours, should_breakthrough
from purple.utils.logging import get_logger

log = get_logger("notify")

_DEBOUNCE_SECONDS = 120


def plan_channels(
    *, breakthrough: bool, quiet: bool, yielding: bool, audible: bool, debounced: bool
) -> tuple[bool, bool]:
    """Pure: decide (speak?, toast?). Voice is the top layer but only if it can be heard;
    if we wanted to speak and it can't land (muted / no device), fall back to a toast even
    in quiet hours — a failed delivery isn't a normal nudge, it still needs to reach you."""
    want_voice = breakthrough or (not yielding and not quiet)
    speak_now = want_voice and audible and not debounced
    voice_cant_land = want_voice and not audible
    toast_now = (not quiet or breakthrough) or voice_cant_land
    return speak_now, toast_now


async def speak(text: str) -> bool:
    """Synthesize with the configured (natural) voice and play it. Returns True if played."""
    try:
        from purple.speech.base import get_speech_provider

        wav = await get_speech_provider().synthesize(text)
        if wav:
            _play(wav)
            return True
    except Exception as exc:
        log.warning("speak_failed", error=str(exc))
    return False


def _play(wav_bytes: bytes) -> None:
    import io
    import wave

    import numpy as np
    import sounddevice as sd

    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
    sd.play(np.frombuffer(data, dtype=np.int16), sr)
    sd.wait()


async def toast(title: str, message: str) -> None:
    import asyncio

    def _do() -> None:
        try:
            from win11toast import toast as win_toast

            win_toast(title, message)
        except Exception:
            pass

    await asyncio.to_thread(_do)


class Notifier:
    def __init__(self) -> None:
        self._recent: dict[str, float] = {}

    def _debounced(self, key: str) -> bool:
        now = time.time()
        if now - self._recent.get(key, 0) < _DEBOUNCE_SECONDS:
            return True
        self._recent[key] = now
        return False

    async def notify(self, event: Event) -> dict:
        breakthrough = should_breakthrough(event)
        quiet = in_quiet_hours()
        yielding = focus.should_yield_gpu()  # gaming/rendering -> don't interrupt
        audible = audio.can_be_heard()  # can my voice actually be heard right now?
        debounced = self._debounced(f"{event.source}:{event.title}")
        channels = ["feed"]

        # The UI activity feed always receives it.
        await bus.broadcast(
            {
                "type": "alert",
                "priority": event.priority,
                "title": event.title,
                "detail": event.detail,
                "source": event.source,
            }
        )

        speak_now, toast_now = plan_channels(
            breakthrough=breakthrough,
            quiet=quiet,
            yielding=yielding,
            audible=audible,
            debounced=debounced,
        )
        if toast_now:
            await toast(event.title, event.detail)
            channels.append("toast")
        if speak_now:
            line = event.title if not event.detail else f"{event.title}. {event.detail}"
            if await speak(line):
                channels.append("voice")

        log.info(
            "notified", source=event.source, priority=event.priority,
            channels=channels, audible=audible,
        )
        return {
            "priority": event.priority,
            "channels": channels,
            "breakthrough": breakthrough,
            "audible": audible,
        }
