"""Live first-run self-check.

Unlike doctor.py (static environment probing), this exercises each subsystem against
the real services: it actually chats with Ollama, round-trips a fact through
PostgreSQL + pgvector, loads the tool registry, and inspects the speech config.

Run it after setup:  ``purple-selfcheck``  (or ``python -m purple.selfcheck``).
It prints PASS / WARN / FAIL per subsystem and exits non-zero if anything is broken,
so it's the first thing to run on a new machine — and the output to paste back if not.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from purple.config import settings

OK = "[ OK ]"
WARN = "[WARN]"
FAIL = "[FAIL]"


@dataclass
class Result:
    status: str
    name: str
    detail: str = ""


def render(results: list[Result]) -> str:
    """Format results into a readable report with a one-line summary."""
    lines = [f"{r.status}  {r.name}" + (f" — {r.detail}" if r.detail else "") for r in results]
    fails = sum(r.status == FAIL for r in results)
    warns = sum(r.status == WARN for r in results)
    if fails:
        summary = f"{fails} blocker(s) and {warns} warning(s) — fix blockers before running Purple."
    elif warns:
        summary = f"No blockers, {warns} warning(s) — Purple will run; address warnings for full function."
    else:
        summary = "All systems go — Purple is ready."
    return "\n".join(lines) + "\n\n" + summary


async def check_llm() -> list[Result]:
    from purple.llm.ollama_client import OllamaLLM

    llm = OllamaLLM()
    if not await llm.health():
        return [
            Result(
                FAIL, "Ollama", f"not reachable at {settings.ollama_base_url} — run `ollama serve`"
            )
        ]
    out = [Result(OK, "Ollama", f"reachable at {settings.ollama_base_url}")]
    try:
        msg = await llm.chat([{"role": "user", "content": "reply with the single word OK"}])
        text = (msg.get("content") or "").strip()
        out.append(Result(OK, f"LLM chat ({settings.llm_model})", f"responded: {text[:40]!r}"))
    except Exception as exc:
        out.append(
            Result(
                FAIL,
                f"LLM chat ({settings.llm_model})",
                f"{exc} — is the model pulled? `ollama pull {settings.llm_model}`",
            )
        )
    try:
        vec = await llm.embed("selfcheck")
        ok = len(vec) == settings.embed_dim
        out.append(
            Result(
                OK if ok else WARN,
                f"Embeddings ({settings.embed_model})",
                f"dim={len(vec)}" + ("" if ok else f" (expected {settings.embed_dim})"),
            )
        )
    except Exception as exc:
        out.append(
            Result(
                FAIL,
                f"Embeddings ({settings.embed_model})",
                f"{exc} — `ollama pull {settings.embed_model}`",
            )
        )
    return out


async def check_db() -> list[Result]:
    from purple.llm.ollama_client import OllamaLLM
    from purple.memory.db import init_db
    from purple.memory.store import Memory

    try:
        await init_db()
    except Exception as exc:
        return [
            Result(
                FAIL,
                "PostgreSQL + pgvector",
                f"{exc} — check the DB exists and `CREATE EXTENSION vector;` was run",
            )
        ]
    out = [Result(OK, "PostgreSQL + pgvector", "connected; schema ready")]
    try:
        mem = Memory(OllamaLLM())
        await mem.remember("selfcheck: the user ran a self-check", kind="selfcheck")
        hits = await mem.recall("self-check", limit=3)
        out.append(
            Result(OK if hits else WARN, "Memory round-trip", f"recalled {len(hits)} fact(s)")
        )
    except Exception as exc:
        out.append(Result(WARN, "Memory round-trip", f"{exc} (needs embeddings working)"))
    return out


async def check_tools() -> Result:
    try:
        from purple.tools import load_tools, registry

        load_tools()
        return Result(OK, "Tool registry", f"{len(registry.schemas())} tools loaded")
    except Exception as exc:
        return Result(FAIL, "Tool registry", str(exc))


def check_speech() -> list[Result]:
    out = [Result(OK, "Speech provider", settings.speech_provider)]
    if settings.speech_provider == "local":
        kdir = settings.models_dir / "kokoro"
        onnx = kdir / "kokoro-v1.0.onnx"
        out.append(
            Result(OK, f"Kokoro voice ({settings.kokoro_voice})", str(kdir))
            if onnx.exists()
            else Result(WARN, "Kokoro voice", f"model files missing in {kdir} — run setup.ps1")
        )
        out.append(Result(OK, "Whisper", f"model '{settings.whisper_model}' loads on first use"))
    elif not settings.sarvam_api_key:
        out.append(Result(FAIL, "Sarvam", "PURPLE_SARVAM_API_KEY not set"))
    return out


async def run() -> int:
    settings.ensure_dirs()
    results: list[Result] = []
    results += await check_llm()
    results += await check_db()
    results.append(await check_tools())
    results += check_speech()
    print("Purple self-check\n" + "=" * 40)
    print(render(results))
    return 1 if any(r.status == FAIL for r in results) else 0


def main() -> None:
    raise SystemExit(asyncio.run(run()))


if __name__ == "__main__":
    main()
