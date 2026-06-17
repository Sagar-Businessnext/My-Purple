"""Audio output state — so Purple knows whether her voice can actually be heard.

The detail is Windows-specific (pycaw / Core Audio). On other platforms, or if pycaw
isn't installed, we can't tell — so we assume audio is fine (don't suppress her voice
over a false negative). Never raises.
"""

from __future__ import annotations

from purple.utils.logging import get_logger

log = get_logger("audio")


def _audible(available: bool, muted: bool, volume: float) -> bool:
    """Pure decision: can a spoken line actually be heard right now?"""
    return available and not muted and volume > 0.0


def output_state() -> dict:
    """Best-effort default-output state: {available, muted, volume, known}. Never raises.

    known=False means we couldn't query (no pycaw / not Windows) — callers should assume
    audio is fine rather than silence her.
    """
    try:
        from ctypes import POINTER, cast

        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except Exception:
        return {"available": True, "muted": False, "volume": 1.0, "known": False}
    try:
        speakers = AudioUtilities.GetSpeakers()
        iface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol = cast(iface, POINTER(IAudioEndpointVolume))
        return {
            "available": True,
            "muted": bool(vol.GetMute()),
            "volume": float(vol.GetMasterVolumeLevelScalar()),
            "known": True,
        }
    except Exception as exc:  # no output device, or the query failed
        log.info("no_audio_output", error=str(exc))
        return {"available": False, "muted": False, "volume": 0.0, "known": True}


def can_be_heard() -> bool:
    s = output_state()
    return _audible(s["available"], s["muted"], s["volume"])


def describe() -> str:
    s = output_state()
    if not s.get("known"):
        return "audio state unknown"
    if not s["available"]:
        return "no audio output device"
    if s["muted"]:
        return "speaker muted"
    if s["volume"] <= 0:
        return "volume at zero"
    return "audio OK"
