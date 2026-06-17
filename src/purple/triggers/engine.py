"""Trigger engine — runs the watchers on a schedule and dispatches events to the notifier.

CPU-only watching (no GPU), so it runs happily alongside games. Built-in watchers ship
now; user-defined rules + natural-language triggers + the Automations UI come next slice.
"""

from __future__ import annotations

from typing import Any

from purple.config import settings
from purple.triggers.notify import Notifier
from purple.triggers.priority import _ORDER, IMPORTANT, NORMAL, Event
from purple.triggers.rules import Rule, apply_rules
from purple.triggers.watchers import (
    CalendarWatcher,
    CallWatcher,
    DownloadsWatcher,
    EmailWatcher,
    MessageWatcher,
    SelfWatcher,
    SystemHealthWatcher,
    SystemWatcher,
    Watcher,
)
from purple.utils.logging import get_logger

log = get_logger("triggers")

# Set by the automation tools / API after a rule changes; the next tick reloads rules
# from the DB. Avoids a DB hit every tick while keeping edits near-instant.
_rules_dirty = True


def request_rules_reload() -> None:
    """Ask the engine to refresh its user rules on the next tick."""
    global _rules_dirty
    _rules_dirty = True


def _default_watchers() -> list[Watcher]:
    watchers: list[Watcher] = [
        SystemWatcher(),
        SystemHealthWatcher(),
        DownloadsWatcher(),
        EmailWatcher(),
        CalendarWatcher(),
    ]
    if settings.enable_self_watcher:
        watchers.append(SelfWatcher())
    if settings.enable_phone_watchers:
        watchers += [CallWatcher(), MessageWatcher()]
    return watchers


class TriggerEngine:
    def __init__(
        self,
        notifier: Notifier | None = None,
        watchers: list[Watcher] | None = None,
        rules: list[Rule] | None = None,
    ) -> None:
        self.notifier = notifier or Notifier()
        self.watchers = watchers if watchers is not None else _default_watchers()
        self.rules: list[Rule] = rules or []  # user-defined overrides, loaded from the DB
        self._scheduler: Any | None = None

    async def load_rules(self) -> None:
        """Pull the user's automation rules from memory (no-op if the DB is unavailable)."""
        global _rules_dirty
        try:
            from purple.runtime import get_memory

            self.rules = await get_memory().get_rules()
            _rules_dirty = False
            log.info("rules_loaded", count=len(self.rules))
        except Exception as exc:
            log.warning("rules_load_failed", error=str(exc))

    async def tick(self, watchers: list[Watcher] | None = None) -> int:
        """Poll the given watchers once (all of them by default); dispatch any events."""
        if _rules_dirty:
            await self.load_rules()
        dispatched = 0
        for watcher in self.watchers if watchers is None else watchers:
            try:
                for raw in await watcher.check():
                    outcome = apply_rules(self.rules, raw)  # user rules: mute / escalate / act
                    if not outcome.mute:
                        if outcome.force_speak and _ORDER.get(raw.priority, 1) < _ORDER[IMPORTANT]:
                            raw.priority = IMPORTANT
                        await self.notifier.notify(raw)
                        dispatched += 1
                    for tool, args in outcome.actions:
                        await self._run_action(tool, args)
            except Exception as exc:
                log.warning("watcher_failed", watcher=getattr(watcher, "name", "?"), error=str(exc))
        return dispatched

    async def _run_action(self, tool: str, args: dict) -> None:
        """Run a rule's action under the autonomy policy.

        notify  → never run; just tell the user a rule could act.
        confirm → never run unattended; surface a prompt to approve it in chat.
        act     → run it now, but high-risk (requires_confirmation) tools are auto-declined
                  in the background, so unattended actions can never spend money / be
                  irreversible without you. Lower-risk tools run freely.
        """
        mode = settings.autonomy
        if mode == "notify":
            await self.notifier.notify(
                Event("automation", f"A rule matched — I can run {tool} (autonomy: notify)", priority=NORMAL)
            )
            return
        if mode == "confirm":
            await self.notifier.notify(
                Event("automation", f"A rule wants to run {tool} — tell me to go ahead", priority=IMPORTANT)
            )
            return

        async def _decline_risky(_name: str, _args: dict) -> bool:
            return False  # unattended: never auto-approve a high-risk tool

        from purple.tools import registry

        result = await registry.execute(tool, args, _decline_risky)
        ok = bool(result.get("ok"))
        log.info("automation_action", tool=tool, ok=ok, error=result.get("error"))
        await self.notifier.notify(
            Event(
                "automation",
                f"Ran {tool}" if ok else f"Couldn't run {tool}: {result.get('error', '')}",
                priority=NORMAL,
            )
        )

    def start(self) -> None:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        default_period = max(15, min(settings.system_poll_seconds, settings.email_poll_seconds))
        # Watchers can opt into a faster/slower poll (calls need ~5s); group by interval
        # so each cohort gets its own job instead of forcing one period on all of them.
        groups: dict[int, list[Watcher]] = {}
        for watcher in self.watchers:
            groups.setdefault(watcher.interval or default_period, []).append(watcher)

        self._scheduler = AsyncIOScheduler()
        for period, cohort in groups.items():
            self._scheduler.add_job(
                self.tick,
                IntervalTrigger(seconds=period),
                args=[cohort],
                id=f"trigger_tick_{period}s",
                replace_existing=True,
            )
        self._scheduler.start()
        log.info(
            "triggers_started",
            watchers=[w.name for w in self.watchers],
            periods=sorted(groups),
        )

    def stop(self) -> None:
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
