# Observability

Purple has three layers of observability: **logs** (always on), **metrics** (Prometheus,
on by default), and **traces** (OpenTelemetry, opt-in). Everything is local-first.

## Logs

Structured logs (structlog) go to the console **and** a rotating file. The agent, tools,
LLM, DB, voice loop and scheduler all log key events.

- Location: `logs/purple.log` (rotates at ~5 MB, keeps 5 backups).
- Tune via `.env`: `PURPLE_LOG_TO_FILE`, `PURPLE_LOG_DIR`, `PURPLE_LOG_MAX_BYTES`,
  `PURPLE_LOG_BACKUPS`, `PURPLE_LOG_LEVEL`.
- A separate per-action audit trail for development lives in `.claude/log.md` (bnac).

## Metrics (Prometheus)

Exposed at `GET /metrics` in the Prometheus text format. Series:

| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `purple_requests_total` | counter | `endpoint` | HTTP requests handled |
| `purple_agent_turns_total` | counter | — | Completed agent turns |
| `purple_llm_calls_total` | counter | `model` | LLM chat calls |
| `purple_llm_seconds` | histogram | — | LLM chat latency |
| `purple_tool_calls_total` | counter | `tool`, `ok` | Tool calls (ok=true/false) |
| `purple_tool_seconds` | histogram | `tool` | Tool latency |

Scrape it with a local Prometheus (`scrape_configs` → `targets: ['127.0.0.1:8765']`,
`metrics_path: /metrics`) and graph in Grafana, or just `curl 127.0.0.1:8765/metrics`.

## Traces (OpenTelemetry)

Off by default. Spans cover the `llm_chat` and `tool` calls so you can see where time
goes in a turn.

1. Install the extra: `pip install -e ".[observability]"`
2. Enable in `.env`:
   ```
   PURPLE_ENABLE_TRACING=true
   # blank -> spans print to the console; or point at an OTLP collector:
   PURPLE_OTLP_ENDPOINT=http://127.0.0.1:4318/v1/traces
   ```

If the OpenTelemetry SDK isn't installed or tracing is disabled, span calls are
zero-cost no-ops — nothing breaks.

## LLM-call tracing (optional, Langfuse)

For prompt/response-level tracing and eval of the model itself, self-host
[Langfuse](https://langfuse.com) (Docker) and wrap the Ollama client — a good next step
if you want to inspect exactly what the model saw. Not wired in by default since it needs
an external service; ask and it can be added behind a config flag.
