"""Tests for the /config backend (get/set + .env persistence) and the agent's live
tool-event broadcast used by the monitor."""

from __future__ import annotations

from purple import config_api
from purple.agent.orchestrator import Agent
from purple.config import settings
from purple.tools.registry import ToolRegistry


def test_get_config_masks_secret():
    cfg = config_api.get_config()
    assert "sarvam_api_key" not in cfg  # secret value never returned
    assert "sarvam_api_key_set" in cfg  # presence flag only
    assert "llm_model" in cfg and "require_confirmation" in cfg


def test_set_config_persists_and_flags_restart(monkeypatch, tmp_path):
    monkeypatch.setattr(config_api, "ROOT", tmp_path)
    (tmp_path / ".env").write_text("# existing\nPURPLE_HOST=127.0.0.1\n")

    orig_conf, orig_model = settings.require_confirmation, settings.llm_model
    try:
        res = config_api.set_config({"require_confirmation": False, "llm_model": "test:7b"})
        # live-applicable field is applied to the running settings immediately
        assert settings.require_confirmation is False
        # startup-bound field is flagged as needing a restart
        assert "llm_model" in res["restart_needed"]
        assert "require_confirmation" not in res["restart_needed"]
        env = (tmp_path / ".env").read_text()
        assert "PURPLE_REQUIRE_CONFIRMATION=false" in env
        assert "PURPLE_LLM_MODEL=test:7b" in env
        assert "# existing" in env  # existing lines preserved
    finally:
        settings.require_confirmation, settings.llm_model = orig_conf, orig_model


async def test_agent_emits_tool_event():
    reg = ToolRegistry()

    @reg.tool("ping", "ping", {"type": "object", "properties": {}, "required": []})
    async def ping():
        return "pong"

    class FakeLLM:
        def __init__(self):
            self.n = 0

        async def chat(self, messages, tools=None, temperature=0.4):
            self.n += 1
            if self.n == 1:
                return {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{"function": {"name": "ping", "arguments": {}}}],
                }
            return {"role": "assistant", "content": "done"}

        async def embed(self, text):
            return [0.0] * 768

    events: list = []

    async def emit(e):
        events.append(e)

    async def allow(_n, _a):
        return True

    agent = Agent(FakeLLM(), reg, memory=None, emit=emit)
    reply = await agent.respond("ping", approver=allow)
    assert "done" in reply
    assert any(e.get("type") == "tool" and e.get("name") == "ping" for e in events)
