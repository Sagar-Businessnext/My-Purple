"""Commit-confirmation safety layer.

Some actions are irreversible or spend money (tapping 'Pay', 'Send', 'Confirm',
placing an order). A tool can call `confirm()` mid-execution to require explicit human
approval, optionally attaching a screenshot so the user sees exactly what they're OK-ing.

The approver is the same callable passed to the tool registry; it's stashed in a
contextvar so a tool deep in a call can reach it without threading it through signatures.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import contextvars
import re
from typing import Any

from purple.config import settings

Approver = Callable[[str, dict[str, Any]], Awaitable[bool]]

_approver: contextvars.ContextVar[Approver | None] = contextvars.ContextVar(
    "purple_approver", default=None
)

# Words that signal an irreversible / money-spending commit.
COMMIT_RE = re.compile(
    r"\b(pay|buy|purchase|order|checkout|place\s*order|send|confirm|subscribe|book|transfer|donate)\b",
    re.IGNORECASE,
)


def set_current_approver(approver: Approver | None) -> contextvars.Token:
    return _approver.set(approver)


def reset_current_approver(token: contextvars.Token) -> None:
    _approver.reset(token)


def is_commit_label(text: str | None) -> bool:
    return bool(text and COMMIT_RE.search(text))


async def confirm(action: str, screenshot_b64: str | None = None) -> bool:
    """Ask the human to approve a sensitive action. Returns True if approved.
    If no approver is wired in, denies whenever confirmation is required."""
    approver = _approver.get()
    if approver is None:
        return not settings.require_confirmation
    args: dict[str, Any] = {"action": action}
    if screenshot_b64:
        args["screenshot_b64"] = screenshot_b64
    return await approver(action, args)
