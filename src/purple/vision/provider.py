"""Vision provider — Purple's eyes.

Sends a screenshot plus a prompt to a local vision-language model (default
``qwen3-vl:8b``, which is purpose-built for GUI/screen grounding) through Ollama, and
returns the model's answer. Kept as a swappable singleton so the model is one config
change (``PURPLE_VISION_MODEL``) — e.g. bump to ``qwen3-vl:30b-a3b`` for more capability.
"""

from __future__ import annotations

from typing import Any

from purple.utils.logging import get_logger

log = get_logger("vision")


class VisionProvider:
    def __init__(self) -> None:
        self._client: Any | None = None

    @property
    def model(self) -> str:
        from purple.config import settings

        return settings.vision_model

    def _ensure(self) -> Any:
        if self._client is None:
            import ollama

            from purple.config import settings

            self._client = ollama.AsyncClient(host=settings.ollama_base_url)
        return self._client

    async def look(self, image: bytes, prompt: str) -> str:
        """Show the model an image and a question; return its textual answer."""
        client = self._ensure()
        resp = await client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt, "images": [image]}],
        )
        msg = resp["message"] if isinstance(resp, dict) else resp.message
        content = msg.get("content") if isinstance(msg, dict) else msg.content
        return (content or "").strip()


# Process-wide vision provider.
provider = VisionProvider()
