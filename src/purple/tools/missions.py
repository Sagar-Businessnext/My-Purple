"""Mission tools — give Purple a goal and she plans + runs it in the background.

start_mission plans the goal into steps, persists the mission, and kicks off background
execution (steps run in order, persisted, resumable). Running missions use a deny-risky
approver, so nothing irreversible happens unattended (5b adds milestone approvals).
"""

from __future__ import annotations

import asyncio

from purple.autonomy.missions import MissionRunner, MissionStore
from purple.autonomy.plan import CANCELLED
from purple.runtime import get_agent
from purple.tools.registry import registry

_RUNNING: set[asyncio.Task] = set()  # hold refs so background tasks aren't GC'd


@registry.tool(
    name="start_mission",
    description="Give Purple a multi-step goal to plan and carry out in the background "
    "(e.g. 'research three laptops under 80k and draft a comparison'). She breaks it into "
    "steps and works them on her own; check progress with mission_status.",
    parameters={
        "type": "object",
        "properties": {"goal": {"type": "string", "description": "The goal to pursue."}},
        "required": ["goal"],
    },
)
async def start_mission(goal: str) -> str:
    runner = MissionRunner(get_agent())
    res = await runner.plan_and_create(goal)
    if not res.get("ok"):
        return res.get("error", "couldn't start that mission")
    mission_id = res["mission_id"]
    task = asyncio.create_task(runner.run_mission(mission_id))
    _RUNNING.add(task)
    task.add_done_callback(_RUNNING.discard)
    steps = "; ".join(f"{i + 1}. {s}" for i, s in enumerate(res["steps"]))
    return f"Mission #{mission_id} started ({len(res['steps'])} steps): {steps}"


@registry.tool(
    name="mission_status",
    description="Show a mission's plan and the status of each step.",
    parameters={
        "type": "object",
        "properties": {"mission_id": {"type": "integer", "description": "The mission's id."}},
        "required": ["mission_id"],
    },
)
async def mission_status(mission_id: int) -> dict | str:
    mission = await MissionStore().get(mission_id)
    return mission or f"No mission #{mission_id}."


@registry.tool(
    name="list_missions",
    description="List recent missions and their status.",
    parameters={"type": "object", "properties": {}, "required": []},
)
async def list_missions() -> list[dict] | str:
    missions = await MissionStore().list()
    return missions or "No missions yet."


@registry.tool(
    name="cancel_mission",
    description="Cancel a running mission by its id (stops before the next step).",
    parameters={
        "type": "object",
        "properties": {"mission_id": {"type": "integer", "description": "The mission's id."}},
        "required": ["mission_id"],
    },
)
async def cancel_mission(mission_id: int) -> str:
    store = MissionStore()
    if await store.mission_status(mission_id) is None:
        return f"No mission #{mission_id}."
    await store.set_mission_status(mission_id, CANCELLED)
    return f"Mission #{mission_id} cancelled — it'll stop before the next step."


@registry.tool(
    name="resume_mission",
    description="Approve and continue a mission that's paused/blocked waiting for your OK.",
    parameters={
        "type": "object",
        "properties": {"mission_id": {"type": "integer", "description": "The mission's id."}},
        "required": ["mission_id"],
    },
)
async def resume_mission(mission_id: int) -> str:
    runner = MissionRunner(get_agent())
    task = asyncio.create_task(runner.resume(mission_id))
    _RUNNING.add(task)
    task.add_done_callback(_RUNNING.discard)
    return f"Resuming mission #{mission_id}."
