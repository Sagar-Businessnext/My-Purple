"""Notes & reminders — Purple's notebook and lightweight calendar.

These back onto Postgres via the shared Memory instance (purple.runtime.get_memory()).
"""

from __future__ import annotations

from datetime import datetime

from purple.runtime import get_memory
from purple.tools.registry import registry


@registry.tool(
    name="add_note",
    description="Save a note for the user (e.g. an idea, a fact to jot down).",
    parameters={
        "type": "object",
        "properties": {"text": {"type": "string", "description": "The note content."}},
        "required": ["text"],
    },
)
async def add_note(text: str) -> str:
    note_id = await get_memory().add_note(text)
    return f"Saved note #{note_id}."


@registry.tool(
    name="list_notes",
    description="List the user's most recent notes.",
    parameters={
        "type": "object",
        "properties": {"limit": {"type": "integer", "description": "How many (default 10)."}},
        "required": [],
    },
)
async def list_notes(limit: int = 10) -> list[str] | str:
    notes = await get_memory().list_notes(limit)
    return notes or "No notes yet."


@registry.tool(
    name="add_reminder",
    description="Add a reminder or calendar entry. due_iso is an optional ISO-8601 "
    "datetime (e.g. '2026-06-10T09:00:00'); omit it for an open to-do.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "What to be reminded of."},
            "due_iso": {"type": "string", "description": "Optional ISO-8601 due datetime."},
        },
        "required": ["text"],
    },
)
async def add_reminder(text: str, due_iso: str | None = None) -> str:
    due = datetime.fromisoformat(due_iso) if due_iso else None
    rid = await get_memory().add_reminder(text, due)
    return f"Reminder #{rid} set" + (f" for {due_iso}." if due_iso else " (no due date).")


@registry.tool(
    name="list_reminders",
    description="List the user's open reminders / upcoming calendar entries.",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def list_reminders() -> list[dict] | str:
    rems = await get_memory().list_reminders()
    return rems or "No open reminders."
