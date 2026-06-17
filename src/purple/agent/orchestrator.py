"""The agent loop: reason -> (maybe) call tools -> reason -> final answer.

This is intentionally a clean, readable loop rather than a heavy framework. When
flows get genuinely branchy (parallel tools, retries, sub-agents) this is the file
to migrate onto LangGraph — the public `Agent.respond()` signature stays the same.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import json
from typing import Any

from purple import observability as obs
from purple.agent.prompts import build_system_prompt
from purple.utils.logging import get_logger

log = get_logger("agent")

# An approver decides whether a confirmation-required tool may run.
# The API/CLI supplies one that actually asks the user.
Approver = Callable[[str, dict[str, Any]], Awaitable[bool]]

MAX_TOOL_ITERS = 6


async def _auto_deny(tool_name: str, args: dict[str, Any]) -> bool:
    log.warning("no_approver_denying", tool=tool_name)
    return False


class Agent:
    def __init__(
        self, llm: Any, registry: Any, memory: Any | None = None, emit: Any | None = None
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.memory = memory
        self.emit = emit  # optional async callback for live activity (tool calls)

    async def _memory_context(self, user_text: str, session_id: str | None = None) -> str | None:
        if not self.memory:
            return None
        parts: list[str] = []
        try:
            summary = await self.memory.profile_summary()
            if summary:
                parts.append(f"User profile — {summary}")
        except Exception as exc:
            log.warning("profile_summary_failed", error=str(exc))
        if session_id:
            try:
                rolling = await self.memory.get_session_summary(session_id)
                if rolling:
                    parts.append(f"This session so far: {rolling}")
            except Exception as exc:
                log.warning("session_summary_failed", error=str(exc))
        try:
            episodes = await self.memory.search_summaries(user_text, limit=1)
            if episodes:
                parts.append(f"From a past session: {episodes[0]}")
        except Exception as exc:
            log.warning("episodic_recall_failed", error=str(exc))
        try:
            facts = await self.memory.recall(user_text, limit=6)
            if facts:
                parts.append("Relevant memory:\n" + "\n".join(f"- {f}" for f in facts))
        except Exception as exc:
            log.warning("memory_recall_failed", error=str(exc))
        return "\n\n".join(parts) if parts else None

    async def respond(
        self,
        user_text: str,
        history: list[dict[str, Any]] | None = None,
        approver: Approver | None = None,
        session_id: str | None = None,
    ) -> str:
        approver = approver or _auto_deny
        profile: dict[str, str] = {}
        if self.memory:
            try:
                profile = await self.memory.get_profile()
            except Exception as exc:
                log.warning("profile_load_failed", error=str(exc))
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt(profile)}
        ]

        ctx = await self._memory_context(user_text, session_id)
        if ctx:
            messages.append({"role": "system", "content": ctx})

        try:
            from purple import selfstate

            note = selfstate.context_note()
            if note:
                messages.append({"role": "system", "content": note})
        except Exception as exc:
            log.warning("selfstate_failed", error=str(exc))

        try:
            from purple import observe

            screen = observe.context_note()
            if screen:
                messages.append({"role": "system", "content": screen})
        except Exception as exc:
            log.warning("observe_note_failed", error=str(exc))

        messages.extend(history or [])
        messages.append({"role": "user", "content": user_text})

        tools = self.registry.schemas()

        for _ in range(MAX_TOOL_ITERS):
            msg = await self.llm.chat(messages, tools=tools)
            messages.append(msg)

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                final = (msg.get("content") or "").strip()
                if self.memory:
                    await self.memory.observe(user_text, final)
                obs.record_turn()
                return final

            for call in tool_calls:
                fn = call.get("function", {})
                name = fn.get("name", "")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                log.info("tool_call", tool=name, args=args)
                if self.emit:
                    await self.emit({"type": "tool", "name": name})
                result = await self.registry.execute(name, args, approver=approver)
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(result) if not isinstance(result, str) else result,
                    }
                )

        return (
            "I wasn't able to finish that within a reasonable number of steps. "
            "Want me to try a different approach?"
        )
