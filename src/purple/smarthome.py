"""Smart-home control via Home Assistant (M6 foundation).

Home Assistant is the local-first, vendor-neutral hub: it runs on your own network and
fronts almost every brand/protocol (Hue, Matter, Zigbee, …) behind one local REST API,
so Purple integrates once instead of with a dozen clouds. Configure PURPLE_HA_BASE_URL +
PURPLE_HA_TOKEN (a long-lived access token). httpx is imported lazily; everything is
best-effort and degrades to "not configured" with no devices.

The parsing + action→service mapping is pure and unit-tested; the live calls are verified
on the user's network once Home Assistant + a device exist.
"""

from __future__ import annotations

from typing import Any

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("smarthome")

_ACTION_SERVICE = {"on": "turn_on", "off": "turn_off", "toggle": "toggle"}


def domain_of(entity_id: str) -> str:
    """'light.kitchen' -> 'light'. Pure."""
    return entity_id.split(".", 1)[0] if "." in (entity_id or "") else ""


def parse_states(states: list[dict]) -> list[dict[str, Any]]:
    """Simplify HA's /api/states payload into {entity_id, name, state, domain}. Pure."""
    out: list[dict[str, Any]] = []
    for s in states or []:
        eid = s.get("entity_id", "")
        attrs = s.get("attributes", {}) or {}
        out.append(
            {
                "entity_id": eid,
                "name": attrs.get("friendly_name") or eid,
                "state": s.get("state", ""),
                "domain": domain_of(eid),
            }
        )
    return out


def action_to_service(action: str) -> str | None:
    """Map a plain action to an HA service: on→turn_on, off→turn_off, toggle→toggle. Pure."""
    return _ACTION_SERVICE.get((action or "").lower().strip())


class HAClient:
    def configured(self) -> bool:
        return bool(settings.ha_base_url and settings.ha_token)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {settings.ha_token}", "Content-Type": "application/json"}

    async def list_entities(self) -> list[dict[str, Any]]:
        if not self.configured():
            return []
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{settings.ha_base_url.rstrip('/')}/api/states", headers=self._headers()
                )
                resp.raise_for_status()
                return parse_states(resp.json())
        except Exception as exc:
            log.warning("ha_list_failed", error=str(exc))
            return []

    async def call_service(self, domain: str, service: str, entity_id: str) -> bool:
        if not self.configured():
            return False
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{settings.ha_base_url.rstrip('/')}/api/services/{domain}/{service}",
                    headers=self._headers(),
                    json={"entity_id": entity_id},
                )
                resp.raise_for_status()
                return True
        except Exception as exc:
            log.warning("ha_service_failed", domain=domain, service=service, error=str(exc))
            return False

    async def control(self, entity_id: str, action: str) -> dict[str, Any]:
        service = action_to_service(action)
        if not service:
            return {"ok": False, "error": f"unknown action '{action}' (use on/off/toggle)"}
        domain = domain_of(entity_id)
        if not domain:
            return {"ok": False, "error": f"bad entity id '{entity_id}'"}
        ok = await self.call_service(domain, service, entity_id)
        return {"ok": ok, "entity_id": entity_id, "action": action}


_ha = HAClient()


def get_ha() -> HAClient:
    return _ha
