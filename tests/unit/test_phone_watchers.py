"""Phone watcher tests: ADB call-state/contacts parsing, spam-aware CallWatcher routing,
and MessageWatcher priming/classification. All fakes — no device, no adb, no network."""

from __future__ import annotations

import purple.phone.adb as adb
from purple.triggers.priority import IMPORTANT, NORMAL
from purple.triggers.watchers import CallWatcher, MessageWatcher

RING_KNOWN = "mCallState=1\nmCallIncomingNumber=+15551112222\n"
RING_UNKNOWN = "mCallState=1\nmCallIncomingNumber=+15559990000\n"
IDLE = "mCallState=0\nmCallIncomingNumber=\n"
CONTACTS = "Row: 0 data1=+1 555-111-2222\nRow: 1 data1=5553334444\n"


def test_normalize_number():
    assert adb.normalize_number("+1 555-111-2222") == "5551112222"
    assert adb.normalize_number("5551112222") == "5551112222"
    assert adb.normalize_number("") == ""


def test_parse_call_state():
    assert adb.parse_call_state(RING_KNOWN) == (1, "+15551112222")
    assert adb.parse_call_state(IDLE) == (0, "")
    # multi-SIM: a ringing line on any subscription wins
    assert adb.parse_call_state("mCallState=0\nmCallState=1\nmCallIncomingNumber=+15550001111\n")[0] == 1


def test_parse_contacts():
    nums = adb.parse_contacts(CONTACTS)
    assert "5551112222" in nums and "5553334444" in nums


def _runner(call_out: str, contacts_out: str = CONTACTS):
    async def fake_run_adb(args, timeout=30.0):
        if "telephony.registry" in args:
            return 0, call_out
        if "content" in args:
            return 0, contacts_out
        return 0, ""

    return fake_run_adb


async def test_call_from_known_contact_breaks_through(monkeypatch):
    w = CallWatcher()
    monkeypatch.setattr(adb, "run_adb", _runner(RING_KNOWN))
    events = await w.check()
    assert len(events) == 1
    assert events[0].priority == IMPORTANT  # gentle spoken nudge, even mid-game
    assert await w.check() == []  # same ring de-duped, won't nag


async def test_call_from_unknown_is_quiet(monkeypatch):
    w = CallWatcher()
    monkeypatch.setattr(adb, "run_adb", _runner(RING_UNKNOWN))
    events = await w.check()
    assert len(events) == 1
    assert events[0].priority == NORMAL  # likely spam: no breakthrough


async def test_call_idle_rearms(monkeypatch):
    w = CallWatcher()
    monkeypatch.setattr(adb, "run_adb", _runner(RING_KNOWN))
    assert len(await w.check()) == 1
    monkeypatch.setattr(adb, "run_adb", _runner(IDLE))
    assert await w.check() == []  # hung up: nothing, and re-arms
    monkeypatch.setattr(adb, "run_adb", _runner(RING_KNOWN))
    assert len(await w.check()) == 1  # next call notifies again


async def test_call_watcher_no_phone(monkeypatch):
    w = CallWatcher()

    async def fake(args, timeout=30.0):
        return 127, "adb not found"

    monkeypatch.setattr(adb, "run_adb", fake)
    assert await w.check() == []


async def test_message_watcher_primes_then_classifies(monkeypatch):
    w = MessageWatcher()
    state = {"out": "android.title=String (News)\nandroid.text=String (daily digest)\n"}

    async def fake(args, timeout=30.0):
        return 0, state["out"]

    monkeypatch.setattr(adb, "run_adb", fake)
    assert await w.check() == []  # first run baselines existing notifications
    state["out"] = "android.title=String (Boss)\nandroid.text=String (urgent: call me)\n"
    events = await w.check()
    assert len(events) == 1
    assert events[0].priority == IMPORTANT  # "urgent" keyword
