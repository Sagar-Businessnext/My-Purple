# Purple

A fully-local, Jarvis-style personal assistant that runs on your own PC. The model,
your memory, and your data never leave the machine. Purple can hold a conversation,
remember things about you, control your Windows PC, and automate the web — and it asks
before doing anything irreversible or that spends money.

## How this is built vs. run

The code is written into this folder (`D:\Purple`) on your PC, but it **runs on your
hardware** — your GPU, your Ollama, your Postgres. The dev sandbox can't see your GPU,
so the loop is: code lands here → you run a command on your PC → you paste the output
back → fixes get written here. The `doctor.py` script and clear logging exist to make
that loop fast. Start every troubleshooting message by pasting the relevant output.

## Architecture

```
 React + Tauri  (thin desktop UI)
        |  REST + WebSocket
 FastAPI backend (purple/app.py)
        |
   Agent loop (purple/agent)  ──calls──>  Tools (purple/tools): PC control, web, ...
        |                                    └─ risky tools gated by human confirmation
   LLM via Ollama (purple/llm)
   Memory: PostgreSQL + pgvector (purple/memory)
   Speech: faster-whisper + Piper, Sarvam optional (purple/speech)
```

## Prerequisites (install on your PC)

1. **Python 3.12** — https://python.org
2. **Ollama** — https://ollama.com , then pull the model:
   ```
   ollama pull qwen2.5:14b-instruct-q4_K_M
   ollama pull nomic-embed-text
   ```
3. **PostgreSQL 16+ with pgvector** — install Postgres, then:
   ```sql
   CREATE DATABASE purple;
   CREATE USER purple WITH PASSWORD 'purple';
   GRANT ALL PRIVILEGES ON DATABASE purple TO purple;
   \c purple
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. **ffmpeg** (for speech) — `winget install Gyan.FFmpeg`
5. **Node.js LTS** (for the frontend, later) — https://nodejs.org

## Setup

**Fastest (Windows):** `powershell -ExecutionPolicy Bypass -File setup.ps1` runs every
step below, then a live self-check. See **[docs/FIRSTRUN.md](docs/FIRSTRUN.md)** for the
ordered first-run checklist and troubleshooting. Or do it step by step:

```bash
# 1. Check your environment first
python doctor.py

# 2. Create a virtual environment and install the project (editable, with dev tools)
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium

# 3. Configure
copy .env.example .env
#   edit .env if your Postgres password / model differ

# 4. Download a Piper voice into models\piper\
#   (e.g. en_US-amy-medium.onnx + .json from the Piper releases page)
```

## Run

```bash
# Quickest test — chat in the terminal (no UI needed):
python -m purple.cli

# Full backend server:
purple                 # installed entry point — or: python -m purple.run
#   -> http://127.0.0.1:8765/health
```

Try in the CLI: *"open notepad"*, *"what processes are using the most memory?"*,
*"search the web for flights from Delhi to Kolkata next Friday"*.

## Project layout

```
src/purple/            importable package (bnac src/ layout)
  config.py            all settings (env-driven)
  app.py               FastAPI app (chat / ws / voice)
  run.py               server entry point (`purple` / `python -m purple.run`)
  cli.py               terminal chat
  safety.py            commit-confirmation guard
  agent/               orchestration loop + prompts
  llm/                 Ollama client (the brain)
  memory/              Postgres + pgvector (history + facts)
  speech/              STT/TTS provider interface + local + Sarvam
  tools/               registry, permissions, files, system, browser, UI automation, phone
  browser/             persistent Playwright browser controller
  desktop/             tray icon + push-to-talk hotkey
  voice/               wake word + voice loop
tests/unit/            pytest suite (run: pytest)
pyproject.toml         metadata + ruff / mypy / pytest config (canonical)
doctor.py              environment diagnostic — run first
.claude/               bnac agents, commands, skills — the dev workflow
frontend/              React + Tauri UI (see frontend/README.md)
```

## Development (bnac)

This project is managed with **bnac** (BusinessNext Agentic Coding); its python-profile
agents, commands, and skills live in `.claude/`. Make changes through bnac going forward
— e.g. `/bnac-python-feature-dev` to build, `/bnac-python-verify` to review, and
`/bnac-python-test` to add tests. Lint/format/test locally with:

```bash
ruff check src/ && ruff format src/ && pytest
```

## Roadmap

- **v1 (now):** voice + memory + PC control + web automation, fully local.
- **Next:** "Hey Purple" wake word, automatic fact extraction into memory, daily
  briefing on a schedule, a phone bridge (Android via ADB), richer flight/booking
  flow (find + prepare, you authorize payment).
- **Scale path (no rewrite):** Ollama → vLLM for throughput; the agent loop → LangGraph
  for complex flows; Sarvam toggle for Indian-language voice.

## Safety

Anything that spends money or is irreversible (purchases, bookings, sending messages,
`run_command`) is tagged `requires_confirmation` and will stop for your explicit OK.
Keep `PURPLE_REQUIRE_CONFIRMATION=true`.
