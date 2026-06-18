"""Self-awareness tests: the pure audibility decision, channel planning (muted → toast
fallback), self-state note injection, and the SelfWatcher edge-trigger. All fakes."""

from __future__ import annotations

from purple import audio, selfstate
from purple.triggers import notify as notify_mod
from purple.triggers.notify import Notifier, plan_channels
from purple.triggers.priority import IMPORTANT, NORMAL, Event
from purple.triggers.watchers import SelfWatcher


def test_audible_truth_table():
    assert audio._audible(True, False, 1.0) is True
    assert audio._audible(True, True, 1.0) is False  # muted
    assert audio._audible(True, False, 0.0) is False  # zero volume
    assert audio._audible(False, False, 1.0) is False  # no device


def test_should_refresh_portaudio_on_device_change():
    # Re-init PortAudio only when the default output endpoint actually changed.
    assert audio._should_refresh("dev-A", "dev-A") is False  # same device
    assert audio._should_refresh("dev-B", "dev-A") is True  # switched (BT -> headphones)
    assert audio._should_refresh("dev-A", None) is True  # first play
    assert audio._should_refresh(None, "dev-A") is False  # unknown -> don't churn


def test_plan_channels_normal_speaks_and_toasts():
    speak, toast = plan_channels(
        breakthrough=False, quiet=False, yielding=False, audible=True, debounced=False
    )
    assert speak is True and toast is True


def test_plan_channels_muted_falls_back_to_toast():
    # wanted voice, but speaker can't be heard -> no voice, but toast carries it
    speak, toast = plan_channels(
        breakthrough=False, quiet=False, yielding=False, audible=False, debounced=False
    )
    assert speak is False and toast is True


def test_plan_channels_muted_breakthrough_in_quiet_hours_still_toasts():
    # important + quiet hours + muted: voice can't land, so toast must override the quiet
    speak, toast = plan_channels(
        breakthrough=True, quiet=True, yielding=True, audible=False, debounced=False
    )
    assert speak is False and toast is True


def test_plan_channels_gaming_audible_no_voice_no_toast_when_normal():
    # normal priority, gaming (yielding), not quiet, audible: no voice; toast still ok
    speak, toast = plan_channels(
        breakthrough=False, quiet=False, yielding=True, audible=True, debounced=False
    )
    assert speak is False and toast is True


def test_selfstate_note(monkeypatch):
    monkeypatch.setattr(audio, "can_be_heard", lambda: False)
    monkeypatch.setattr(audio, "describe", lambda: "speaker muted")
    note = selfstate.context_note()
    assert note and "won't reach you" in note
    monkeypatch.setattr(audio, "can_be_heard", lambda: True)
    assert selfstate.context_note() is None


async def test_notify_muted_falls_back_to_toast(monkeypatch):
    spoke, toasted, fed = [], [], []

    async def fake_speak(text):
        spoke.append(text)
        return True

    async def fake_toast(a, b):
        toasted.append(a)

    class FakeBus:
        async def broadcast(self, e):
            fed.append(e)

    monkeypatch.setattr(notify_mod, "speak", fake_speak)
    monkeypatch.setattr(notify_mod, "toast", fake_toast)
    monkeypatch.setattr(notify_mod, "bus", FakeBus())
    monkeypatch.setattr(notify_mod.audio, "can_be_heard", lambda: False)  # muted
    monkeypatch.setattr(notify_mod, "in_quiet_hours", lambda: False)
    from purple import focus

    monkeypatch.setattr(focus, "should_yield_gpu", lambda: False)

    r = await Notifier().notify(Event("self", "Heads up — you won't hear me", priority=IMPORTANT))
    assert "voice" not in r["channels"] and not spoke  # couldn't be heard
    assert "toast" in r["channels"] and toasted  # ...so it fell back to a toast
    assert r["audible"] is False


async def test_self_watcher_edge_triggers_once(monkeypatch):
    w = SelfWatcher()
    monkeypatch.setattr(audio, "can_be_heard", lambda: False)
    monkeypatch.setattr(w, "_llm_down", _afalse)
    monkeypatch.setattr(w, "_db_down", _afalse)

    events = await w.check()
    assert len(events) == 1 and events[0].source == "self"
    assert events[0].priority == IMPORTANT
    assert await w.check() == []  # still down: no repeat (edge-triggered)

    monkeypatch.setattr(audio, "can_be_heard", lambda: True)  # recovered
    assert await w.check() == []
    monkeypatch.setattr(audio, "can_be_heard", lambda: False)  # down again
    assert len(await w.check()) == 1  # re-arms and warns again


async def _afalse() -> bool:
    return False


def test_priority_constants_present():
    assert NORMAL and IMPORTANT  # sanity that imports resolved
