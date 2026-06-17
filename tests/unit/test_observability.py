"""Tests for the observability facade: metric recording, the /metrics payload, and that
tracing spans are safe no-ops when tracing is disabled."""

from __future__ import annotations

from purple import observability as obs


def test_metrics_text_returns_payload_and_content_type():
    payload, content_type = obs.metrics_text()
    assert isinstance(payload, bytes)
    assert isinstance(content_type, str) and content_type


def test_record_calls_are_safe_and_exposed():
    obs.record_request("chat")
    obs.record_turn()
    obs.record_llm("test-model", 0.01)
    obs.record_tool("open_app", True, 0.02)
    obs.record_tool("run_command", False, 0.5)
    text = obs.metrics_text()[0].decode()
    if obs._PROM:  # only assert series names when prometheus_client is installed
        assert "purple_requests_total" in text
        assert "purple_agent_turns_total" in text
        assert "purple_llm_calls_total" in text
        assert "purple_tool_calls_total" in text


def test_metrics_summary_shape():
    obs.record_turn()
    obs.record_tool("open_app", True, 0.01)
    s = obs.metrics_summary()
    assert "enabled" in s
    if s.get("enabled"):
        assert s["turns"] >= 1
        assert "tools" in s and "tool_calls" in s and "llm_avg_ms" in s


def test_span_is_noop_when_tracing_disabled():
    # tracing is off by default -> span must be a harmless context manager
    with obs.span("unit-test-span", attr="value"):
        result = 1 + 1
    assert result == 2
