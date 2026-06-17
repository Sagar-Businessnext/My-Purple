"""Terminal chat with Purple — the fastest way to test the brain + tools without a UI.

    python -m purple.cli

Risky tools prompt for confirmation right in the terminal.
"""

from __future__ import annotations

import asyncio

from purple.agent.orchestrator import Agent
from purple.config import settings
from purple.llm.ollama_client import OllamaLLM
from purple.memory.db import init_db
from purple.memory.store import Memory
from purple.runtime import set_runtime
from purple.tools import load_tools, registry
from purple.tools.permissions import console_approver
from purple.utils.logging import configure_logging


async def main() -> None:
    configure_logging(settings.log_level)
    settings.ensure_dirs()
    load_tools()

    llm = OllamaLLM()
    if not await llm.health():
        print("Ollama isn't reachable. Start it with `ollama serve` and pull the model first.")
        return

    memory: Memory | None
    try:
        await init_db()
        memory = Memory(llm)
    except Exception as exc:
        print(f"(memory disabled — Postgres not reachable: {exc})")
        memory = None

    set_runtime(llm, memory)
    agent = Agent(llm, registry, memory)
    history: list[dict[str, str]] = []
    print("Purple CLI ready. Type a message, or Ctrl-C to exit.\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            return
        if not user:
            continue
        reply = await agent.respond(user, history=history, approver=console_approver)
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": reply})
        print(f"\npurple> {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())
