"""User-defined rules — the layer that lets *you* shape what Purple surfaces.

Built-in watchers decide what's worth noticing; rules let you override that per your
taste without code: mute a noisy source, or force a gentle spoken nudge for things you
never want to miss. Rules are pure data (created from the UI or by voice) and matching
is pure logic — no GPU, no I/O — so it stays cheap and runs even while you game.

Effect precedence: "speak" beats "mute" (escalation wins over silencing), so a
"speak anything from my boss" rule still talks even if a "mute work email" rule matches.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from purple.triggers.priority import _ORDER, IMPORTANT, NORMAL, Event

SPEAK = "speak"  # force a one-time spoken breakthrough (escalate to IMPORTANT)
MUTE = "mute"  # suppress entirely (no voice, no toast, no feed)
NOTIFY = "notify"  # default surfacing (feed + toast + voice-by-policy)
EFFECTS = (SPEAK, MUTE, NOTIFY)


@dataclass
class Rule:
    name: str
    keywords: list[str] = field(default_factory=list)  # match event title+detail; empty = any
    source: str = ""  # watcher source filter (email/call/system/...); empty = any
    min_priority: str = NORMAL  # only consider events at/above this priority
    effect: str = NOTIFY  # speak | mute | notify (how to surface it)
    enabled: bool = True
    action: str = ""  # optional tool to run when matched ("" = none) — gated by autonomy
    action_args: dict = field(default_factory=dict)  # fixed args for that tool


@dataclass
class Outcome:
    mute: bool = False
    force_speak: bool = False
    matched: list[str] = field(default_factory=list)  # names of rules that fired
    actions: list[tuple[str, dict]] = field(default_factory=list)  # (tool, args) to run


def rule_matches(rule: Rule, event: Event) -> bool:
    if not rule.enabled:
        return False
    if rule.source and rule.source != event.source:
        return False
    if _ORDER.get(event.priority, 1) < _ORDER.get(rule.min_priority, 1):
        return False
    if rule.keywords:
        haystack = f"{event.title} {event.detail} {event.sender}".lower()
        if not any(kw.lower().strip() in haystack for kw in rule.keywords if kw.strip()):
            return False
    return True


def apply_rules(rules: list[Rule], event: Event) -> Outcome:
    """Fold all matching rules into one decision. speak wins over mute."""
    outcome = Outcome()
    for rule in rules:
        if not rule_matches(rule, event):
            continue
        outcome.matched.append(rule.name)
        if rule.effect == SPEAK:
            outcome.force_speak = True
        elif rule.effect == MUTE:
            outcome.mute = True
        if rule.action:
            outcome.actions.append((rule.action, dict(rule.action_args)))
    if outcome.force_speak:  # escalation beats silencing
        outcome.mute = False
    return outcome


def shape_event(rules: list[Rule], event: Event) -> Event | None:
    """Apply rules to an event. Returns the (possibly escalated) event, or None to drop it."""
    outcome = apply_rules(rules, event)
    if outcome.mute:
        return None
    if outcome.force_speak and _ORDER.get(event.priority, 1) < _ORDER[IMPORTANT]:
        event.priority = IMPORTANT  # so should_breakthrough() speaks it once
    return event
