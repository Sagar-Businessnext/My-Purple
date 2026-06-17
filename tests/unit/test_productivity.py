"""Tests for notes/reminders/remember tools and the briefing builder, using a fake
in-memory store (no Postgres needed)."""

from __future__ import annotations

from purple import runtime
from purple.briefing import build_briefing
from purple.config import settings
from purple.tools import load_tools, registry


class FakeMemory:
    def __init__(self) -> None:
        self.notes: list[str] = []
        self.reminders: list[tuple[str, object]] = []
        self.facts: list[str] = []

    async def add_note(self, text: str) -> int:
        self.notes.append(text)
        return len(self.notes)

    async def list_notes(self, limit: int = 10) -> list[str]:
        return self.notes[-limit:]

    async def add_reminder(self, text: str, due_at=None) -> int:
        self.reminders.append((text, due_at))
        return len(self.reminders)

    async def list_reminders(self, include_done: bool = False) -> list[dict]:
        return [{"id": i, "text": t, "due_at": None} for i, (t, _) in enumerate(self.reminders)]

    async def due_reminders(self) -> list[str]:
        return [t for t, _ in self.reminders]

    async def remember(self, text: str, kind: str = "fact") -> None:
        self.facts.append(text)


async def _allow(_n, _a):
    return True


async def test_add_note_tool():
    load_tools()
    mem = FakeMemory()
    runtime.set_runtime(None, mem)
    res = await registry.execute("add_note", {"text": "buy milk"}, approver=_allow)
    assert res["ok"] and mem.notes == ["buy milk"]


async def test_remember_tool():
    load_tools()
    mem = FakeMemory()
    runtime.set_runtime(None, mem)
    res = await registry.execute("remember", {"text": "user prefers tea"}, approver=_allow)
    assert res["ok"] and mem.facts == ["user prefers tea"]


async def test_add_reminder_tool_parses_due():
    load_tools()
    mem = FakeMemory()
    runtime.set_runtime(None, mem)
    res = await registry.execute(
        "add_reminder", {"text": "call mom", "due_iso": "2026-06-10T09:00:00"}, approver=_allow
    )
    assert res["ok"] and mem.reminders[0][0] == "call mom"


async def test_briefing_mentions_reminders():
    mem = FakeMemory()
    await mem.add_reminder("call mom")
    runtime.set_runtime(None, mem)
    text = await build_briefing(agent=None)
    assert "reminder" in text.lower()


async def test_observe_is_noop_when_auto_memory_off():
    from purple.memory.store import Memory

    class BoomLLM:
        async def embed(self, t):
            return [0.0] * 768

        async def chat(self, *a, **k):
            raise AssertionError("LLM must not be called when auto_memory is off")

    settings.auto_memory = False
    mem = Memory(BoomLLM())
    await mem.observe("hi", "hello")  # should simply return, no LLM call
