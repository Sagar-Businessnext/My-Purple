"""Pluggable tool registry — the backbone of "Purple can do anything connected".

Each capability registers a Tool here. Adding a new power = writing a new handler
and registering it; the agent picks it up automatically. No core changes.
Risky tools (requires_confirmation=True) are gated behind the human approver.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import time
from typing import Any

from purple import observability as obs
from purple.config import settings
from purple.safety import reset_current_approver, set_current_approver
from purple.utils.logging import get_logger

log = get_logger("tools")

Approver = Callable[[str, dict[str, Any]], Awaitable[bool]]


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON schema: {"type":"object","properties":{...},"required":[...]}
    handler: Callable[..., Awaitable[Any]]
    requires_confirmation: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            log.warning("tool_override", name=tool.name)
        self._tools[tool.name] = tool

    def tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        requires_confirmation: bool = False,
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        """Decorator to register an async function as a tool."""

        def deco(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            self.register(Tool(name, description, parameters, fn, requires_confirmation))
            return fn

        return deco

    def schemas(self) -> list[dict[str, Any]]:
        """Tool definitions in the function-calling format Ollama expects."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    async def execute(self, name: str, args: dict[str, Any], approver: Approver) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            return {"ok": False, "error": f"unknown tool '{name}'"}

        from purple import usage

        usage.record(name)  # durable usage log (powers Purple's self-suggestions)

        if tool.requires_confirmation and settings.require_confirmation:
            try:
                approved = await approver(name, args)
            except Exception as exc:
                return {"ok": False, "error": f"confirmation failed: {exc}"}
            if not approved:
                return {"ok": False, "error": "cancelled — the user did not confirm this action"}

        # Make the approver reachable to tools that need mid-execution confirmation
        # (e.g. a commit-guarded tap) via purple.safety.confirm().
        token = set_current_approver(approver)
        start = time.perf_counter()
        ok = False
        try:
            with obs.span("tool", tool=name):
                result = await tool.handler(**args)
            ok = True
            return {"ok": True, "result": result}
        except TypeError as exc:
            return {"ok": False, "error": f"bad arguments for '{name}': {exc}"}
        except Exception as exc:
            log.warning("tool_error", tool=name, error=str(exc))
            return {"ok": False, "error": str(exc)}
        finally:
            obs.record_tool(name, ok, time.perf_counter() - start)
            reset_current_approver(token)


# Shared singleton imported by tool modules and the agent.
registry = ToolRegistry()
