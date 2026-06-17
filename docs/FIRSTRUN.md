# Purple — first run

Everything was built and logic-tested in a sandbox; this is the first time it runs on
real hardware (your GPU, Ollama, Postgres). Expect a fix or two — paste any failing
output back and it gets sorted quickly.

## Order of operations

1. **Install prerequisites** (one time): Python 3.12, Ollama, PostgreSQL 16+ with
   pgvector, ffmpeg, Node.js LTS. (Details + DB SQL in the main README.)
2. **Static check:** `python doctor.py` — confirms Python, GPU/VRAM, RAM, disk, and
   whether Ollama / Postgres / ffmpeg are reachable. Fix any `[FAIL]` first.
3. **One-command setup:** `powershell -ExecutionPolicy Bypass -File setup.ps1`
   — creates the venv, installs Purple, pulls the models, creates the DB, downloads a
   voice, then runs the self-check. (Re-runnable; each step is best-effort.)
4. **Live self-check:** `python -m purple.selfcheck` — actually chats with the model,
   round-trips memory through Postgres, loads the tools, checks speech. Aim for all
   `[ OK ]`.
5. **Talk to it (no UI):** `python -m purple.cli` — try "open notepad", "what's using
   the most memory", "search the web for X".
6. **Run the server:** `purple` (or `python -m purple.run`) → http://127.0.0.1:8765/health
7. **Desktop UI (optional):** see `frontend/README.md` (three commands).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Ollama not reachable` | Start it: `ollama serve`. Confirm `PURPLE_OLLAMA_BASE_URL` in `.env`. |
| `model ... not pulled` / slow first reply | `ollama pull qwen2.5:14b-instruct-q4_K_M` and `ollama pull nomic-embed-text`. |
| `PostgreSQL ... not reachable` | Start Postgres; verify `PURPLE_PG_DSN`. Create DB: `CREATE DATABASE purple;` |
| `CREATE EXTENSION vector` errors | Install the **pgvector** extension for your Postgres build, then `CREATE EXTENSION vector;` |
| STT errors / no audio decode | Install ffmpeg: `winget install Gyan.FFmpeg`. |
| `Piper voice missing` | Put `en_US-amy-medium.onnx` + `.json` in `models\piper\` (setup.ps1 tries this). |
| Browser tools fail | `python -m playwright install chromium`. |
| Runs on CPU / very slow | GPU/CUDA not detected — check `nvidia-smi` and your driver; Whisper/LLM fall back to CPU. |
| Out of memory under load | 16 GB RAM is tight with model + Whisper + DB; close apps or add RAM (32 GB+). |
| Wake word / tray / hotkey not active | They're opt-in: set `PURPLE_ENABLE_WAKE`, `PURPLE_ENABLE_TRAY`, `PURPLE_ENABLE_PUSH_TO_TALK` in `.env`. |

If a self-check line shows `[FAIL]`, copy the whole self-check output back — that's
the fastest way to pin down the fix.
