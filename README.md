# Purple

A fully-local, Jarvis-style personal assistant that runs on your own PC. The model, your
memory, and your data never leave the machine. Purple holds a conversation, remembers things
about you, controls your Windows PC, automates the web, watches for things worth telling you
about, runs long multi-step missions, and talks back in a natural voice — and she asks before
doing anything irreversible or that spends money.

> **Status:** all six build milestones landed (always-on • proactivity • knows-me • duplex
> voice • autonomy • smart-home foundation). Tonight-ready run guide: **[RUN_TONIGHT.txt](RUN_TONIGHT.txt)**.

## Built here, run on your hardware

The code lives in this folder on your PC, but it **runs on your machine** — your GPU, your
Ollama, your Postgres. Development happens in an isolated sandbox that can't see your GPU, so
the loop is: code lands here → you run a command on your PC → you paste the output back →
fixes get written here. `python -m purple.selfcheck` and clear logging exist to make that loop
fast. When troubleshooting, start by pasting the relevant output.

## What she can do

- **Conversation + memory** — chat by text or voice; remembers your profile, people, durable
  facts, a rolling session summary, and passages from your documents (RAG over PDF/Word/MD/TXT).
- **PC control** — open apps, manage windows, files (search/move/copy/delete-to-recycle-bin),
  clipboard, media keys, lock/sleep, and a generic UI-automation layer (screenshot + read +
  click/type) that can drive *any* Windows app. Plus a vision model to see the screen.
- **Web** — a persistent Playwright browser she can open, read, click (by visible text), and fill.
- **Proactivity** — watchers (system health, downloads, email, calendar, phone calls/messages)
  feed a fast rules-based priority engine; important things break through, the rest stay quiet
  during focus/quiet hours. You shape it all with natural-language **Automations**.
- **Boot greeting + briefing** — a time-aware hello on startup (varied each time), a morning
  weather line (or a heads-up if rough weather is coming), and live news headlines on request;
  a scheduled morning briefing that **catches up** if your PC was off at the scheduled time.
- **Self-learning suggestions** — she watches her own tool usage and proposes improvements in
  her own voice (e.g. "you lean on raw commands a lot — want a dedicated tool for that?").
- **Screen observation (opt-in)** — say *"start observing"* and she can use your active-window
  title to ground vague requests; *"stop observing"* turns it off. Off by default, auto-stops
  after a few hours, with a visible toggle in the UI.
- **Voice** — wake word ("hey …"), streaming spoken replies, barge-in, and continuous
  conversation. Only **enrolled** voices may command her (fail-closed speaker gate).
- **Missions** — long-horizon, multi-step autonomy with checkpoints, resume-on-restart, and
  sub-agents that delegate into the same executor.
- **Email / calendar** — Gmail + Google Calendar (optional; the one feature that calls an
  external API). Sending/creating always requires confirmation.
- **Smart home** — a local-first Home Assistant foundation (control devices once you have them).

## Architecture

```
 React + Tauri  (thin desktop UI: Chat / Monitor / Automations / Memory / Missions / Settings)
        |  REST + WebSocket
 FastAPI backend (src/purple/app.py)
        |
   Agent loop (agent/)  ──calls──>  Tools (tools/): PC, files, browser, vision, phone,
        |                            email/calendar, missions, smart home, observe, …
        |                            └─ risky tools gated by a human-confirmation step
   LLM via Ollama (llm/)            — qwen2.5:14b + qwen3-vl vision + nomic-embed
   Memory: PostgreSQL + pgvector (memory/)  — history, facts, profile, episodic summaries, RAG
   Speech (speech/): faster-whisper STT + Kokoro TTS (XTTS / Sarvam optional)
   Proactivity (triggers/): watchers → priority → notifier (voice / toast / feed)
```

## Prerequisites (install on your PC)

1. **Python 3.12** — https://python.org
2. **Ollama** — https://ollama.com , then:
   ```
   ollama pull qwen2.5:14b-instruct-q4_K_M
   ollama pull nomic-embed-text
   ollama pull qwen3-vl:8b          # optional, for screen vision
   ```
3. **PostgreSQL 16+ with pgvector**:
   ```sql
   CREATE DATABASE purple;
   CREATE USER purple WITH PASSWORD 'purple';
   GRANT ALL PRIVILEGES ON DATABASE purple TO purple;
   \c purple
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. **ffmpeg** (for microphone / speech) — `winget install Gyan.FFmpeg`
5. **Node.js LTS** (only for the desktop UI) — https://nodejs.org

## Setup

**Fastest (Windows):**

```
powershell -ExecutionPolicy Bypass -File setup.ps1
```

This creates the virtual env, installs Purple, pulls the Ollama models, sets up the database +
pgvector, downloads the Kokoro voice, copies `.env`, and finishes with the self-check. Then
edit `.env` (at minimum set `PURPLE_WEATHER_LOCATION` to your city). See **[RUN_TONIGHT.txt](RUN_TONIGHT.txt)**
for the full start-to-end run + feature-testing checklist, and **[docs/FIRSTRUN.md](docs/FIRSTRUN.md)**
for first-run troubleshooting.

Manual install:

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
copy .env.example .env
```

**Optional extras** (install only what you want):

```
pip install -e ".[speaker]"        # voice access gate (only enrolled voices may talk to her)
pip install -e ".[google]"         # Gmail + Calendar
pip install -e ".[xtts]"           # XTTS voice-cloning TTS backup
pip install -e ".[observability]"  # OpenTelemetry tracing for /metrics
```

## Run

```
purple                       # the server — or: python -m purple.run   (UI/API on :8765)
python -m purple.selfcheck   # live go/no-go diagnostic (run this if anything misbehaves)
purple-service               # run as a single-instance background service
```

Quick smoke test (second terminal, server running):

```
Invoke-RestMethod http://127.0.0.1:8765/health | ConvertTo-Json
Invoke-RestMethod -Method Post http://127.0.0.1:8765/chat -ContentType 'application/json' -Body '{"message":"Hi Purple, who are you?"}'
```

The desktop UI lives in `frontend/` (React + Tauri) — see `frontend/README.md`.

## Project layout

```
src/purple/
  config.py            all settings (env-driven, PURPLE_* vars)
  app.py               FastAPI app: chat / ws / voice + all REST endpoints
  run.py · cli.py      server entry point · terminal chat
  selfcheck.py         live diagnostic (`python -m purple.selfcheck`)
  service.py           single-instance background service
  safety.py            commit-confirmation guard for risky actions
  agent/               orchestration loop + persona/system prompt
  llm/                 Ollama client (the brain)
  memory/              Postgres + pgvector: history, facts, profile, summaries, RAG
  speech/              STT/TTS provider interface (faster-whisper + Kokoro; XTTS/Sarvam opt.)
  voice/               wake word, VAD, streaming + barge-in conversation loop
  speaker.py           enrolled-voice access gate (fail-closed)
  tools/               registry + all capabilities (PC, files, browser, vision, phone,
                       email/calendar, missions, smart home, observe, briefing, automations)
  browser/             persistent Playwright controller
  desktop/             tray icon + global push-to-talk hotkey
  triggers/            watchers → priority → notifier (proactivity engine)
  autonomy/            mission planner + store + executor (long-horizon tasks)
  briefing.py          real weather (Open-Meteo) + RSS news, built and delivered
  greeting.py          time-aware boot greeting (randomized; morning weather; news offer)
  observe.py           opt-in screen-context observation (privacy-gated)
  usage.py             durable tool-usage log  ·  suggestions.py  self-improvement ideas
  jobs.py · scheduler.py   scheduled jobs + boot catch-up for missed runs
  smarthome.py         Home Assistant client  ·  integrations/google.py  Gmail+Calendar
  gpu.py · focus.py    GPU monitor + Focus mode (yield the GPU while gaming/rendering)
  observability.py     metrics + optional tracing  ·  utils/logging.py  structured logs
tests/unit/            pytest suite (run: pytest)
pyproject.toml         metadata + ruff / mypy / pytest config (canonical)
doctor.py              environment diagnostic
setup.ps1              one-command Windows setup
RUN_TONIGHT.txt        copy-paste run + feature-testing guide
.claude/               bnac agents, commands, skills, logs — the dev workflow
frontend/              React + Tauri UI (see frontend/README.md)
docs/                  FIRSTRUN, ALWAYS_ON, OBSERVABILITY, EMAIL_CALENDAR, wake_word, roadmap
```

## Safety & privacy

- **Local by default.** The LLM, embeddings, memory, and speech all run on your machine.
  The only feature that calls an external service is the optional Gmail/Calendar integration.
- **Human-in-the-loop.** Anything irreversible or that spends money (purchases, bookings,
  sending messages, deleting files, `run_command`) is tagged `requires_confirmation` and stops
  for your explicit OK. Keep `PURPLE_REQUIRE_CONFIRMATION=true`.
- **Voice is gated.** Once you enroll a voice, only enrolled voices can command her, and the
  gate fails *closed* (no recognition → no action; typing still works).
- **Observation is opt-in.** Screen-context observation is off by default, toggled by voice or
  UI, uses only the active-window title (no screenshots), and auto-stops after a few hours.
- **Secrets stay out of git.** `.env`, `google_credentials.json`, `google_token.json`,
  `voiceprints.json`, your `data/`, `logs/`, and downloaded `models/` are git-ignored.

## Development (bnac)

Managed with **bnac** (BusinessNext Agentic Coding); the python-profile agents, commands, and
skills live in `.claude/`, and every change is logged to `.claude/log.md`. Build via bnac
(`/bnac-python-feature-dev`, `/bnac-python-verify`, `/bnac-python-test`). Lint/format/test:

```
ruff check src/ tests/ && ruff format src/ tests/ && pytest
```

(Target runtime is Python 3.12; use `datetime.UTC`, not `timezone.utc`.)

## Scale path (no rewrite)

Ollama → vLLM for throughput; the agent loop → LangGraph for branchy flows; the Sarvam toggle
for Indian-language voice; the Home Assistant foundation → full device control + device-driven
automations once you have hardware.
