"""Tests for the voice stack: VAD, wake-word threshold logic, the event bus, and the
voice loop's command processing — all with fakes, no audio hardware."""

from __future__ import annotations

import numpy as np

from purple.events import EventBus
from purple.voice.loop import VoiceLoop
from purple.voice.vad import is_speech
from purple.voice.wake import WakeListener


def test_vad_distinguishes_loud_from_quiet():
    quiet = np.zeros(1280, dtype=np.int16)
    loud = (np.ones(1280) * 5000).astype(np.int16)
    assert is_speech(quiet, 500.0) is False
    assert is_speech(loud, 500.0) is True


class _FakeWakeModel:
    def __init__(self, score: float) -> None:
        self._score = score

    def predict(self, frame):
        return {"hey_jarvis": self._score}

    def reset(self):
        pass


def test_wake_threshold_logic():
    frame = np.zeros(1280, dtype=np.int16)
    hot = WakeListener(model=_FakeWakeModel(0.9), threshold=0.5)
    cold = WakeListener(model=_FakeWakeModel(0.1), threshold=0.5)
    assert hot.is_wake(frame) is True
    assert cold.is_wake(frame) is False


async def test_event_bus_broadcasts_and_drops_dead_clients():
    bus = EventBus()

    class FakeWS:
        def __init__(self, fail: bool = False) -> None:
            self.fail = fail
            self.events: list[dict] = []

        async def send_json(self, data: dict) -> None:
            if self.fail:
                raise RuntimeError("connection dead")
            self.events.append(data)

    good, bad = FakeWS(), FakeWS(fail=True)
    bus.register(good)
    bus.register(bad)
    await bus.broadcast({"type": "voice", "state": "woke"})
    assert good.events == [{"type": "voice", "state": "woke"}]
    # the failing client should have been removed, so this still succeeds:
    await bus.broadcast({"type": "voice", "state": "listening"})
    assert len(good.events) == 2


async def test_voice_loop_process_command_flow():
    events: list[dict] = []

    class FakeSpeech:
        async def transcribe(self, path):
            return "open notepad"

        async def synthesize(self, text):
            return b""

    class FakeAgent:
        async def respond(self, text, approver=None):
            return "Opening Notepad."

    async def emit(ev):
        events.append(ev)

    vl = VoiceLoop(FakeAgent(), FakeSpeech(), emit=emit)
    vl._write_wav = lambda audio: "/tmp/fake.wav"  # bypass real WAV write
    vl._play = lambda audio: None  # no audio device in tests

    transcript, reply = await vl.process_command(np.zeros(16, dtype=np.int16))
    assert transcript == "open notepad"
    assert reply == "Opening Notepad."
    states = [e.get("state") for e in events]
    assert "heard" in states and "reply" in states
