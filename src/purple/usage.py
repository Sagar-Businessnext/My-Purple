"""Persistent tool-usage log — the substrate for Purple's self-learning.

Prometheus metrics reset on every restart, so they can't tell Purple "you've leaned on raw
commands a lot lately". This keeps a small, durable, append-only record of which tools ran
and when (capped, in data_dir) so the suggestions engine can spot patterns across sessions.
No arguments or results are stored — only the tool name and a timestamp.
"""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from purple.config import settings

_UTC = UTC
_CAP = 2000  # keep at most this many recent events


def _path() -> Path:
    return settings.data_dir / "tool_usage.json"


def _load_raw() -> list[dict[str, Any]]:
    path = _path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def record(tool: str, now: datetime | None = None) -> None:
    """Append one tool-use event. Best-effort; never raises into the caller."""
    with contextlib.suppress(Exception):
        events = _load_raw()
        events.append({"tool": tool, "at": (now or datetime.now(_UTC)).isoformat()})
        events = events[-_CAP:]
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        _path().write_text(json.dumps(events), encoding="utf-8")


def _parse(ts: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(ts)
        return dt if dt.tzinfo else dt.replace(tzinfo=_UTC)
    except Exception:
        return None


def summarize_counts(
    events: list[dict[str, Any]], since: datetime, now: datetime
) -> dict[str, int]:
    """Pure: count tool uses in [since, now]. Tolerant of malformed rows."""
    counts: dict[str, int] = {}
    for ev in events:
        if not isinstance(ev, dict):
            continue
        tool = ev.get("tool")
        at = _parse(ev.get("at", "")) if isinstance(ev.get("at"), str) else None
        if not tool or at is None:
            continue
        if since <= at <= now:
            counts[tool] = counts.get(tool, 0) + 1
    return counts


def recent_counts(days: int = 14) -> dict[str, int]:
    """Tool-use counts over the last `days`, read from the durable log."""
    now = datetime.now(_UTC)
    since = now.fromordinal(now.toordinal() - max(1, days)).replace(tzinfo=_UTC)
    return summarize_counts(_load_raw(), since, now)
