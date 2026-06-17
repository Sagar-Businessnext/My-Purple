"""TTS tests: WAV encoding of float samples and the kokoro/xtts engine dispatch.
The heavy models are never loaded — the synth helpers are faked."""

from __future__ import annotations

import io
import wave

from purple.config import settings
from purple.speech.local_provider import LocalSpeech, _to_wav


def test_to_wav_roundtrip():
    data = _to_wav([0.0, 0.5, -0.5, 1.0, -1.0], 24000)
    with wave.open(io.BytesIO(data)) as wav:
        assert wav.getframerate() == 24000
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2  # 16-bit
        assert wav.getnframes() == 5


def test_to_wav_clips_out_of_range():
    data = _to_wav([5.0, -5.0], 16000)
    with wave.open(io.BytesIO(data)) as wav:
        frames = wav.readframes(2)
    # +5.0 clamps to +32767, -5.0 clamps to -32767 (little-endian int16)
    assert frames == b"\xff\x7f\x01\x80"


def test_tts_engine_dispatch(monkeypatch):
    sp = LocalSpeech()
    monkeypatch.setattr(sp, "_kokoro_sync", lambda t: b"KOKORO")
    monkeypatch.setattr(sp, "_xtts_sync", lambda t: b"XTTS")
    monkeypatch.setattr(settings, "tts_engine", "kokoro")
    assert sp._synthesize_sync("hi") == b"KOKORO"
    monkeypatch.setattr(settings, "tts_engine", "xtts")
    assert sp._synthesize_sync("hi") == b"XTTS"
