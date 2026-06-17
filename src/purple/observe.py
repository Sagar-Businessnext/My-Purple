"""Screen-context observation — explicitly consented, off by default.

Privacy model: Purple only knows what's on your screen when you turn it on ("start
observing") and forgets again when you turn it off ("stop observing"). There is a visible
toggle in the UI, and observation auto-disables after a few hours so it can never silently
stay on. By default she only uses the *current* foreground window as context; logging that
context to memory is a separate opt-in (settings.observe_log_history).

Only the active window *title* is read (cheap, no screenshots), and it's injected as a
one-line system note — the same mechanism as selfstate. The window read is best-effort:
it returns None off-Windows or if the helper isn't installed, and never raises.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("observe")

_UTC = UTC

# Runtime state (default off regardless of config; config only sets the boot default).
_observing: bool = False
_since: datetime | None = None


def should_auto_off(since: datetime | None, now: datetime, max_hours: int) -> bool:
    """Pure: has observation been on longer than its safety window? (max_hours<=0 = never)."""
    if since is None or max_hours <= 0:
        return False
    return (now - since).total_seconds() >= max_hours * 3600


def set_observing(on: bool) -> bool:
    """Turn screen-context observation on/off. Returns the new state."""
    global _observing, _since
    _observing = bool(on)
    _since = datetime.now(_UTC) if _observing else None
    log.info("observe_toggled", observing=_observing)
    return _observing


def is_observing() -> bool:
    """True only if observation is on AND still within its auto-off window."""
    global _observing, _since
    if _observing and should_auto_off(_since, datetime.now(_UTC), settings.observe_auto_off_hours):
        log.info("observe_auto_off", hours=settings.observe_auto_off_hours)
        _observing = False
        _since = None
    return _observing


def status() -> dict[str, Any]:
    on = is_observing()
    return {
        "observing": on,
        "since": _since.isoformat() if _since else None,
        "auto_off_hours": settings.observe_auto_off_hours,
        "log_history": settings.observe_log_history,
    }


def active_window_title() -> str | None:
    """Best-effort foreground window title (Windows). None off-Windows / on any error."""
    try:
        import pygetwindow as gw

        win = gw.getActiveWindow()
    except Exception:
        return None
    title = getattr(win, "title", None) if win else None
    title = (title or "").strip()
    return title or None


def context_note() -> str | None:
    """One-line system note about what's on screen, or None when not observing / unknown."""
    if not is_observing():
        return None
    title = active_window_title()
    if not title:
        return None
    if settings.observe_log_history:
        log.info("observed_window", title=title)
    return (
        f"Screen context (you are observing, with the user's consent) — the user is "
        f"currently looking at: {title!r}. Use this to ground vague requests; don't mention "
        "it unless relevant."
    )


def reset() -> None:
    """Test helper: clear observation state."""
    global _observing, _since
    _observing = False
    _since = None
