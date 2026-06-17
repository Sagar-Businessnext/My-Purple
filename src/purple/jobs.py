"""Persistent last-run timestamps for scheduled jobs, so a job missed while the PC was
off runs on the next boot instead of silently waiting for its next slot.

State is a small JSON file in data_dir (no DB needed — this must work before the DB is
up). is_overdue() is pure and unit-tested; the scheduler records each run and, on start,
runs anything overdue.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("jobs")


def _path() -> Path:
    return settings.data_dir / "job_runs.json"


def load_runs() -> dict[str, str]:
    p = _path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


def record_run(job_id: str, now: datetime | None = None) -> None:
    runs = load_runs()
    runs[job_id] = (now or datetime.now(UTC)).isoformat()
    p = _path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(runs), encoding="utf-8")
    except OSError as exc:
        log.warning("job_run_write_failed", error=str(exc))


def last_run(job_id: str) -> datetime | None:
    raw = load_runs().get(job_id)
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def is_overdue(last: datetime | None, period_seconds: float, now: datetime) -> bool:
    """Has at least one period elapsed since the last run (or it never ran)? Pure."""
    if last is None:
        return True
    return (now - last).total_seconds() >= period_seconds
