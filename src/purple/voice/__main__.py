"""Run Purple in voice-only mode (no web server):

    python -m purple.voice

Say the wake word ("hey jarvis" by default), then speak your request. Needs a mic,
Ollama running, and the wake model downloaded on first run.
"""

from __future__ import annotations

import asyncio
import contextlib

from purple.agent.orchestrator import Agent
from purple.config import settings
from purple.llm.ollama_client import OllamaLLM
from purple.memory.db import init_db
from purple.memory.store import Memory
from purple.runtime import set_runtime
from purple.speech.base import get_speech_provider
from purple.tools import load_tools, registry
from purple.utils.logging import configure_logging
from purple.voice.loop import VoiceLoop


async def main() -> None:
    configure_logging(settings.log_level)
    settings.ensure_dirs()
    load_tools()

    llm = OllamaLLM()
    if not await llm.health():
        print("Ollama isn't reachable. Start it with `ollama serve` first.")
        return

    memory = None
    try:
        await init_db()
        memory = Memory(llm)
    except Exception as exc:
        print(f"(memory disabled — Postgres not reachable: {exc})")
    set_runtime(llm, memory)

    agent = Agent(llm, registry, memory)
    speech = get_speech_provider()

    async def emit(event: dict) -> None:
        print(event)

    loop = VoiceLoop(agent, speech, emit=emit)
    loop.start(asyncio.get_running_loop())
    print(f"Listening for '{settings.wake_model}'. Ctrl-C to stop.")
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        loop.stop()
        print("\nstopped.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
