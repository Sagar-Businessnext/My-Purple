"""Email + calendar tools (Google). Reading/searching/drafting are safe; sending an
email and creating a calendar event are commit actions and ask for confirmation first
(prepare-then-confirm). The blocking Google client runs in a worker thread.
"""

from __future__ import annotations

import asyncio

from purple.integrations.google import google
from purple.tools.registry import registry


@registry.tool(
    "list_emails",
    "List recent inbox emails (id, from, subject, snippet).",
    {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
)
async def list_emails(limit: int = 10) -> list[dict] | str:
    return await asyncio.to_thread(google.list_emails, limit) or "inbox empty"


@registry.tool(
    "search_email",
    'Search email with a Gmail query, e.g. "from:mom is:unread", "subject:invoice".',
    {
        "type": "object",
        "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
        "required": ["query"],
    },
)
async def search_email(query: str, limit: int = 10) -> list[dict] | str:
    return await asyncio.to_thread(google.search_emails, query, limit) or "no matches"


@registry.tool(
    "read_email",
    "Read the full text of an email by its id (from list_emails / search_email).",
    {
        "type": "object",
        "properties": {"message_id": {"type": "string"}},
        "required": ["message_id"],
    },
)
async def read_email(message_id: str) -> dict:
    return await asyncio.to_thread(google.read_email, message_id)


@registry.tool(
    "draft_email",
    "Create a Gmail draft (does NOT send) — prepare a message for the user to review/send.",
    {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["to", "subject", "body"],
    },
)
async def draft_email(to: str, subject: str, body: str) -> str:
    draft_id = await asyncio.to_thread(google.create_draft, to, subject, body)
    return f"Draft created ({draft_id}) — review in Gmail, or ask me to send it."


@registry.tool(
    "send_email",
    "Send an email. Confirmation is required before it goes out.",
    {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["to", "subject", "body"],
    },
    requires_confirmation=True,
)
async def send_email(to: str, subject: str, body: str) -> str:
    message_id = await asyncio.to_thread(google.send_email, to, subject, body)
    return f"Sent to {to} ({message_id})."


@registry.tool(
    "list_events",
    "List upcoming calendar events.",
    {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
)
async def list_events(limit: int = 10) -> list[dict] | str:
    return await asyncio.to_thread(google.list_events, limit) or "no upcoming events"


@registry.tool(
    "create_event",
    "Create a calendar event. start_iso/end_iso are ISO-8601 datetimes. Confirmation required.",
    {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "start_iso": {"type": "string"},
            "end_iso": {"type": "string"},
        },
        "required": ["summary", "start_iso", "end_iso"],
    },
    requires_confirmation=True,
)
async def create_event(summary: str, start_iso: str, end_iso: str) -> str:
    link = await asyncio.to_thread(google.create_event, summary, start_iso, end_iso)
    return f"Event created: {link}"
