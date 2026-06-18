"""FastAPI app — wires the agent, memory, speech and tools together.

Endpoints:
  GET  /health   -> liveness + Ollama status
  POST /chat     -> text in, text out (safe tools auto-run; risky ones auto-declined)
  WS   /ws       -> interactive chat WITH live confirmation for risky tools
  POST /voice    -> upload audio -> transcript + spoken reply (base64 WAV)
"""

from __future__ import annotations

import asyncio
import base64
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from pathlib import Path
import tempfile

from fastapi import FastAPI, File, Form, Request, Response, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from purple.agent.orchestrator import Agent
from purple.config import settings
from purple.events import bus
from purple.llm.ollama_client import OllamaLLM
from purple.memory.db import init_db
from purple.memory.store import Memory
from purple.runtime import set_runtime
from purple.scheduler import shutdown_scheduler, start_scheduler
from purple.speech.base import get_speech_provider
from purple.tools import load_tools, registry
from purple.tools.permissions import auto_deny
from purple.utils.logging import configure_logging, get_logger
from purple.voice.loop import VoiceLoop

log = get_logger("app")


class ChatIn(BaseModel):
    message: str
    session_id: str = "default"


async def _safe_history(memory: Memory, session_id: str) -> list[dict[str, str]]:
    try:
        return await memory.load_history(session_id)
    except Exception:
        return []


async def _safe_save(memory: Memory, session_id: str, role: str, content: str) -> None:
    with suppress(Exception):
        await memory.save_message(session_id, role, content)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.log_level)
    settings.ensure_dirs()
    import time

    app.state.started_at = time.time()
    from purple import observability as obs

    obs.setup_tracing()
    load_tools()
    app.state.llm = OllamaLLM()
    app.state.memory = Memory(app.state.llm)
    app.state.agent = Agent(app.state.llm, registry, app.state.memory, emit=bus.broadcast)
    app.state.speech = get_speech_provider()
    set_runtime(app.state.llm, app.state.memory, app.state.agent)
    app.state.missions = set()  # holds background mission tasks so they aren't GC'd

    async def _resume_missions() -> None:
        from purple.autonomy.missions import MissionRunner, MissionStore

        for mid in await MissionStore().list_running():
            task = asyncio.create_task(MissionRunner(app.state.agent).run_mission(mid))
            app.state.missions.add(task)
            task.add_done_callback(app.state.missions.discard)

    try:
        await init_db()
        await _resume_missions()  # pick up missions interrupted by a restart
    except Exception as exc:
        log.warning("db_init_failed", error=str(exc), hint="chat works, memory disabled")
    if settings.enable_scheduler:
        start_scheduler(app.state.agent)
    loop = asyncio.get_running_loop()
    app.state.voice = VoiceLoop(app.state.agent, app.state.speech, emit=bus.broadcast)
    app.state.voice.main_loop = loop
    if settings.enable_wake:
        app.state.voice.start(loop)
    app.state.ptt = None
    if settings.enable_push_to_talk:
        from purple.desktop.hotkey import PushToTalk

        app.state.ptt = PushToTalk(settings.ptt_hotkey, app.state.voice.push_to_talk)
        app.state.ptt.start()
    app.state.tray = None
    if settings.enable_tray:
        import webbrowser

        from purple.desktop.tray import Tray

        app.state.tray = Tray(on_open=lambda: webbrowser.open(settings.ui_url))
        app.state.tray.start()
    app.state.triggers = None
    if settings.enable_triggers:
        from purple.triggers.engine import TriggerEngine

        app.state.triggers = TriggerEngine()
        app.state.triggers.start()
    if settings.observe_default:
        from purple import observe

        observe.set_observing(True)
    app.state.greeting_task = None
    if settings.enable_greeting:
        from purple import greeting

        app.state.greeting_task = asyncio.create_task(greeting.greet_on_boot())
    if settings.open_ui_on_start:
        import threading
        import webbrowser

        # Open after a short delay so the server is accepting connections first.
        threading.Timer(1.5, lambda: webbrowser.open(settings.ui_url)).start()
    log.info(
        "purple_ready",
        model=settings.llm_model,
        speech=settings.speech_provider,
        tools=len(registry.schemas()),
        wake=settings.enable_wake,
        scheduler=settings.enable_scheduler,
    )
    yield
    app.state.voice.stop()
    if app.state.ptt is not None:
        app.state.ptt.stop()
    if app.state.tray is not None:
        app.state.tray.stop()
    if app.state.triggers is not None:
        app.state.triggers.stop()
    shutdown_scheduler()


app = FastAPI(title="Purple", version="0.1.0", lifespan=lifespan)

# Allow the Tauri webview / Vite dev server (localhost) to call the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^(https?://localhost(:\d+)?|https?://127\.0\.0\.1(:\d+)?|tauri://localhost|https://tauri\.localhost)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def _auth(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Require X-Purple-Token for non-localhost requests when an api_token is set."""
    from fastapi.responses import JSONResponse

    client = request.client.host if request.client else ""
    local = client in ("127.0.0.1", "::1", "localhost", "testclient")
    if settings.api_token and not local and request.headers.get("X-Purple-Token") != settings.api_token:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)


# --- Web UI: the React app, built by Vite into web/ and served here at /ui/ ---
_WEB_DIR = (Path(__file__).resolve().parent / "web").resolve()
_UI_PLACEHOLDER = (
    "<!doctype html><meta charset='utf-8'><title>Purple</title>"
    "<body style='font-family:system-ui;background:#0e0b1a;color:#ece9fb;padding:40px'>"
    "<h1>Purple's UI isn't built yet</h1>"
    "<p>Run <code>setup.ps1</code>, or build it manually:</p>"
    "<pre>cd frontend\nnpm install\nnpm run build</pre>"
    "<p>The API is live in the meantime at <a style='color:#a78bfa' href='/docs'>/docs</a>.</p>"
    "</body>"
)


def _serve_web(rel: str) -> Response:
    """Serve a file from the built web/ dir; SPA-fallback to index.html; placeholder if unbuilt."""
    from fastapi.responses import FileResponse, HTMLResponse

    target = (_WEB_DIR / rel).resolve()
    if (target == _WEB_DIR or _WEB_DIR in target.parents) and target.is_file():
        return FileResponse(str(target))
    index = _WEB_DIR / "index.html"
    if index.is_file():
        return FileResponse(str(index))  # SPA fallback for client-side routes
    return HTMLResponse(_UI_PLACEHOLDER)


@app.get("/")
async def _root() -> Response:
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/ui/")


@app.get("/ui", include_in_schema=False)
async def _ui_root() -> Response:
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/ui/")  # trailing slash so relative asset paths resolve


@app.get("/ui/", include_in_schema=False)
async def _ui_index() -> Response:
    return _serve_web("index.html")


@app.get("/ui/{path:path}", include_in_schema=False)
async def _ui_asset(path: str) -> Response:
    return _serve_web(path)


async def _db_ok() -> bool:
    from sqlalchemy import text

    from purple.memory.db import engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@app.get("/health")
async def health() -> dict:
    ollama_up = await app.state.llm.health()
    db_up = await _db_ok()
    return {
        "ok": ollama_up,
        "ollama": ollama_up,
        "model": settings.llm_model,
        "database": db_up,
        "speech_provider": settings.speech_provider,
        "vision_model": settings.vision_model,
        "wake_enabled": settings.enable_wake,
        "scheduler_enabled": settings.enable_scheduler,
        "tools": len(registry.schemas()),
        "tool_names": [s["function"]["name"] for s in registry.schemas()],
    }


@app.get("/config")
async def config_get() -> dict:
    from purple.config_api import get_config

    return get_config()


@app.post("/config")
async def config_set(updates: dict) -> dict:
    from purple.config_api import set_config

    return set_config(updates)


# --- Automations (user-defined notification rules; the UI's Automations tab) ---
@app.get("/automations")
async def automations_list() -> dict:
    from purple.runtime import get_memory

    return {"rules": await get_memory().list_rules_raw()}


@app.post("/automations")
async def automations_add(rule: dict) -> dict:
    from purple.runtime import get_memory
    from purple.triggers.engine import request_rules_reload

    kw = rule.get("keywords") or []
    if isinstance(kw, str):
        kw = [k.strip() for k in kw.split(",") if k.strip()]
    args = rule.get("action_args") or {}
    if isinstance(args, str):
        import json

        try:
            args = json.loads(args) if args.strip() else {}
        except ValueError:
            args = {}
    rid = await get_memory().add_rule(
        name=rule.get("name", "rule"),
        keywords=kw,
        source=rule.get("source", ""),
        min_priority=rule.get("min_priority", "normal"),
        effect=rule.get("effect", "notify"),
        action=rule.get("action", ""),
        action_args=args,
    )
    request_rules_reload()
    return {"id": rid}


@app.patch("/automations/{rule_id}")
async def automations_toggle(rule_id: int, body: dict) -> dict:
    from purple.runtime import get_memory
    from purple.triggers.engine import request_rules_reload

    ok = await get_memory().set_rule_enabled(rule_id, bool(body.get("enabled", True)))
    request_rules_reload()
    return {"ok": ok}


@app.delete("/automations/{rule_id}")
async def automations_delete(rule_id: int) -> dict:
    from purple.runtime import get_memory
    from purple.triggers.engine import request_rules_reload

    ok = await get_memory().delete_rule(rule_id)
    request_rules_reload()
    return {"ok": ok}


# --- Memory (the Memory tab: what Purple knows about you) ---
@app.get("/memory")
async def memory_overview() -> dict:
    from purple.runtime import get_memory

    mem = get_memory()
    return {
        "profile": await mem.get_profile(),
        "people": await mem.list_entities("person"),
        "facts": await mem.list_facts(limit=100),
        "auto_memory": settings.auto_memory,
        "auto_memory_mode": settings.auto_memory_mode,
    }


@app.get("/memory/search")
async def memory_search(q: str) -> dict:
    from purple.runtime import get_memory

    return {"facts": await get_memory().search_facts(q, limit=30)}


@app.post("/memory/fact")
async def memory_fact_add(body: dict) -> dict:
    from purple.runtime import get_memory

    text = (body.get("text") or "").strip()
    if not text:
        return {"ok": False, "error": "empty"}
    await get_memory().remember(text, kind=body.get("category", "fact"))
    return {"ok": True}


@app.patch("/memory/fact/{fact_id}")
async def memory_fact_update(fact_id: int, body: dict) -> dict:
    from purple.runtime import get_memory

    return {"ok": await get_memory().update_fact(fact_id, (body.get("text") or "").strip())}


@app.delete("/memory/fact/{fact_id}")
async def memory_fact_delete(fact_id: int) -> dict:
    from purple.runtime import get_memory

    return {"ok": await get_memory().forget_fact(fact_id)}


@app.post("/memory/profile")
async def memory_profile_set(body: dict) -> dict:
    from purple.runtime import get_memory

    key = (body.get("key") or "").strip().lower().replace(" ", "_")
    if not key:
        return {"ok": False, "error": "empty key"}
    await get_memory().set_profile(key, (body.get("value") or "").strip())
    return {"ok": True}


@app.delete("/memory/person/{entity_id}")
async def memory_person_delete(entity_id: int) -> dict:
    from purple.runtime import get_memory

    return {"ok": await get_memory().delete_entity(entity_id)}


# --- Knowledge base (the Knowledge section: documents Purple has learned) ---
@app.get("/documents")
async def documents_list() -> dict:
    from purple.runtime import get_memory

    return {"documents": await get_memory().list_documents()}


@app.post("/documents/ingest")
async def documents_ingest(body: dict) -> dict:
    from pathlib import Path

    from purple.runtime import get_memory

    path = (body.get("path") or "").strip()
    if not path:
        return {"ok": False, "error": "no path"}
    mem = get_memory()
    if Path(path).expanduser().is_dir():
        return await mem.ingest_folder(path, force=bool(body.get("force")))
    return await mem.ingest_file(path, force=bool(body.get("force")))


@app.get("/documents/search")
async def documents_search(q: str) -> dict:
    from purple.runtime import get_memory

    return {"hits": await get_memory().search_documents(q, k=5)}


@app.delete("/documents/{document_id}")
async def documents_delete(document_id: int) -> dict:
    from purple.runtime import get_memory

    return {"ok": await get_memory().remove_document(document_id)}


# --- Missions (long-horizon autonomy; the Missions tab) ---
@app.get("/missions")
async def missions_list() -> dict:
    from purple.autonomy.missions import MissionStore

    return {"missions": await MissionStore().list()}


@app.get("/missions/{mission_id}")
async def mission_get(mission_id: int) -> dict:
    from purple.autonomy.missions import MissionStore

    m = await MissionStore().get(mission_id)
    return m or {"error": "not found"}


@app.post("/missions")
async def mission_start(body: dict) -> dict:
    import asyncio

    from purple.autonomy.missions import MissionRunner
    from purple.runtime import get_agent

    goal = (body.get("goal") or "").strip()
    if not goal:
        return {"ok": False, "error": "no goal"}
    runner = MissionRunner(get_agent())
    res = await runner.plan_and_create(goal)
    if res.get("ok"):
        task = asyncio.create_task(runner.run_mission(res["mission_id"]))
        app.state.missions.add(task)
        task.add_done_callback(app.state.missions.discard)
    return res


@app.delete("/missions/{mission_id}")
async def mission_cancel(mission_id: int) -> dict:
    from purple.autonomy.missions import MissionStore
    from purple.autonomy.plan import CANCELLED

    store = MissionStore()
    if await store.mission_status(mission_id) is None:
        return {"ok": False, "error": "not found"}
    await store.set_mission_status(mission_id, CANCELLED)
    return {"ok": True}


@app.post("/missions/{mission_id}/resume")
async def mission_resume(mission_id: int) -> dict:
    import asyncio

    from purple.autonomy.missions import MissionRunner
    from purple.runtime import get_agent

    runner = MissionRunner(get_agent())
    task = asyncio.create_task(runner.resume(mission_id))
    app.state.missions.add(task)
    task.add_done_callback(app.state.missions.discard)
    return {"ok": True}


@app.get("/metrics")
async def metrics() -> Response:
    from purple import observability as obs

    payload, content_type = obs.metrics_text()
    return Response(content=payload, media_type=content_type)


@app.get("/metrics/summary")
async def metrics_summary() -> dict:
    from purple import observability as obs

    return obs.metrics_summary()


@app.get("/logs")
async def logs(n: int = 100) -> dict:
    from pathlib import Path

    path = Path(settings.log_dir) / "purple.log"
    if not path.exists():
        return {"lines": []}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"lines": lines[-n:]}


@app.get("/status")
async def status() -> dict:
    import os
    import time

    from purple import __version__, focus

    started = getattr(app.state, "started_at", time.time())
    return {
        "version": __version__,
        "pid": os.getpid(),
        "uptime_seconds": round(time.time() - started, 1),
        "focus": focus.state(),
    }


@app.get("/system")
async def system_stats() -> dict:
    """Live host stats for the Monitor charts (percent 0-100). Best-effort."""
    import psutil

    from purple import gpu

    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    g: dict = {}
    try:
        g = gpu.status()
    except Exception:
        g = {}
    return {
        "cpu": round(cpu, 1),
        "ram": round(ram, 1),
        "gpu": round(float(g.get("util", 0) or 0), 1),
        "vram": round(float(g.get("vram_pct", 0) or 0), 1),
    }


@app.get("/focus")
async def focus_get() -> dict:
    from purple import focus

    return focus.state()


@app.post("/focus")
async def focus_set(body: dict) -> dict:
    from purple import focus

    focus.set_focus(bool(body.get("on")))
    return focus.state()


# --- Screen-context observation (privacy toggle; off by default) ---
@app.get("/observe")
async def observe_get() -> dict:
    from purple import observe

    return observe.status()


@app.post("/observe")
async def observe_set(body: dict) -> dict:
    from purple import observe

    observe.set_observing(bool(body.get("on")))
    return observe.status()


@app.get("/suggestions")
async def suggestions_get() -> dict:
    from purple import suggestions

    return {"suggestions": await suggestions.collect_suggestions(limit=3)}


@app.post("/chat")
async def chat(body: ChatIn) -> dict:
    from purple import observability as obs

    obs.record_request("chat")
    memory: Memory = app.state.memory
    agent: Agent = app.state.agent
    history = await _safe_history(memory, body.session_id)
    await _safe_save(memory, body.session_id, "user", body.message)
    reply = await agent.respond(
        body.message, history=history, approver=auto_deny, session_id=body.session_id
    )
    await _safe_save(memory, body.session_id, "assistant", reply)
    with suppress(Exception):
        await memory.maybe_summarize(body.session_id)  # refresh rolling summary periodically
    return {"reply": reply}


@app.websocket("/ws")
async def ws(websocket: WebSocket) -> None:
    """Interactive chat. When a risky tool fires, the server sends
    {"type":"confirm_request",...} and waits for {"approved": true/false}."""
    await websocket.accept()
    bus.register(websocket)  # also receive live voice/activity events
    agent: Agent = app.state.agent

    async def approver(tool_name: str, args: dict) -> bool:
        await websocket.send_json({"type": "confirm_request", "tool": tool_name, "args": args})
        resp = await websocket.receive_json()
        return bool(resp.get("approved"))

    try:
        while True:
            data = await websocket.receive_json()
            if "message" not in data:
                continue  # stray confirm reply outside a tool call; ignore
            await websocket.send_json({"type": "status", "state": "thinking"})
            reply = await agent.respond(data["message"], approver=approver)
            # Display-stream the reply word-by-word for a live feel, then the full message.
            from purple.voice.streaming import word_groups

            for chunk in word_groups(reply):
                await websocket.send_json({"type": "reply_chunk", "text": chunk})
            await websocket.send_json({"type": "reply", "reply": reply})
    except WebSocketDisconnect:
        return
    finally:
        bus.unregister(websocket)


@app.post("/voice")
async def voice(file: UploadFile = File(...)) -> dict:
    speech = app.state.speech
    agent: Agent = app.state.agent
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    from purple import speaker

    gate = await asyncio.to_thread(speaker.authorize_file, path)
    if not gate["allow"]:  # only enrolled voices may command Purple
        return {"transcript": "", "reply": "", "audio_base64": "", "not_recognized": gate["reason"]}

    transcript = await speech.transcribe(path)
    reply = await agent.respond(transcript, approver=auto_deny)
    audio = await speech.synthesize(reply)
    return {
        "transcript": transcript,
        "reply": reply,
        "audio_base64": base64.b64encode(audio).decode() if audio else "",
    }


@app.post("/voice/enroll")
async def voice_enroll(name: str = Form(...), file: UploadFile = File(...)) -> dict:
    from purple import speaker

    if not speaker.available():
        return {"ok": False, "error": "speaker model not installed — pip install '.[speaker]'"}
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        n = await asyncio.to_thread(speaker.enroll_file, name.strip(), path)
        return {"ok": True, "name": name.strip(), "samples": n}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.get("/voice/voices")
async def voice_voices() -> dict:
    from purple import speaker

    return {
        "voices": speaker.list_speakers(),
        "available": speaker.available(),
        "enforced": settings.require_enrolled_voice and speaker.has_enrollments(),
    }


@app.delete("/voice/voices/{name}")
async def voice_remove(name: str) -> dict:
    from purple import speaker

    return {"ok": speaker.remove_speaker(name)}
