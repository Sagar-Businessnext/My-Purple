"""Thin async wrapper around the local Ollama server.

This is the ONLY place that talks to the model. Swapping models (or later swapping
to vLLM) means changing this file, nothing else.
"""

from __future__ import annotations

import time
from typing import Any

import ollama

from purple import observability as obs
from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("llm")


class OllamaLLM:
    def __init__(
        self,
        model: str | None = None,
        embed_model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model or settings.llm_model
        self.embed_model = embed_model or settings.embed_model
        self._client = ollama.AsyncClient(host=base_url or settings.ollama_base_url)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.4,
    ) -> dict[str, Any]:
        """Send a chat turn. Returns the assistant message dict, which may contain
        `tool_calls`. Tool schemas follow the OpenAI/Ollama function-calling format.
        """
        start = time.perf_counter()
        with obs.span("llm_chat", model=self.model):
            resp = await self._client.chat(
                model=self.model,
                messages=messages,
                tools=tools or None,
                options={"temperature": temperature},
            )
        obs.record_llm(self.model, time.perf_counter() - start)
        # ollama returns a ChatResponse (dict-like); normalise to a plain dict.
        msg = resp["message"] if isinstance(resp, dict) else resp.message
        return dict(msg) if not isinstance(msg, dict) else msg

    async def stream_chat(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.4,
    ) -> Any:
        """Yield assistant content tokens as they arrive (no tool-calling). Async generator
        for low-latency speaking — chunk the tokens into sentences and synthesize as you go."""
        start = time.perf_counter()
        stream = await self._client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": temperature},
            stream=True,
        )
        async for chunk in stream:
            msg = chunk["message"] if isinstance(chunk, dict) else chunk.message
            piece = (msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")) or ""
            if piece:
                yield piece
        obs.record_llm(self.model, time.perf_counter() - start)

    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for `text` using the local embedding model."""
        resp = await self._client.embeddings(model=self.embed_model, prompt=text)
        return list(resp["embedding"] if isinstance(resp, dict) else resp.embedding)

    async def health(self) -> bool:
        try:
            await self._client.list()
            return True
        except Exception as exc:
            log.warning("ollama_unreachable", error=str(exc))
            return False
