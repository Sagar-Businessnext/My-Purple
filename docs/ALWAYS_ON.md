# Always-on presence + GPU Focus mode

Run Purple 24/7 as a resilient background service that starts with your PC, and that
yields the GPU to your games/renders instead of fighting them.

## Run as a service

```bash
purple-service          # or: python -m purple.service
```

It takes a single-instance lock (`data/purple.lock`) so two Purples never run at once,
then starts the server (which in turn runs the voice loop and scheduler). Crash recovery
comes from the Scheduled Task (below), which relaunches it if it exits.

### Autostart at logon (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_service.ps1   # register
powershell -ExecutionPolicy Bypass -File scripts\uninstall_service.ps1 # remove
```

Registers a hidden task ("Purple") that launches `python -m purple.service` via
`pythonw.exe` at logon and restarts it up to 3×/min if it stops. (Alternative: run as a
true Windows Service with [NSSM](https://nssm.cc) pointing at the same command.)

Note: the PC must actually be on for a 24/7 assistant — sleep/hibernate pauses it.

## GPU Focus mode — coexisting with gaming/rendering

Running 24/7 does **not** keep the GPU occupied: Ollama unloads idle models after a few
minutes, so when you're not actively using Purple the GPU is free. The only contention is
if Purple runs inference at the same moment as a heavy GPU task — and Focus mode handles
that:

- When focus is active, Purple **defers its GPU-heavy background work** (proactive
  LLM/vision). It stays alive for GPU-free tasks (reminders, email/calendar,
  notifications, rule-based triggers).
- Active when: you toggle it (`POST /focus {"on": true}` or the UI button /
  `PURPLE_FOCUS_MODE=true`), **or** `PURPLE_AUTO_FOCUS=true` (default) and the GPU is busy
  (utilisation ≥ `PURPLE_GPU_BUSY_UTIL` or VRAM used ≥ `PURPLE_GPU_BUSY_VRAM_MB`).
- Interactive requests you make are **not** blocked — if you ask Purple something while
  gaming, it still answers; only autonomous background GPU work yields.

Zero-contention options: keep a small model resident for triage and load the big model on
demand, or point `PURPLE_OLLAMA_BASE_URL` at a second machine so this GPU is never used.

## Reaching Purple from another device

By default Purple binds to localhost. To reach it from your phone / another room:

```
PURPLE_HOST=0.0.0.0
PURPLE_API_TOKEN=<a long random string>
```

Non-localhost requests must then send `X-Purple-Token: <token>`. The desktop app on the
same machine (localhost) is unaffected. Only expose it on a network you trust.

## Status

`GET /status` → version, pid, uptime, and focus/GPU state. Surfaced as uptime + focus
badges in the desktop UI's Monitor tab.
