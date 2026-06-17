"""Event priority + Tier-1 importance/spam classification + breakthrough policy.

Tier-1 only: rules + cheap CPU signals (VIP list, keywords). The heavy GPU LLM is never
used here, so priority decisions keep working even while the GPU is busy gaming — which
is exactly when the breakthrough (a gentle spoken nudge) matters most.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from purple.config import settings

LOW = "low"
NORMAL = "normal"
IMPORTANT = "important"
URGENT = "urgent"
_ORDER = {LOW: 0, NORMAL: 1, IMPORTANT: 2, URGENT: 3}

_IMPORTANT_WORDS = (
    "urgent",
    "asap",
    "immediately",
    "important",
    "deadline",
    "emergency",
    "action required",
    "final notice",
    "payment",
    "overdue",
)


@dataclass
class Event:
    source: str  # which watcher produced it (email, calendar, system, call, ...)
    title: str
    detail: str = ""
    priority: str = NORMAL
    sender: str = ""
    data: dict[str, Any] = field(default_factory=dict)


def is_vip(sender: str) -> bool:
    s = (sender or "").lower()
    return any(v.lower() in s for v in settings.vip_senders)


def classify(title: str, body: str = "", sender: str = "") -> str:
    """Tier-1 importance: VIP sender or urgent keywords -> important, else normal."""
    if sender and is_vip(sender):
        return IMPORTANT
    text = f"{title} {body}".lower()
    if any(word in text for word in _IMPORTANT_WORDS):
        return IMPORTANT
    return NORMAL


def is_spam_caller(number: str, contacts: list[str]) -> bool:
    """A caller is treated as non-spam only if the number is in your contacts."""
    return number not in (contacts or [])


def in_quiet_hours(now: datetime | None = None) -> bool:
    now = now or datetime.now()
    start, end = settings.quiet_hours_start, settings.quiet_hours_end
    if start == end:
        return False
    if start < end:
        return start <= now.hour < end
    return now.hour >= start or now.hour < end  # window wraps midnight


def should_breakthrough(event: Event) -> bool:
    """Important/urgent events break through Focus mode and quiet hours (speak once)."""
    return _ORDER.get(event.priority, 1) >= _ORDER[IMPORTANT]
