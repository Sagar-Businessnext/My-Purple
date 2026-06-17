"""Smart-home tools — list and control devices through Home Assistant (local).

Needs PURPLE_HA_BASE_URL + PURPLE_HA_TOKEN set (Settings). With nothing configured these
report that smart home isn't set up, rather than failing.
"""

from __future__ import annotations

from purple.smarthome import get_ha
from purple.tools.registry import registry


@registry.tool(
    name="list_devices",
    description="List the smart-home devices/entities Home Assistant knows about "
    "(lights, switches, sensors, etc.), with their current state.",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def list_devices() -> list[dict] | str:
    ha = get_ha()
    if not ha.configured():
        return "Smart home isn't set up yet — add your Home Assistant URL + token in Settings."
    entities = await ha.list_entities()
    return entities or "No devices found (is Home Assistant reachable?)."


@registry.tool(
    name="control_device",
    description="Turn a smart-home device on or off (or toggle) by its Home Assistant "
    "entity id, e.g. 'light.kitchen'. action is on | off | toggle.",
    parameters={
        "type": "object",
        "properties": {
            "entity_id": {"type": "string", "description": "HA entity id, e.g. light.kitchen."},
            "action": {"type": "string", "description": "on | off | toggle."},
        },
        "required": ["entity_id", "action"],
    },
)
async def control_device(entity_id: str, action: str) -> str:
    ha = get_ha()
    if not ha.configured():
        return "Smart home isn't set up yet — add your Home Assistant URL + token in Settings."
    res = await ha.control(entity_id.strip(), action)
    if not res.get("ok"):
        return res.get("error", f"couldn't {action} {entity_id}")
    return f"Done — {action} {entity_id}."
