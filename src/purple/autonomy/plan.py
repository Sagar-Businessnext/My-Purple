"""Mission planning + state — pure logic (no DB / LLM / network), so it's unit-tested.

The MissionRunner (missions.py) persists and executes; this module decides the *shape*
of a plan and the mission's status from its steps. The sequential executor's step seam is
where a sub-agent will later be able to take over a step (M5c).
"""

from __future__ import annotations

import json
import re

# Mission statuses
PLANNED = "planned"
RUNNING = "running"
PAUSED = "paused"
BLOCKED = "blocked"
DONE = "done"
FAILED = "failed"
CANCELLED = "cancelled"

# Step statuses
S_PENDING = "pending"
S_RUNNING = "running"
S_DONE = "done"
S_FAILED = "failed"
S_SKIPPED = "skipped"

_MAX_STEPS = 20


def planning_prompt(goal: str) -> str:
    return (
        "Break this goal into a short ordered list of concrete steps Purple can carry out "
        "with her tools (web, files, email, calendar, etc.). Use 3-8 steps. Reply ONLY with "
        'a JSON array of short step strings, e.g. ["Research X", "Compare Y", "Draft Z"].'
        f"\n\nGoal: {goal}"
    )


def parse_plan(text: str) -> list[str]:
    """Parse the planner's reply into step titles. Tolerant: a JSON array if present,
    else numbered/bulleted lines. Capped at _MAX_STEPS."""
    text = (text or "").strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            steps = [str(s).strip() for s in data if str(s).strip()]
            if steps:
                return steps[:_MAX_STEPS]
        except (ValueError, TypeError):
            pass
    steps: list[str] = []
    for line in text.splitlines():
        cleaned = re.sub(r"^\s*(\d+[.)]|[-*•])\s*", "", line).strip()
        if cleaned:
            steps.append(cleaned)
    return steps[:_MAX_STEPS]


def next_pending(statuses: list[str]) -> int | None:
    """Index of the next step to run, or None when there's nothing pending."""
    for i, s in enumerate(statuses):
        if s == S_PENDING:
            return i
    return None


def mission_outcome(statuses: list[str]) -> str:
    """Mission status implied by its step statuses (stop-on-failure policy):
    FAILED if any step failed; DONE if all are done/skipped; otherwise RUNNING."""
    if not statuses:
        return DONE
    if any(s == S_FAILED for s in statuses):
        return FAILED
    if all(s in (S_DONE, S_SKIPPED) for s in statuses):
        return DONE
    return RUNNING


# Words that mark a step as a commit (money / irreversible / outbound) — always checkpointed.
_COMMIT_WORDS = (
    "buy", "pay", "purchase", "order", "checkout", "subscribe", "book", "transfer",
    "send", "email", "message", "post", "publish", "delete", "remove", "cancel",
)


def is_commit_step(title: str) -> bool:
    t = (title or "").lower()
    return any(w in t for w in _COMMIT_WORDS)


def needs_checkpoint(title: str, autonomy: str) -> bool:
    """Should the mission pause for your approval before this step?
    - autonomy 'act'  → only at commit steps (money/irreversible/outbound).
    - 'confirm'/'notify'/other → before every step (cautious default)."""
    if autonomy == "act":
        return is_commit_step(title)
    return True


# Hints that a step is big enough to hand to a sub-agent (its own mini-plan).
_COMPLEX_HINTS = (
    "research", "compare", "each", "several", "multiple", "gather", "analyze",
    "summarize", "for every", "all of", "find and", "look into",
)


def is_complex_step(title: str) -> bool:
    t = (title or "").lower()
    return len(t.split()) >= 8 or " and " in t or any(h in t for h in _COMPLEX_HINTS)


def should_delegate(depth: int, max_depth: int, complex_step: bool) -> bool:
    """Delegate a step to a sub-agent only if it's complex AND under the depth limit (so
    recursion can't run away)."""
    return complex_step and depth < max_depth
