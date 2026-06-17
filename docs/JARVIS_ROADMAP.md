# Purple → Jarvis: capability roadmap

Six feature milestones to close the gap from "very capable assistant" to a real-world
Jarvis, in build order. Re-prioritized from the six gaps by dependency and impact:
presence is the substrate proactivity runs on, so it leads; smart-home depends on
external hardware, so it trails. Built through bnac (python profile).

| # | Milestone | Was gap | Why here |
|---|-----------|---------|----------|
| **M1** | **Always-on presence** | #2 | Foundation — the 24/7 runtime everything proactive needs |
| **M2** | **Proactivity / trigger engine** | #1 | The #1 Jarvis-defining feature; needs M1's always-on runtime |
| **M3** | **Deeper "knows me"** (auto-memory, document RAG, persona, speaker ID) | #6 | Makes anticipation smart; enriches M2 |
| **M4** | **Natural real-time conversation** (streaming duplex voice, barge-in) | #3 | The conversational leap; independent |
| **M5** | **Long-horizon autonomy** (planner + background jobs + sub-agents) | #5 | Whole-mission execution; builds on M1 + agent |
| **M6** | **Physical environment** (smart home / Home Assistant) | #4 | Runs the room; depends on external HA/hardware, so last |

(Holographic UI, robotics/suit control, and omniscient surveillance are deliberately
out of scope — not what makes Jarvis feel like Jarvis day to day.)

---

## Milestone 1 — Always-on presence (the foundation)

**Goal:** Purple runs 24/7 as a single, resilient background service that starts with
the PC, stays up, and is reachable beyond the desktop window — the substrate M2's
proactivity will run on. Today Purple only runs while you keep a terminal/app open.

### What we'll build

1. **Supervised service runtime** (`purple/service.py`) — one long-lived process that
   owns the FastAPI server plus the background loops (voice, scheduler), with graceful
   start/stop and a **single-instance lock** so two Purples never run at once.
2. **Watchdog / resilience** — background loops that crash are caught and restarted with
   backoff and logged; a heartbeat is recorded so the Monitor tab shows uptime.
3. **Autostart at login (Windows)** — `scripts/install_service.ps1` registers a hidden
   Scheduled Task "Purple" that launches the service at logon and relaunches it if it
   exits; `scripts/uninstall_service.ps1` removes it. (NSSM "true service" documented as
   an alternative.)
4. **Reachable from other devices (opt-in, secure)** — allow binding to the LAN
   (`PURPLE_HOST=0.0.0.0`) guarded by an optional API token: a tiny auth middleware that
   requires `X-Purple-Token` for non-localhost requests (localhost stays open for the
   desktop app). So your phone/another room can reach the UI safely.
5. **Lifecycle CLI + status** — `purple-service status` (running? uptime? pid?) and a
   `/status` endpoint surfaced as an "uptime / service" badge in the Monitor tab.
6. **Config:** `api_token` (blank = localhost-only), heartbeat interval; reuse existing
   `host`/`port`.

### Deliverables
`purple/service.py`, token auth middleware in `app.py`, single-instance lock, watchdog
wrapper for the background loops, `scripts/install_service.ps1` + uninstaller,
`docs/ALWAYS_ON.md`, `purple-service` entry point, tests (lock, token gate, watchdog
restart logic), Monitor "uptime" badge. ruff-clean + pytest, logged to `.claude/log.md`.

### Acceptance
Purple autostarts at login, runs as exactly one resilient instance, restarts a failed
background loop on its own, is reachable from another LAN device only with the token,
and reports uptime in the UI.

### Build-vs-run
The lock, watchdog, token gate, and status logic are unit-tested in the sandbox. The
Scheduled-Task autostart and LAN reachability are verified on your PC (the paste-back
loop), since they need the real OS + network.

> **Status: M1 DONE.**

---

## Milestone 2 — Proactivity / trigger engine

**Goal:** Purple watches your world and speaks up on its own — the leap from "assistant
I summon" to "presence that anticipates." Runs on M1's always-on service and reuses the
scheduler, event bus, email/calendar, TTS, and Focus mode we already have.

### The model: watchers → rules → actions
- **Watchers** observe a source on a schedule and surface events:
  email (new/unread, by sender/label), calendar (event starting soon), files (a file
  appears/changes in a watched folder), system (disk/battery low, a process starts), and
  time (richer recurring schedules). Built on the existing scheduler + integrations.
- **Rules** = trigger + condition + action, stored in Postgres. Conditions can be simple
  (`sender == boss`, `disk_free < 20GB`) or **LLM-judged** ("is this email urgent?").
  LLM-judged conditions respect Focus mode — they defer/queue while the GPU is busy.
- **Actions**: notify, speak, draft (email/reminder), or run a safe tool. Anything risky
  (send/spend/irreversible) routes through the existing commit-confirm guard.

### What we'll build
1. `purple/triggers/`: `rules.py` (Rule DB model + CRUD), `engine.py` (registers
   watchers, evaluates rules, dispatches actions, honours Focus + confirm), `watchers.py`
   (email/calendar/file/system/time), `actions.py`, `notify.py`.
2. **Notifications**: real Windows toast + push to the UI activity feed + optional spoken
   (TTS) — so Purple can actually get your attention.
3. **Natural-language triggers**: "tell me if I get mail from my boss", "warn me if disk
   drops below 20 GB", "remind me to stretch hourly" → an LLM parses it into a stored
   rule. Tools: `add_trigger`, `list_triggers`, `toggle_trigger`, `remove_trigger`.
4. **Autonomy levels** (config): `notify` (just tell me) → `confirm` (act, but ask) →
   `act` (do safe actions freely). Default conservative; risky always confirms.
5. **UI**: an "Automations" tab to view/enable/disable/delete rules; fired triggers already
   stream into the Monitor activity feed.
6. Wire the engine into the service lifespan (gated by Focus); fold the morning briefing
   in as a built-in rule. `docs/PROACTIVITY.md`.

### Acceptance
While running as the always-on service, Purple can be told (in plain language) to watch
something, persists the rule, watches autonomously, and notifies you — toast + UI +
optional voice — when it fires, acting only within the configured autonomy level and
confirming anything risky, while deferring LLM-heavy checks when the GPU is busy.

### Build-vs-run
Rule CRUD, the engine's evaluate→dispatch loop, the NL→rule parser, action routing, and
Focus-gating are unit-tested with fakes. Live email/calendar polling, file watching, and
Windows toasts are verified on your PC.

> **Status: planned — awaiting go.**

---

## M3 — Deeper "knows me" (memory) — PLAN (2026-06-12)

**Decisions (user):** lead with **3a**; auto-learning = **Balanced** (salient durable facts only, dedup, reviewable + forgettable, GPU extraction only when the GPU is free); **Speaker ID deferred** to a later pass. Build order: 3a → 3b → 3c → (3d later).

**Baseline today:** every turn injects the top-6 semantically-recalled facts as "Known about the user"; `observe()` auto-extraction exists but is OFF and naive (no dedup/categories). Models: `Fact(text, kind, embedding)`, `Message`, `Note`, `Reminder`, `AutomationRule`. No profile, no documents, no persona config, no memory UI.

### Slice 3a — Smart memory + profile (foundation)
1. **Categorized facts** — `Fact.kind` becomes a real category (`preference | person | project | routine | fact`); recall can filter/boost by category.
2. **Structured profile + entities** — a profile store (you: name, location, work, comms style) + `Person` entities (name, relation, aliases, notes) + `Project` entities; get/set tools. Unify `Person` with VIP/contacts where natural.
3. **Smart auto-memory (Balanced)** — rework `observe()` into one extraction pass that keeps only salient durable facts, **dedups by embedding similarity** (update a near-duplicate instead of inserting), and tags a category. Runs async/non-blocking after the turn; uses the GPU LLM only when `focus.should_yield_gpu()` is False (skips/defers during gaming). Default ON.
4. **Richer context injection** — `_memory_context` assembles profile summary + top-K relevant facts (recency + relevance) + a rolling session summary, within a token budget.
5. **Episodic session summaries** — periodically/at session end, summarize the conversation into a stored summary so Purple recalls "what we did".
6. **Consolidation + forget** — a periodic reflection pass (merge dups, decay stale low-value facts) + a forget tool (by id/topic).
7. **Memory UI tab** — view/search facts + profile + entities, edit, forget, toggle auto-memory; `/memory` API + React tab. (Controlled from the UI, like Automations.)
8. **Privacy** — honor sensitive-data guardrails; never auto-store secrets/health/etc. without explicit consent.

Verify: dedup/update + ranking + profile CRUD + context assembly + forget (unit tests, fake embeddings), ruff, pytest, esbuild for the tab.

### Slice 3b — Document RAG
Point Purple at files/folders (PDF/docx/md/txt) → chunk + embed into pgvector (`Document`/`Chunk` models) → retrieval tool + auto-context in chat; optional watched "knowledge" folder. "Ask my documents."

### Slice 3c — Persona
Configurable personality (name/tone/style — the warm, concise "her") in config + system prompt, editable from Settings, applied to chat and spoken nudges.

### Slice 3d — (LATER) Speaker ID
Enroll the user's voice (local embedding model), recognize the owner on the voice path, optionally gate sensitive actions to the owner.

**Refinements (2026-06-12):**
- **Auto-learning modes** — `auto_memory_mode`: `moderate` (default; durable/important only), `high` (+ softer signals: interests, habits, recurring topics), `aggressive` (capture most novel info, low salience bar). Tunable from the UI; GPU extraction still only runs when the GPU is free.
- **Speaker ID is a firm requirement (3d), not just personalization** — Purple must only converse with **enrolled voices**; an unrecognized voice on the wake-word / mic path is refused. Built in a later slice, but elevated from "optional" to "required access control" in the spec.

---

## M3 — Self-awareness slice (inserted 2026-06-12, before 3a-3)

**Why:** today a muted/off speaker doesn't raise — Purple speaks into the void and never knows you didn't hear. She has passive health checks but no delivery-awareness, no proactive self-monitoring, and her own state isn't in her reasoning.

1. **Delivery-aware voice** — `audio.py` detects the default output device (present? muted? volume>0) via pycaw on Windows (graceful elsewhere). `notify` checks `can_be_heard()` before speaking; if voice can't land it falls back to a toast + on-screen so the message still reaches you, even mid-quiet-hours (it's a failed delivery, not a normal nudge).
2. **Self-health watcher** — a `SelfWatcher` in the trigger engine warns (through a working channel) when Purple's own subsystems degrade: audio out, the local LLM (Ollama), the memory DB. Edge-triggered (warns once per outage, resets on recovery).
3. **Self-state in reasoning** — `selfstate.py` surfaces current issues (e.g. "your output is muted; replies won't be heard"); the orchestrator injects this note when something's degraded, so Purple can actually say "I'm muted — keeping this on screen."

---

## M3 — 3b Document RAG — PLAN (2026-06-12)

**Decisions (user):** retrieval = a TOOL Purple calls when relevant (cites source); ingestion = manual ("learn this file/folder") + one watched "knowledge" folder auto-ingested; file types = PDF (pypdf) + Word (python-docx) + Markdown/text. Fully local (parsing on-machine, embeddings via Ollama nomic-embed-text into the existing pgvector).

**Baseline:** only `read_text_file` (plain text) exists — no parsing, chunking, or retrieval.

### Slice 3b-1 — Ingestion core
- Models: `Document` (id, path, title, sha/mtime, n_chunks, created/updated) + `Chunk` (id, document_id FK, ordinal, text, embedding Vector).
- Parsers: PDF (pypdf), docx (python-docx), .md/.txt (built-in). Dispatch by extension; best-effort, never crash a whole folder on one bad file.
- Pure **chunker** (overlapping windows, ~word-budget + overlap) — unit-tested.
- `ingest_file(path)` / `ingest_folder(path)`: parse → chunk → embed each chunk → store. Idempotent: skip unchanged files (sha/mtime), re-chunk on change (delete old chunks first).
- Management + tools: `ingest`, `list_documents`, `remove_document`, `reingest`.
- New deps: pypdf, python-docx.

### Slice 3b-2 — Retrieval + use
- `search_documents(query, k)` — semantic over chunks (pgvector cosine), returns passages + source file/title.
- Tool `search_documents` (a.k.a. "ask my documents") the agent calls when a question is document-ish; answers cite the source.
- Watched `knowledge_dir` (config): a scheduled/periodic re-ingest of new/changed files (reuse APScheduler).
- UI: a Knowledge section (in the Memory tab or its own) — point at a file/folder, list ingested docs, remove; `/documents` API.

Verify each slice: pure chunker tests, ruff, py_compile (DB), esbuild (UI). DB/parse run on the user's PC.

---

## M3 — 3c Persona — PLAN (2026-06-12)

**Decisions (user):** preset + free-text control; personalize from profile (address by name, honor comms_style); default vibe = warm & concise "her". Single slice.

**Baseline:** `SYSTEM_PROMPT` is a fixed string with identity + capabilities + safety rules all hardcoded.

**Build:**
- Config: `assistant_name="Purple"`, `persona_tone="warm"` (warm|professional|playful|terse), `persona_style=""` (free-text override), `persona_use_profile=True`.
- `prompts.py`: split into a fixed CAPABILITIES + non-negotiable SAFETY block, plus `build_system_prompt(profile)` that composes: identity ("You are <name>…"), the tone preset, the free-text style (if any), and — when `persona_use_profile` — "address them as <name>; they prefer <comms_style>". Safety/capabilities stay constant; persona only shapes voice/identity.
- Orchestrator: build the prompt per turn from `await memory.get_profile()` instead of the static string.
- `config_api` EDITABLE += persona fields → they appear in the Settings tab automatically (no new UI needed).
- Spoken nudges stay short/literal (no per-alert LLM); they just use the configured name. Audible personality = the af_bella voice (already shipped).
- Verify: pure `build_system_prompt` tests (name substituted, tone preset present, free-text appended, profile address line, safety rules always present), ruff.

---

## M3 — 3d Speaker ID (REQUIRED voice access gate) — PLAN (2026-06-12)

**Decisions (user):** multiple registered voices may speak (you + trusted people, all explicitly enrolled); unknown voice → ignore + show "voice not recognized" in the UI feed (no spoken reply to strangers); enforce only once at least one voice is enrolled (can't lock yourself out; if the model is missing, voice works as today with a warning). Gate applies to the VOICE path only — typed chat is unaffected.

**Choke point:** `VoiceLoop.process_command(audio)` (wake-word + push-to-talk both flow through it) and the `/voice` upload endpoint.

### Slice 3d-1 — Speaker-ID provider + enrollment
- `purple/speaker.py`: local speaker embeddings via Resemblyzer (lazy import, graceful if absent). Pure `_match(score, threshold)`. `enroll(name, audio)`, `identify(audio) -> (name|None, score)`, `is_enrolled(audio) -> bool`, `has_enrollments()`.
- Voiceprint storage: a local file in models_dir (name → embedding[s]); `list_speakers`, `remove_speaker`.
- Config: `require_enrolled_voice=True` (gate on; enforced only when ≥1 enrolled), `speaker_threshold=0.75`.
- Optional dep extra `[speaker] = ["resemblyzer"]` (pulls torch).
- Tests: pure `_match` threshold; voiceprint store roundtrip + cosine match with fake embeddings.

### Slice 3d-2 — Gate the voice path + enroll UI
- In `process_command` + `/voice`: embed the clip, accept only if it matches an enrolled print (when enforcing); else emit `{voice: "not_recognized"}` to the feed and stop (no transcribe, no agent). Fail-open until enrolled / if model missing (with a one-time warning).
- Enroll flow: `/voice/enroll` (multipart audio + name) + a Voice/Enroll section in Settings (browser mic → record a few seconds → POST). `list/remove` enrolled voices in UI.
- selfcheck/SelfWatcher note when the gate is on but unavailable.
- Verify: gate decision tests (faked identify), ruff, esbuild (UI).

**Correction (2026-06-12) — fail posture for the lock (no silent fail-open):** the gate has THREE states, not "degrade gracefully":
1. Not enrolled yet → allow voice (can't lock yourself out before enrolling).
2. Enrolled + verifier works → enforce (only matched voices pass).
3. Enrolled + verifier missing/errors → **FAIL-CLOSED**: refuse all voice commands and warn loudly (toast + SelfWatcher + selfcheck FAIL). Never silently revert to open. Typing always still works, so the user is never stuck.
The optional-dependency "graceful" behavior applies ONLY to case 1 (pre-enrollment); once a voiceprint exists the lock is real and a broken verifier means deny, not allow.

---

## M4 — Real-time duplex voice — PLAN (2026-06-12)

**Decisions (user):** want all three — barge-in, faster (streaming) replies, hands-free continuous conversation; turns = continuous session after one wake until a quiet timeout; STT = chunked faster-whisper (local, no new dep). Speaker-ID gate still runs per utterance (only enrolled voices can talk/interrupt).

**Baseline:** half-duplex + turn-based — wake → record-until-silence → transcribe whole clip → agent (non-streaming) → synthesize whole reply → play; not interruptible; wake word every turn.

### Slice 4a — Streaming reply pipeline (lower latency)
- LLM token streaming: add `OllamaLLM.stream_chat()` (Ollama `stream=True`); Agent.respond gains a streaming path for the FINAL answer (tool-calling stays buffered).
- Pure `sentence_chunks(token_iter)` — accumulate tokens, emit on sentence boundaries (. ? ! newline) so TTS can start early. Unit-tested.
- TTS-as-you-go: synthesize each sentence with Kokoro and feed a **cancelable playback queue** (sounddevice), so audio starts within ~1s and can be stopped mid-stream (groundwork for barge-in).
- Verify: pure sentence chunker tests; playback queue cancel logic (faked).

### Slice 4b — Barge-in + conversation mode
- Barge-in: keep the mic monitoring while TTS plays; on VAD speech (above threshold, and only from an enrolled speaker) → cancel playback queue + capture the new utterance.
- Conversation mode: after wake, loop listen→reply→listen; return to wake-word sleep after `conversation_idle_timeout` of silence. config `conversation_mode`, idle timeout.
- Chunked STT: transcribe VAD-delimited segments for snappier turn-taking.
- Gate per utterance (existing speaker.authorize) so only you can interrupt/continue.
- Verify: barge-in decision + conversation-timeout logic (pure/faked); ruff.

Note: real mic/playback timing is verified on the user's PC (sandbox has no audio); pure logic (chunker, barge decision, timeout) is unit-tested here.

---

## M5 — Long-horizon autonomy — PLAN (2026-06-12)

**Decisions (user):** missions run in the BACKGROUND with progress reports; autonomy = confirm risky/money steps (reuse commit-confirm) + pause for approval at milestones; build SEQUENTIAL executor first, then add SUB-AGENTS that delegate down into the same sequential executor for larger/fan-out steps (don't skip sub-agents; design the Step seam for delegation). Reuses: agent+tools, scheduler/always-on service, M2 autonomy + safety, memory.

**Baseline:** orchestrator is single-turn (MAX_TOOL_ITERS=6); no planner / mission store / background jobs / sub-agents.

### Slice 5a — Planner + mission store + sequential executor
- LLM **planner**: goal → ordered steps (JSON: title + optional tool hint). Pure parse/validate (testable).
- `Mission` + `Step` models (Postgres): goal, status (planned/running/paused/blocked/done/failed/cancelled), step ordinals, per-step status + result, created/updated. Resumable across restart.
- **Sequential executor**: run steps in order, each via the agent/tools; record result; stop/persist on pause/block/fail. **Design the Step→execute seam so a step can later delegate to a sub-agent** (executor calls `run_step(step)` that today runs inline, later may spawn a sub-agent).
- Tools + API: start_mission(goal), mission_status, cancel_mission; /missions endpoints.
- Verify: pure plan parsing + step state-machine transitions (unit tests).

### Slice 5b — Background runner + guardrails + Missions UI
- Background job runner in the always-on service: missions execute off the request path; pause/resume/cancel; survive restart (resume from persisted step).
- Guardrails: risky/money steps → commit-confirm gate (existing); pause at milestone checkpoints for approval per autonomy (notify/confirm/act); per-mission step/budget cap; report progress via notifier + bus.
- Missions UI tab: live plan + step status, approve checkpoints, pause/cancel.
- Verify: checkpoint/guardrail decision logic (pure), esbuild UI.

### Slice 5c — Sub-agents (delegate into sequential)
- A step flagged "complex/fan-out" delegates to a sub-agent that runs its OWN sequential mini-plan via the same executor (recursion with depth limit). Specialized sub-agent prompts (research/booking/etc.). Results merge back into the parent step.
- Guardrails + persistence apply to sub-missions too. Verify: delegation decision + depth-limit (pure).

Note: long-running/background + audio is PC-verified; pure logic (planner parse, state machine, checkpoint/delegation decisions) unit-tested in sandbox.
