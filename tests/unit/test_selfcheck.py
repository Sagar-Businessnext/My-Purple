"""Tests for the self-check report logic (the live service checks run on the PC)."""

from __future__ import annotations

from purple.config import settings
from purple.selfcheck import FAIL, OK, WARN, Result, check_speech, check_tools, render


def test_render_summary_levels():
    assert "All systems go" in render([Result(OK, "x")])
    assert "warning" in render([Result(WARN, "x")]).lower()
    assert "blocker" in render([Result(FAIL, "x")]).lower()


def test_render_includes_name_and_detail():
    out = render([Result(OK, "Ollama", "reachable")])
    assert "Ollama" in out and "reachable" in out


async def test_check_tools_loads_registry():
    res = await check_tools()
    assert res.status == OK
    assert "tools" in res.detail


def test_check_speech_reports_provider(monkeypatch):
    monkeypatch.setattr(settings, "speech_provider", "local")
    out = check_speech()
    assert any(r.name == "Speech provider" for r in out)
