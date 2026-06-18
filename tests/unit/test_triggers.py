"""M2 slice-1 tests: priority/classification, breakthrough/quiet-hours, the notifier's
channel routing (voice suppressed while gaming except breakthrough), and engine dispatch.
All with fakes — no GPU, no audio, no network."""

from __future__ import annotations

from datetime import datetime

from purple import focus
from purple.config import settings
from purple.triggers import notify as notify_mod
from purple.triggers.engine import TriggerEngine
from purple.triggers.notify import Notifier
from purple.triggers.priority import (
    IMPORTANT,
    NORMAL,
    Event,
    classify,
    in_quiet_hours,
    is_spam_caller,
    should_breakthrough,
)
from purple.triggers.watchers import Watcher


def test_classify(monkeypatch):
    monkeypatch.setattr(settings, "vip_senders", ["boss@work.com"])
    assert classify("hi", "", "boss@work.com") == IMPORTANT  # VIP
    assert classify("URGENT: server down", "", "x@y.com") == IMPORTANT  # keyword
    assert classify("lunch?", "", "friend@y.com") == NORMAL


def test_spam_and_breakthrough():
    assert is_spam_caller("+100", ["+200"]) is True
    assert is_spam_caller("+200", ["+200"]) is False
    assert should_breakthrough(Event("call", "x", priority=IMPORTANT)) is True
    assert should_breakthrough(Event("email", "x", priority=NORMAL)) is False


def test_quiet_hours(monkeypatch):
    monkeypatch.setattr(settings, "quiet_hours_start", 23)
    monkeypatch.setattr(settings, "quiet_hours_end", 7)
    assert in_quiet_hours(datetime(2026, 1, 1, 2, 0)) is True
    assert in_quiet_hours(datetime(2026, 1, 1, 12, 0)) is False


async def _patch_channels(monkeypatch):
    spoke: list = []
    fed: list = []

    async def fake_speak(text):
        spoke.append(text)

    async def fake_toast(a, b):
        pass

    class FakeBus:
        async def broadcast(self, e):
            fed.append(e)

    monkeypatch.setattr(notify_mod, "speak", fake_speak)
    monkeypatch.setattr(notify_mod, "toast", fake_toast)
    monkeypatch.setattr(notify_mod, "bus", FakeBus())
    return spoke, fed


async def test_notify_speaks_when_free(monkeypatch):
    spoke, _fed = await _patch_channels(monkeypatch)
    monkeypatch.setattr(notify_mod, "in_quiet_hours", lambda: False)
    monkeypatch.setattr(focus, "should_yield_gpu", lambda: False)
    r = await Notifier().notify(Event("email", "Hello", priority=NORMAL))
    assert "voice" in r["channels"] and "toast" in r["channels"] and spoke and fed


async def test_notify_silent_while_gaming(monkeypatch):
    spoke, _fed = await _patch_channels(monkeypatch)
    monkeypatch.setattr(notify_mod, "in_quiet_hours", lambda: False)
    monkeypatch.setattr(focus, "should_yield_gpu", lambda: True)  # gaming
    r = await Notifier().notify(Event("email", "Hello", priority=NORMAL))
    assert "voice" not in r["channels"] and not spoke  # won't talk over the game
    assert "toast" in r["channels"]


async def test_notify_breakthrough_and_debounce(monkeypatch):
    spoke, _fed = await _patch_channels(monkeypatch)
    monkeypatch.setattr(notify_mod, "in_quiet_hours", lambda: True)
    monkeypatch.setattr(focus, "should_yield_gpu", lambda: True)  # gaming + quiet
    n = Notifier()
    r = await n.notify(Event("call", "Call from Mom", priority=IMPORTANT))
    assert "voice" in r["channels"] and spoke  # important breaks through
    r2 = await n.notify(Event("call", "Call from Mom", priority=IMPORTANT))
    assert "voice" not in r2["channels"]  # debounced, won't nag


async def test_engine_tick_dispatches():
    class W(Watcher):
        name = "w"

        async def check(self):
            return [Event("w", "a"), Event("w", "b")]

    seen: list = []

    class N:
        async def notify(self, e):
            seen.append(e)

    eng = TriggerEngine(notifier=N(), watchers=[W()])
    assert await eng.tick() == 2 and len(seen) == 2
