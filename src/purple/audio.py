"""Audio output state — so Purple knows whether her voice can actually be heard.

The detail is Windows-specific (pycaw / Core Audio). On other platforms, or if pycaw
isn't installed, we can't tell — so we assume audio is fine (don't suppress her voice
over a false negative). Never raises.
"""

from __future__ import annotations

import contextlib

from purple.utils.logging import get_logger

log = get_logger("audio")

_warned_query = False  # so a recurring pycaw failure is logged once, not every poll


def _audible(available: bool, muted: bool, volume: float) -> bool:
    """Pure decision: can a spoken line actually be heard right now?"""
    return available and not muted and volume > 0.0


def output_state() -> dict:
    """Best-effort default-output state: {available, muted, volume, known}. Never raises.

    known=False means we couldn't query (no pycaw / not Windows) — callers should assume
    audio is fine rather than silence her.
    """
    unknown = {"available": True, "muted": False, "volume": 1.0, "known": False}
    try:
        from ctypes import POINTER, cast

        import comtypes
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except Exception:
        return unknown

    # pycaw talks to Windows Core Audio over COM. On a background thread (e.g. the
    # self-watcher) COM may not be initialised, which makes the query fail and *look*
    # like there's no output device. Initialise COM here so we read the real default
    # endpoint (Bluetooth included); uninitialise after.
    initialised = False
    try:
        comtypes.CoInitialize()
        initialised = True
    except Exception:
        pass
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
    except Exception as exc:
        # Couldn't query (no default endpoint at this instant, a transient COM error, or a
        # pycaw version whose device lacks .Activate). Treat as UNKNOWN and assume audio is
        # fine — never silence her, and never falsely warn "no output device". Log once only.
        global _warned_query
        if not _warned_query:
            log.info("audio_query_failed", error=str(exc))
            _warned_query = True
        return unknown
    finally:
        if initialised:
            with contextlib.suppress(Exception):
                comtypes.CoUninitialize()


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


# --- Playback that follows the CURRENT default output device --------------------------
# sounddevice/PortAudio caches the device list + default at init, so it won't notice a
# mid-session switch (Bluetooth -> headphones) on its own. We read the OS default endpoint
# id via pycaw (which is *not* cached), and only re-initialise PortAudio when it actually
# changes — so normal playback has zero overhead and switches route to the new device.
_last_output_id: str | None = None


def default_output_id() -> str | None:
    """The Windows default render-endpoint id, or None if it can't be read. Reflects the
    current default device independently of PortAudio's cache."""
    try:
        import comtypes
        from pycaw.pycaw import AudioUtilities
    except Exception:
        return None
    initialised = False
    try:
        comtypes.CoInitialize()
        initialised = True
    except Exception:
        pass
    try:
        return str(AudioUtilities.GetSpeakers().GetId())
    except Exception:
        return None
    finally:
        if initialised:
            with contextlib.suppress(Exception):
                comtypes.CoUninitialize()


def _should_refresh(current_id: str | None, last_id: str | None) -> bool:
    """Pure: re-init PortAudio only when the OS default output actually changed."""
    return current_id is not None and current_id != last_id


def _refresh_portaudio() -> None:
    """Re-enumerate audio devices so sounddevice targets the current default. Best-effort."""
    import sounddevice as sd

    with contextlib.suppress(Exception):
        sd._terminate()
    with contextlib.suppress(Exception):
        sd._initialize()


def play_wav(wav_bytes: bytes) -> bool:
    """Play a WAV blob on the CURRENT default output device. Refreshes the device list when
    the default changed (e.g. you switched Bluetooth -> headphones) and retries once if the
    previous device vanished mid-session. Best-effort; never raises. True if it played."""
    global _last_output_id
    if not wav_bytes:
        return False
    import io
    import wave

    import numpy as np
    import sounddevice as sd

    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr = wf.getframerate()
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)

    cur = default_output_id()
    if _should_refresh(cur, _last_output_id):
        _refresh_portaudio()  # default device changed -> pick it up
        _last_output_id = cur

    for attempt in (1, 2):
        try:
            sd.play(data, sr)
            sd.wait()
            return True
        except Exception as exc:
            log.info("playback_failed", attempt=attempt, error=str(exc))
            if attempt == 1:
                _refresh_portaudio()  # old device likely vanished — refresh and retry once
                _last_output_id = default_output_id()
            else:
                return False
    return False
