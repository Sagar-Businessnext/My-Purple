"""Email/calendar tool tests — registration and the confirmation gate on send/create,
with the Google client faked (no network, no OAuth)."""

from __future__ import annotations

from purple.integrations.google import google
from purple.tools import load_tools, registry


async def _allow(_n, _a):
    return True


async def _deny(_n, _a):
    return False


async def test_list_emails(monkeypatch):
    load_tools()
    monkeypatch.setattr(google, "list_emails", lambda limit=10: [{"id": "1", "subject": "Hello"}])
    res = await registry.execute("list_emails", {"limit": 5}, approver=_allow)
    assert res["ok"] and res["result"][0]["subject"] == "Hello"


async def test_send_email_is_confirmation_gated(monkeypatch):
    load_tools()
    sent: list = []
    monkeypatch.setattr(google, "send_email", lambda to, subject, body: (sent.append(to), "mid")[1])

    blocked = await registry.execute(
        "send_email", {"to": "a@b.com", "subject": "hi", "body": "x"}, approver=_deny
    )
    assert blocked["ok"] is False and not sent  # not sent without confirmation

    ok = await registry.execute(
        "send_email", {"to": "a@b.com", "subject": "hi", "body": "x"}, approver=_allow
    )
    assert ok["ok"] and sent == ["a@b.com"]  # sent after confirmation


async def test_create_event_is_confirmation_gated(monkeypatch):
    load_tools()
    created: list = []
    monkeypatch.setattr(
        google,
        "create_event",
        lambda summary, start_iso, end_iso: (created.append(summary), "link")[1],
    )
    res = await registry.execute(
        "create_event",
        {
            "summary": "Dentist",
            "start_iso": "2026-06-10T09:00:00",
            "end_iso": "2026-06-10T10:00:00",
        },
        approver=_deny,
    )
    assert res["ok"] is False and not created
