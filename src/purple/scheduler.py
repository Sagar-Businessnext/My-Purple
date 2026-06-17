"""Proactivity: scheduled jobs — daily briefing, weekly memory hygiene, watched folder.

APScheduler is in-memory, so a job whose time passed while the PC was off would normally
just wait for its next slot. We record each run (purple.jobs) and, on startup, run anything
overdue — so a missed briefing/hygiene catches up on the next boot.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from purple import jobs
from purple.briefing import build_briefing, deliver
from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("scheduler")

_DAY = 24 * 3600
_WEEK = 7 * _DAY

_scheduler: AsyncIOScheduler | None = None
_catchup_task: Any | None = None  # keep a ref so the boot catch-up task isn't GC'd


async def _briefing_job() -> None:
    text = await build_briefing()
    await deliver(text)
    jobs.record_run("daily_briefing")
    log.info("daily_briefing_delivered")


async def _memory_hygiene_job() -> None:
    from purple.runtime import get_memory

    try:
        mem = get_memory()
        merged = await mem.consolidate()
        decayed = await mem.decay_facts()
        log.info("memory_hygiene", merged=merged, decayed=decayed)
    except Exception as exc:
        log.warning("memory_hygiene_failed", error=str(exc))
    jobs.record_run("memory_hygiene")


async def _knowledge_job() -> None:
    from purple.runtime import get_memory

    try:
        res = await get_memory().ingest_folder(settings.knowledge_dir)
        if res.get("ingested"):
            log.info("knowledge_ingest", **{k: res[k] for k in ("ingested", "chunks")})
    except Exception as exc:
        log.warning("knowledge_ingest_failed", error=str(exc))


async def _catch_up() -> None:
    """On boot, run any cron job whose slot passed while the PC was off."""
    now = datetime.now(UTC)
    if jobs.is_overdue(jobs.last_run("daily_briefing"), _DAY, now):
        log.info("catch_up", job="daily_briefing")
        await _briefing_job()
    if settings.consolidate_weekly and jobs.is_overdue(jobs.last_run("memory_hygiene"), _WEEK, now):
        log.info("catch_up", job="memory_hygiene")
        await _memory_hygiene_job()


def start_scheduler(agent: Any | None = None) -> AsyncIOScheduler:
    global _scheduler, _catchup_task
    if _scheduler is not None:
        return _scheduler

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _briefing_job,
        CronTrigger(hour=settings.briefing_hour, minute=settings.briefing_minute),
        id="daily_briefing",
        replace_existing=True,
    )
    if settings.consolidate_weekly:
        _scheduler.add_job(
            _memory_hygiene_job,
            CronTrigger(day_of_week="sun", hour=3, minute=0),
            id="memory_hygiene",
            replace_existing=True,
        )
    if settings.knowledge_dir:
        _scheduler.add_job(
            _knowledge_job,
            IntervalTrigger(minutes=30),
            id="knowledge_ingest",
            replace_existing=True,
            next_run_time=None,
        )
    _scheduler.start()
    _catchup_task = asyncio.create_task(_catch_up())  # run missed jobs without blocking startup
    log.info(
        "scheduler_started",
        briefing_at=f"{settings.briefing_hour:02d}:{settings.briefing_minute:02d}",
    )
    return _scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
