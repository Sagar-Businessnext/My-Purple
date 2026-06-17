"""Observability facade — metrics + traces in one place, with graceful fallbacks.

Everything here is safe to call unconditionally: if prometheus_client isn't installed
the metric calls become no-ops, and tracing is a no-op unless explicitly enabled. The
rest of the codebase calls record_* / span() without caring whether the backends exist,
so observability never becomes a hard dependency of core behaviour.
"""

from __future__ import annotations

from collections.abc import Iterator
import contextlib
from typing import Any

from purple.utils.logging import get_logger

log = get_logger("observability")

# --- Metrics (Prometheus, optional) ---
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    _REQUESTS = Counter("purple_requests_total", "HTTP requests", ["endpoint"])
    _TURNS = Counter("purple_agent_turns_total", "Agent turns completed")
    _LLM = Counter("purple_llm_calls_total", "LLM chat calls", ["model"])
    _LLM_SEC = Histogram("purple_llm_seconds", "LLM chat latency (seconds)")
    _TOOL = Counter("purple_tool_calls_total", "Tool calls", ["tool", "ok"])
    _TOOL_SEC = Histogram("purple_tool_seconds", "Tool latency (seconds)", ["tool"])
    _PROM = True
except Exception:
    _PROM = False


def record_request(endpoint: str) -> None:
    if _PROM:
        _REQUESTS.labels(endpoint).inc()


def record_turn() -> None:
    if _PROM:
        _TURNS.inc()


def record_llm(model: str, seconds: float) -> None:
    if _PROM:
        _LLM.labels(model).inc()
        _LLM_SEC.observe(seconds)


def record_tool(tool: str, ok: bool, seconds: float) -> None:
    if _PROM:
        _TOOL.labels(tool, str(ok).lower()).inc()
        _TOOL_SEC.labels(tool).observe(seconds)


def metrics_text() -> tuple[bytes, str]:
    """Prometheus exposition payload for the /metrics endpoint."""
    if _PROM:
        return generate_latest(), CONTENT_TYPE_LATEST
    return b"# prometheus_client not installed\n", "text/plain; charset=utf-8"


def metrics_summary() -> dict[str, Any]:
    """Compact JSON view of the metrics for the desktop UI's Monitor tab."""
    if not _PROM:
        return {"enabled": False}

    def _total(metric: Any) -> float:
        return sum(
            s.value for m in metric.collect() for s in m.samples if s.name.endswith("_total")
        )

    def _avg_ms(metric: Any) -> float:
        count = total = 0.0
        for m in metric.collect():
            for s in m.samples:
                if s.name.endswith("_count"):
                    count += s.value  # sum across all label series (e.g. per-tool)
                elif s.name.endswith("_sum"):
                    total += s.value
        return round(total / count * 1000, 1) if count else 0.0

    tools = [
        {"tool": s.labels.get("tool"), "ok": s.labels.get("ok"), "count": s.value}
        for m in _TOOL.collect()
        for s in m.samples
        if s.name.endswith("_total")
    ]
    requests = {
        s.labels.get("endpoint"): s.value
        for m in _REQUESTS.collect()
        for s in m.samples
        if s.name.endswith("_total")
    }
    return {
        "enabled": True,
        "turns": _total(_TURNS),
        "llm_calls": _total(_LLM),
        "llm_avg_ms": _avg_ms(_LLM_SEC),
        "tool_calls": _total(_TOOL),
        "tool_avg_ms": _avg_ms(_TOOL_SEC),
        "tools": sorted(tools, key=lambda t: -t["count"]),
        "requests": requests,
    }


# --- Tracing (OpenTelemetry, optional + off by default) ---
_tracer: Any | None = None


def setup_tracing() -> None:
    """Wire OpenTelemetry if enabled. Exports to an OTLP endpoint if configured, else to
    the console. No-op (and never raises) if disabled or the SDK isn't installed."""
    global _tracer
    from purple.config import settings

    if not settings.enable_tracing:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        provider = TracerProvider()
        if settings.otlp_endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otlp_endpoint))
            )
        else:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("purple")
        log.info("tracing_enabled", otlp=settings.otlp_endpoint or "console")
    except Exception as exc:
        log.warning("tracing_setup_failed", error=str(exc))


@contextlib.contextmanager
def span(name: str, **attributes: Any) -> Iterator[None]:
    """Open a trace span (no-op unless tracing is enabled)."""
    if _tracer is None:
        yield
        return
    with _tracer.start_as_current_span(name) as current:
        for key, value in attributes.items():
            current.set_attribute(key, value)
        yield
