"""User-rule tests: matching, effect precedence (speak beats mute), event shaping, and
the engine muting/escalating events. Pure logic + fakes — no DB."""

from __future__ import annotations

from purple.config import settings
from purple.triggers import engine as engine_mod
from purple.triggers.engine import TriggerEngine
from purple.triggers.priority import IMPORTANT, NORMAL, Event
from purple.triggers.rules import MUTE, NOTIFY, SPEAK, Rule, apply_rules, rule_matches, shape_event
from purple.triggers.watchers import Watcher


def test_rule_matches_source_and_keywords():
    ev = Event("email", "Invoice overdue", "pay now", priority=NORMAL, sender="billing@x.com")
    assert rule_matches(Rule("any"), ev) is True  # no filters = matches
    assert rule_matches(Rule("src", source="email"), ev) is True
    assert rule_matches(Rule("src", source="call"), ev) is False
    assert rule_matches(Rule("kw", keywords=["invoice"]), ev) is True
    assert rule_matches(Rule("kw", keywords=["refund"]), ev) is False
    assert rule_matches(Rule("off", enabled=False), ev) is False


def test_rule_matches_min_priority():
    low = Event("system", "fyi", priority=NORMAL)
    assert rule_matches(Rule("hi", min_priority=IMPORTANT), low) is False
    hi = Event("system", "alert", priority=IMPORTANT)
    assert rule_matches(Rule("hi", min_priority=IMPORTANT), hi) is True


def test_speak_beats_mute():
    ev = Event("email", "from boss", priority=NORMAL, sender="boss@x.com")
    rules = [
        Rule("mute work", keywords=["boss"], effect=MUTE),
        Rule("hear boss", keywords=["boss"], effect=SPEAK),
    ]
    out = apply_rules(rules, ev)
    assert out.force_speak is True and out.mute is False
    assert set(out.matched) == {"mute work", "hear boss"}


def test_shape_event_mute_drops():
    ev = Event("message", "Sale! 50% off", priority=NORMAL)
    assert shape_event([Rule("no ads", keywords=["sale"], effect=MUTE)], ev) is None


def test_shape_event_speak_escalates():
    ev = Event("email", "lunch?", priority=NORMAL)
    shaped = shape_event([Rule("always hear", effect=SPEAK)], ev)
    assert shaped is not None and shaped.priority == IMPORTANT


def test_shape_event_notify_passthrough():
    ev = Event("email", "hi", priority=NORMAL)
    shaped = shape_event([Rule("plain", effect=NOTIFY)], ev)
    assert shaped is ev and shaped.priority == NORMAL


class _OneEvent(Watcher):
    name = "fake"

    def __init__(self, event: Event) -> None:
        self._event = event

    async def check(self) -> list[Event]:
        return [self._event]


class _CountNotifier:
    def __init__(self) -> None:
        self.seen: list[Event] = []

    async def notify(self, e: Event) -> dict:
        self.seen.append(e)
        return {"channels": []}


async def test_engine_mutes_event(monkeypatch):
    monkeypatch.setattr(engine_mod, "_rules_dirty", False)  # use injected rules, skip DB
    n = _CountNotifier()
    eng = TriggerEngine(
        notifier=n,
        watchers=[_OneEvent(Event("message", "Flash sale", priority=NORMAL))],
        rules=[Rule("no ads", keywords=["sale"], effect=MUTE)],
    )
    assert await eng.tick() == 0 and n.seen == []  # muted


async def test_engine_escalates_event(monkeypatch):
    monkeypatch.setattr(engine_mod, "_rules_dirty", False)
    n = _CountNotifier()
    eng = TriggerEngine(
        notifier=n,
        watchers=[_OneEvent(Event("email", "newsletter", priority=NORMAL))],
        rules=[Rule("hear all email", source="email", effect=SPEAK)],
    )
    assert await eng.tick() == 1
    assert n.seen[0].priority == IMPORTANT  # escalated so it breaks through


def test_apply_rules_collects_actions():
    from purple.triggers.rules import apply_rules

    ev = Event("download", "report.pdf finished")
    rules = [Rule("open it", source="download", action="open_path", action_args={"path": "x"})]
    out = apply_rules(rules, ev)
    assert out.actions == [("open_path", {"path": "x"})]


def _patch_registry(monkeypatch):
    import purple.tools as tools_pkg

    calls: list = []

    async def fake_execute(name, args, approver):
        calls.append((name, args))
        return {"ok": True, "result": "done"}

    monkeypatch.setattr(tools_pkg.registry, "execute", fake_execute)
    return calls


async def test_engine_action_act_runs_tool(monkeypatch):
    monkeypatch.setattr(engine_mod, "_rules_dirty", False)
    monkeypatch.setattr(settings, "autonomy", "act")
    calls = _patch_registry(monkeypatch)
    rule = Rule("auto-note", action="add_note", action_args={"text": "hi"})
    eng = TriggerEngine(
        notifier=_CountNotifier(),
        watchers=[_OneEvent(Event("download", "x"))],
        rules=[rule],
    )
    await eng.tick()
    assert calls and calls[0] == ("add_note", {"text": "hi"})


async def test_engine_action_notify_mode_does_not_run(monkeypatch):
    monkeypatch.setattr(engine_mod, "_rules_dirty", False)
    monkeypatch.setattr(settings, "autonomy", "notify")
    calls = _patch_registry(monkeypatch)
    rule = Rule("auto-note", action="add_note", action_args={"text": "hi"})
    n = _CountNotifier()
    eng = TriggerEngine(notifier=n, watchers=[_OneEvent(Event("download", "x"))], rules=[rule])
    await eng.tick()
    assert calls == []  # notify mode never executes
    assert any(e.source == "automation" for e in n.seen)  # but it tells the user
