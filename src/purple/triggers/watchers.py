"""Watchers — observe a source and surface Events. Cheap + CPU-only (no GPU).

Ships system (disk/battery + CPU/RAM health), email, calendar, phone calls (spam-aware),
phone messages, and finished downloads. News + weather fit better in the daily briefing.
"""

from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime
from pathlib import Path

from purple.config import settings
from purple.triggers.priority import IMPORTANT, NORMAL, Event, classify, is_spam_caller
from purple.utils.logging import get_logger

log = get_logger("watchers")


class Watcher:
    name = "watcher"
    interval: int | None = None  # poll period override (seconds); None = engine default

    async def check(self) -> list[Event]:
        return []


class SystemWatcher(Watcher):
    name = "system"

    async def check(self) -> list[Event]:
        def _do() -> list[Event]:
            import shutil

            import psutil

            out: list[Event] = []
            free_gb = shutil.disk_usage(str(settings.data_dir)).free / 1e9
            if free_gb < settings.disk_low_gb:
                out.append(
                    Event("system", f"Low disk space — {free_gb:.0f} GB free", priority=IMPORTANT)
                )
            bat = getattr(psutil, "sensors_battery", lambda: None)()
            if bat and not bat.power_plugged and bat.percent <= 15:
                out.append(Event("system", f"Battery low — {bat.percent:.0f}%", priority=IMPORTANT))
            return out

        return await asyncio.to_thread(_do)


class EmailWatcher(Watcher):
    name = "email"

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self._primed = False

    async def check(self) -> list[Event]:
        try:
            from purple.integrations.google import google

            msgs = await asyncio.to_thread(google.search_emails, "is:unread newer_than:1d", 10)
        except Exception:
            return []
        if not self._primed:  # first run: baseline existing unread, don't flood
            self._seen = {m["id"] for m in msgs}
            self._primed = True
            return []
        out: list[Event] = []
        for m in msgs:
            if m["id"] in self._seen:
                continue
            self._seen.add(m["id"])
            priority = classify(m.get("subject", ""), m.get("snippet", ""), m.get("from", ""))
            if priority == IMPORTANT:  # only surface important unread, not every email
                out.append(
                    Event(
                        "email",
                        f"Email from {m.get('from', '')}",
                        m.get("subject", ""),
                        priority=priority,
                        sender=m.get("from", ""),
                    )
                )
        return out


class CalendarWatcher(Watcher):
    name = "calendar"

    def __init__(self) -> None:
        self._notified: set[str] = set()

    async def check(self) -> list[Event]:
        try:
            from purple.integrations.google import google

            events = await asyncio.to_thread(google.list_events, 5)
        except Exception:
            return []
        out: list[Event] = []
        now = datetime.now().astimezone()
        for ev in events:
            eid, start = ev.get("id", ""), ev.get("start", "")
            if not start or eid in self._notified:
                continue
            with contextlib.suppress(Exception):
                when = datetime.fromisoformat(start)
                mins = (when - now).total_seconds() / 60
                if 0 < mins <= settings.calendar_lead_minutes:
                    self._notified.add(eid)
                    out.append(
                        Event(
                            "calendar",
                            f"Starting soon: {ev.get('summary', 'event')}",
                            f"in {mins:.0f} min",
                            priority=IMPORTANT,
                        )
                    )
        return out


class CallWatcher(Watcher):
    """Incoming-call watcher. A call from a known contact breaks through (gentle voice,
    once); an unknown number (likely spam) is logged quietly without interrupting you.
    Contacts are read once over ADB and cached. Polls fast because rings are brief."""

    name = "call"

    def __init__(self) -> None:
        self.interval = settings.phone_poll_seconds
        self._contacts: list[str] | None = None
        self._last_number = ""  # de-dupe the same ringing call across polls

    async def _contacts_list(self) -> list[str]:
        if self._contacts is None:
            from purple.phone import adb

            rc, out = await adb.run_adb(adb.cmd_contacts())
            self._contacts = adb.parse_contacts(out) if rc == 0 else []
            log.info("contacts_loaded", count=len(self._contacts))
        return self._contacts

    async def check(self) -> list[Event]:
        from purple.phone import adb

        rc, out = await adb.run_adb(adb.cmd_call_state(), timeout=10.0)
        if rc != 0:
            return []  # no phone attached / adb missing — silently skip
        state, number = adb.parse_call_state(out)
        if state != 1:  # not ringing
            if state == 0:  # back to idle: arm for the next call
                self._last_number = ""
            return []
        norm = adb.normalize_number(number)
        if not norm or norm == self._last_number:
            return []
        self._last_number = norm
        if is_spam_caller(norm, await self._contacts_list()):
            return [
                Event(
                    "call",
                    f"Call from {number or 'unknown number'}",
                    "not in your contacts",
                    priority=NORMAL,  # quiet: no breakthrough during games / quiet hours
                    sender=number,
                )
            ]
        return [
            Event(
                "call",
                f"Call from {number}",
                "a known contact is calling",
                priority=IMPORTANT,  # breaks through: one gentle spoken nudge
                sender=number,
            )
        ]


class MessageWatcher(Watcher):
    """Surfaces new phone notifications (messages, chats) read over ADB. Importance is the
    Tier-1 classifier (VIP / urgent keywords); only important ones break through."""

    name = "message"

    def __init__(self) -> None:
        self.interval = max(15, settings.phone_poll_seconds)
        self._seen: set[str] = set()
        self._primed = False

    async def check(self) -> list[Event]:
        from purple.phone import adb

        rc, out = await adb.run_adb(adb.cmd_notifications(), timeout=15.0)
        if rc != 0:
            return []
        notes = adb.parse_notifications(out, limit=20)
        if not self._primed:  # baseline what's already there; don't replay history
            self._seen = set(notes)
            self._primed = True
            return []
        events: list[Event] = []
        for note in notes:
            if note in self._seen:
                continue
            self._seen.add(note)
            title, _, body = note.partition(": ")
            events.append(
                Event(
                    "message",
                    f"Phone: {title}",
                    body,
                    priority=classify(title, body, title),
                    sender=title,
                )
            )
        return events


class DownloadsWatcher(Watcher):
    """Tells you when a download finishes. Watches the Downloads folder and surfaces files
    that newly appeared and are complete (ignores Chrome/Firefox part-files)."""

    name = "download"
    _INCOMPLETE = (".crdownload", ".part", ".partial", ".tmp", ".download")

    def __init__(self) -> None:
        self.interval = max(15, settings.system_poll_seconds)
        self._seen: set[str] = set()
        self._primed = False

    def _dir(self) -> Path:
        return Path(settings.download_dir) if settings.download_dir else Path.home() / "Downloads"

    async def check(self) -> list[Event]:
        def _do() -> list[Event]:
            d = self._dir()
            if not d.exists():
                return []
            files = {
                p.name
                for p in d.iterdir()
                if p.is_file() and not p.name.lower().endswith(self._INCOMPLETE)
            }
            if not self._primed:  # baseline what's already there; don't replay history
                self._seen = files
                self._primed = True
                return []
            new = files - self._seen
            self._seen = files
            return [Event("download", f"Download finished: {n}", priority=NORMAL) for n in sorted(new)]

        return await asyncio.to_thread(_do)


class SystemHealthWatcher(Watcher):
    """Warns on sustained CPU saturation, memory pressure, or GPU/VRAM saturation. Requires
    several consecutive breaches (not one spike) and won't repeat until usage recovers, so
    it stays quiet under normal load — RAM/VRAM matter on a 16GB box. (GPU stays busy while
    gaming; that warning is NORMAL so it never breaks through, and you can mute it.)"""

    name = "system"

    def __init__(self) -> None:
        self.interval = max(30, settings.system_poll_seconds)
        self._hits = {"cpu": 0, "ram": 0, "gpu": 0, "gvram": 0}
        self._warned = {"cpu": False, "ram": False, "gpu": False, "gvram": False}

    def _track(self, key: str, value: float, threshold: float) -> bool:
        """Advance the breach counter; return True once on the 3rd sustained breach."""
        if value >= threshold:
            self._hits[key] += 1
        else:
            self._hits[key], self._warned[key] = 0, False
        if self._hits[key] >= 3 and not self._warned[key]:
            self._warned[key] = True
            return True
        return False

    async def check(self) -> list[Event]:
        def _do() -> list[Event]:
            import psutil

            from purple import gpu

            out: list[Event] = []
            cpu = psutil.cpu_percent(interval=None)  # since last call (0.0 on first, priming)
            ram = psutil.virtual_memory().percent
            if self._track("cpu", cpu, settings.cpu_high_pct):
                out.append(Event("system", f"CPU pinned at {cpu:.0f}% for a while", priority=NORMAL))
            if self._track("ram", ram, settings.ram_high_pct):
                out.append(Event("system", f"Memory almost full — {ram:.0f}% used", priority=IMPORTANT))

            g = gpu.status()
            if g.get("available"):
                if self._track("gpu", g["util"], settings.gpu_high_pct):
                    out.append(
                        Event("system", f"GPU pinned at {g['util']}% for a while", priority=NORMAL)
                    )
                gvram = g.get("vram_pct")
                if gvram is not None and self._track("gvram", gvram, settings.gpu_vram_high_pct):
                    out.append(
                        Event("system", f"GPU memory almost full — {gvram}% used", priority=IMPORTANT)
                    )
            return out

        return await asyncio.to_thread(_do)


class SelfWatcher(Watcher):
    """Purple watching her own health — warns (through whatever channel still works) when
    a subsystem she relies on goes down: her voice output, the local LLM, or the memory DB.
    Edge-triggered: one warning per outage, reset on recovery, so she never nags."""

    name = "self"

    def __init__(self) -> None:
        self.interval = max(30, settings.system_poll_seconds)
        self._down = {"audio": False, "llm": False, "db": False}

    def _edge(self, key: str, bad: bool) -> bool:
        """True once on the falling edge (just went bad); resets when it recovers."""
        if bad and not self._down[key]:
            self._down[key] = True
            return True
        if not bad:
            self._down[key] = False
        return False

    async def _llm_down(self) -> bool:
        try:
            from purple.runtime import get_llm

            return not await get_llm().health()
        except RuntimeError:
            return False  # runtime not initialised yet — don't cry wolf
        except Exception:
            return True

    async def _db_down(self) -> bool:
        try:
            from sqlalchemy import text

            from purple.memory.db import engine

            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return False
        except Exception:
            return True

    async def check(self) -> list[Event]:
        from purple import audio

        out: list[Event] = []
        if self._edge("audio", not audio.can_be_heard()):
            out.append(
                Event("self", "Heads up — you won't hear me", audio.describe(), priority=IMPORTANT)
            )
        if self._edge("llm", await self._llm_down()):
            out.append(
                Event("self", "I can't reach my brain (the local LLM)", "Ollama isn't responding",
                      priority=IMPORTANT)
            )
        if self._edge("db", await self._db_down()):
            out.append(Event("self", "My memory database is unreachable", "", priority=IMPORTANT))
        return out
