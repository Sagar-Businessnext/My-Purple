"""Smoke tests for the parts that don't need a GPU, Ollama, or Postgres.

These verify the architecture wiring: tool registration, the human-approval gate,
and the agent's tool-calling loop (with a fake LLM).
"""

from __future__ import annotations

import pytest

from purple.agent.orchestrator import Agent
from purple.tools.registry import ToolRegistry


def test_builtin_tools_register_and_expose_schemas():
    from purple.tools import load_tools, registry

    load_tools()
    names = {s["function"]["name"] for s in registry.schemas()}
    assert {"open_app", "web_search", "run_command"} <= names


async def test_permission_gate_blocks_unconfirmed_risky_tool():
    reg = ToolRegistry()
    ran = {"v": False}

    @reg.tool(
        "danger",
        "risky",
        {"type": "object", "properties": {}, "required": []},
        requires_confirmation=True,
    )
    async def danger():
        ran["v"] = True
        return "boom"

    async def deny(_name, _args):
        return False

    async def allow(_name, _args):
        return True

    denied = await reg.execute("danger", {}, approver=deny)
    assert denied["ok"] is False and not ran["v"]

    approved = await reg.execute("danger", {}, approver=allow)
    assert approved["ok"] is True and ran["v"] is True


async def test_agent_runs_a_tool_then_answers():
    reg = ToolRegistry()

    @reg.tool(
        "echo",
        "echo text",
        {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )
    async def echo(text: str):
        return text.upper()

    class FakeLLM:
        def __init__(self):
            self.calls = 0

        async def chat(self, messages, tools=None, temperature=0.4):
            self.calls += 1
            if self.calls == 1:
                return {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{"function": {"name": "echo", "arguments": {"text": "hi"}}}],
                }
            return {"role": "assistant", "content": "I said HI."}

        async def embed(self, text):
            return [0.0] * 768

    async def allow(_n, _a):
        return True

    agent = Agent(FakeLLM(), reg, memory=None)
    reply = await agent.respond("say hi", approver=allow)
    assert "HI" in reply


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
