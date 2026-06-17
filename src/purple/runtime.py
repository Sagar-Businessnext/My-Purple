"""Tiny service-locator so tools can reach shared singletons (llm, memory) without
each tool needing them passed in. The app (and CLI/tests) call set_runtime() once
at startup; tools call get_memory() / get_llm() when they run.
"""

from __future__ import annotations

from typing import Any

_llm: Any | None = None
_memory: Any | None = None
_agent: Any | None = None


def set_runtime(llm: Any, memory: Any, agent: Any | None = None) -> None:
    global _llm, _memory, _agent
    _llm, _memory = llm, memory
    if agent is not None:
        _agent = agent


def set_agent(agent: Any) -> None:
    global _agent
    _agent = agent


def get_llm() -> Any:
    if _llm is None:
        raise RuntimeError("runtime not initialised — call set_runtime() at startup")
    return _llm


def get_memory() -> Any:
    if _memory is None:
        raise RuntimeError("memory not available (database not connected)")
    return _memory


def get_agent() -> Any:
    if _agent is None:
        raise RuntimeError("agent not available — call set_runtime()/set_agent() at startup")
    return _agent
