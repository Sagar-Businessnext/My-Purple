"""Automation rules Purple can manage by voice — "mute newsletters", "always tell me
when my boss emails", "when a download finishes, open the folder". Rules reshape
notifications (speak / mute / notify) and may optionally run a tool; whether that tool
actually runs is governed by the autonomy setting (notify/confirm/act), and high-risk
tools are never run unattended. Editable in the Automations UI tab; backed by Postgres."""

from __future__ import annotations

import json

from purple.runtime import get_memory
from purple.tools.registry import registry
from purple.triggers.engine import request_rules_reload
from purple.triggers.priority import _ORDER
from purple.triggers.rules import EFFECTS


@registry.tool(
    name="add_automation",
    description=(
        "Create an automation rule. effect 'speak' = always give a gentle spoken nudge "
        "(even during games/quiet hours); 'mute' = never notify; 'notify' = normal. "
        "keywords match the event text (comma-separated, blank = any). source filters by "
        "watcher (email, call, message, calendar, system, download; blank = any). "
        "min_priority is low|normal|important. Optionally run a tool when matched via "
        "'action' (a tool name) + 'action_args' (JSON); whether it runs depends on the "
        "autonomy setting."
    ),
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "A short label for the rule."},
            "effect": {"type": "string", "description": "speak | mute | notify"},
            "keywords": {"type": "string", "description": "Comma-separated terms to match."},
            "source": {"type": "string", "description": "Watcher source filter (optional)."},
            "min_priority": {"type": "string", "description": "low | normal | important."},
            "action": {"type": "string", "description": "Optional tool to run when matched."},
            "action_args": {"type": "string", "description": "Optional JSON args for the tool."},
        },
        "required": ["name", "effect"],
    },
)
async def add_automation(
    name: str,
    effect: str,
    keywords: str = "",
    source: str = "",
    min_priority: str = "normal",
    action: str = "",
    action_args: str = "",
) -> str:
    if effect not in EFFECTS:
        return f"Unknown effect '{effect}'. Use one of: {', '.join(EFFECTS)}."
    if min_priority not in _ORDER:
        return f"Unknown priority '{min_priority}'. Use low, normal, or important."
    args: dict = {}
    if action_args.strip():
        try:
            args = json.loads(action_args)
        except ValueError:
            return 'action_args must be valid JSON (e.g. {"text": "hi"}).'
    kws = [k.strip() for k in keywords.split(",") if k.strip()]
    rule_id = await get_memory().add_rule(
        name, kws, source.strip(), min_priority, effect, action.strip(), args
    )
    request_rules_reload()
    suffix = f" + run {action}" if action.strip() else ""
    return f"Automation #{rule_id} '{name}' added: {effect}{suffix} when matching {kws or 'anything'}."


@registry.tool(
    name="list_automations",
    description="List the user's notification automation rules.",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def list_automations() -> list[dict] | str:
    rules = await get_memory().list_rules_raw()
    return rules or "No automations yet."


@registry.tool(
    name="toggle_automation",
    description="Turn an automation rule on or off by its id.",
    parameters={
        "type": "object",
        "properties": {
            "rule_id": {"type": "integer", "description": "The automation's id."},
            "enabled": {"type": "boolean", "description": "true to enable, false to disable."},
        },
        "required": ["rule_id", "enabled"],
    },
)
async def toggle_automation(rule_id: int, enabled: bool) -> str:
    ok = await get_memory().set_rule_enabled(rule_id, enabled)
    if not ok:
        return f"No automation #{rule_id}."
    request_rules_reload()
    return f"Automation #{rule_id} {'enabled' if enabled else 'disabled'}."


@registry.tool(
    name="remove_automation",
    description="Delete an automation rule by its id.",
    parameters={
        "type": "object",
        "properties": {"rule_id": {"type": "integer", "description": "The automation's id."}},
        "required": ["rule_id"],
    },
)
async def remove_automation(rule_id: int) -> str:
    ok = await get_memory().delete_rule(rule_id)
    if not ok:
        return f"No automation #{rule_id}."
    request_rules_reload()
    return f"Automation #{rule_id} removed."
