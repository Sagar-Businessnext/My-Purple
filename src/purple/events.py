"""A tiny async pub/sub for pushing live events to connected WebSocket UI clients.

The voice loop and agent emit events (Purple woke, heard you, replied); every open
UI socket receives them so the desktop app can reflect what's happening.
"""

from __future__ import annotations

from typing import Any, Protocol


class _Sender(Protocol):
    async def send_json(self, data: dict[str, Any]) -> None: ...


class EventBus:
    def __init__(self) -> None:
        self._clients: set[_Sender] = set()

    def register(self, client: _Sender) -> None:
        self._clients.add(client)

    def unregister(self, client: _Sender) -> None:
        self._clients.discard(client)

    async def broadcast(self, event: dict[str, Any]) -> None:
        dead: list[_Sender] = []
        for client in list(self._clients):
            try:
                await client.send_json(event)
            except Exception:
                dead.append(client)
        for client in dead:
            self._clients.discard(client)


# Process-wide bus.
bus = EventBus()
