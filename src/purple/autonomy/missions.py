"""Mission persistence + the sequential executor.

MissionStore is the DB boundary (imports SQLAlchemy lazily, so MissionRunner stays
testable without a database). MissionRunner plans a goal, then runs its steps in order
through the agent, persisting after each so a mission resumes across restarts. _run_step
is the seam where a sub-agent will later take over a step (M5c).

Unattended execution uses a DENY-RISKY approver: a running mission can never auto-confirm
an irreversible / money-spending tool (5b adds milestone check-ins to approve them).
Pure planning/state logic lives in plan.py.
"""

from __future__ import annotations

from typing import Any

from purple.autonomy import plan
from purple.utils.logging import get_logger

log = get_logger("missions")


async def _decline_risky(_name: str, _args: dict) -> bool:
    return False  # unattended mission: never auto-approve a high-risk tool


class MissionStore:
    """Postgres-backed mission/step storage. DB imports are lazy (per method)."""

    async def create(self, goal: str, steps: list[str]) -> int:
        from purple.memory.db import async_session
        from purple.memory.models import Mission, Step

        async with async_session() as s:
            mission = Mission(goal=goal, status=plan.PLANNED)
            s.add(mission)
            await s.flush()
            for i, title in enumerate(steps):
                s.add(Step(mission_id=mission.id, ordinal=i, title=title, status=plan.S_PENDING))
            await s.commit()
            return mission.id

    async def get(self, mission_id: int) -> dict[str, Any] | None:
        from sqlalchemy import select

        from purple.memory.db import async_session
        from purple.memory.models import Mission, Step

        async with async_session() as s:
            mission = await s.get(Mission, mission_id)
            if mission is None:
                return None
            rows = await s.execute(
                select(Step).where(Step.mission_id == mission_id).order_by(Step.ordinal)
            )
            steps = [
                {"id": st.id, "ordinal": st.ordinal, "title": st.title,
                 "status": st.status, "result": st.result}
                for st in rows.scalars().all()
            ]
            return {"id": mission.id, "goal": mission.goal, "status": mission.status, "steps": steps}

    async def list(self, limit: int = 20) -> list[dict[str, Any]]:
        from sqlalchemy import select

        from purple.memory.db import async_session
        from purple.memory.models import Mission

        async with async_session() as s:
            rows = await s.execute(select(Mission).order_by(Mission.created_at.desc()).limit(limit))
            return [{"id": m.id, "goal": m.goal, "status": m.status} for m in rows.scalars().all()]

    async def set_mission_status(self, mission_id: int, status: str) -> None:
        from purple.memory.db import async_session
        from purple.memory.models import Mission

        async with async_session() as s:
            mission = await s.get(Mission, mission_id)
            if mission is not None:
                mission.status = status
                await s.commit()

    async def mission_status(self, mission_id: int) -> str | None:
        from purple.memory.db import async_session
        from purple.memory.models import Mission

        async with async_session() as s:
            mission = await s.get(Mission, mission_id)
            return mission.status if mission else None

    async def set_step(self, step_id: int, status: str, result: str | None = None) -> None:
        from purple.memory.db import async_session
        from purple.memory.models import Step

        async with async_session() as s:
            step = await s.get(Step, step_id)
            if step is not None:
                step.status = status
                if result is not None:
                    step.result = result[:4000]
                await s.commit()

    async def step_statuses(self, mission_id: int) -> list[str]:
        from sqlalchemy import select

        from purple.memory.db import async_session
        from purple.memory.models import Step

        async with async_session() as s:
            rows = await s.execute(
                select(Step).where(Step.mission_id == mission_id).order_by(Step.ordinal)
            )
            return [st.status for st in rows.scalars().all()]

    async def pending_step(self, mission_id: int) -> dict[str, Any] | None:
        from sqlalchemy import select

        from purple.memory.db import async_session
        from purple.memory.models import Step

        async with async_session() as s:
            rows = await s.execute(
                select(Step).where(Step.mission_id == mission_id).order_by(Step.ordinal)
            )
            for st in rows.scalars().all():
                if st.status == plan.S_PENDING:
                    return {"id": st.id, "ordinal": st.ordinal, "title": st.title}
            return None

    async def list_running(self) -> list[int]:
        """Mission ids left in 'running' (e.g. interrupted by a restart) — to resume."""
        from sqlalchemy import select

        from purple.memory.db import async_session
        from purple.memory.models import Mission

        async with async_session() as s:
            rows = await s.execute(select(Mission).where(Mission.status == plan.RUNNING))
            return [m.id for m in rows.scalars().all()]

    async def remove(self, mission_id: int) -> bool:
        from sqlalchemy import delete

        from purple.memory.db import async_session
        from purple.memory.models import Mission, Step

        async with async_session() as s:
            mission = await s.get(Mission, mission_id)
            if mission is None:
                return False
            await s.execute(delete(Step).where(Step.mission_id == mission_id))
            await s.delete(mission)
            await s.commit()
            return True


class MissionRunner:
    def __init__(self, agent: Any, store: MissionStore | None = None) -> None:
        self.agent = agent
        self.store = store or MissionStore()

    async def plan_and_create(self, goal: str) -> dict[str, Any]:
        """Ask the LLM for a plan and persist the mission (status: planned)."""
        try:
            msg = await self.agent.llm.chat(
                [{"role": "user", "content": plan.planning_prompt(goal)}]
            )
            steps = plan.parse_plan(msg.get("content") or "")
        except Exception as exc:
            log.warning("plan_failed", error=str(exc))
            steps = []
        if not steps:
            return {"ok": False, "error": "couldn't plan that goal"}
        mission_id = await self.store.create(goal, steps)
        return {"ok": True, "mission_id": mission_id, "steps": steps}

    def _step_prompt(self, mission_goal: str, title: str, depth: int) -> str:
        role = "a focused sub-agent" if depth else "Purple"
        return (
            f"You are {role} working on the mission: {mission_goal}\n"
            f"Do just this step now and report the result concisely: {title}"
        )

    async def _run_step(self, mission_goal: str, title: str, depth: int = 0) -> str:
        """Execute one step. A complex/fan-out step is DELEGATED to a sub-agent that runs
        its own mini-plan through this same executor (depth-limited recursion); otherwise
        it runs inline via the agent. This is the M5c sub-agent seam."""
        from purple.config import settings

        if plan.should_delegate(depth, settings.mission_max_depth, plan.is_complex_step(title)):
            delegated = await self._delegate(mission_goal, title, depth)
            if delegated is not None:
                return delegated
        return await self.agent.respond(
            self._step_prompt(mission_goal, title, depth), approver=_decline_risky
        )

    async def _delegate(self, mission_goal: str, title: str, depth: int) -> str | None:
        """Plan a complex step into sub-steps and run each via a sub-agent. Returns the
        merged result, or None to fall back to running the step inline."""
        try:
            msg = await self.agent.llm.chat(
                [{"role": "user", "content": plan.planning_prompt(title)}]
            )
            subs = plan.parse_plan(msg.get("content") or "")
        except Exception as exc:
            log.warning("subplan_failed", error=str(exc))
            return None
        if len(subs) < 2:  # not worth a sub-agent — just run it inline
            return None
        log.info("delegating", step=title, substeps=len(subs), depth=depth)
        lines = []
        for sub in subs:
            result = await self._run_step(f"{mission_goal} → {title}", sub, depth + 1)
            lines.append(f"- {sub}: {result}")
        return f"(sub-agent handled '{title}')\n" + "\n".join(lines)

    async def _notify(self, text: str) -> None:
        try:
            from purple.events import bus

            await bus.broadcast(
                {"type": "alert", "priority": "normal", "source": "mission",
                 "title": text, "detail": ""}
            )
        except Exception as exc:
            log.warning("mission_notify_failed", error=str(exc))

    async def run_mission(self, mission_id: int, approve_step_id: int | None = None) -> str:
        """Run pending steps in order, persisting after each. Resumable; pauses (BLOCKED)
        at a checkpoint for your approval per the autonomy setting; stops on cancel,
        failure, or completion. `approve_step_id` pre-approves one step (used by resume)."""
        from purple.config import settings

        mission = await self.store.get(mission_id)
        if mission is None:
            return "missing"
        await self.store.set_mission_status(mission_id, plan.RUNNING)
        while True:
            if await self.store.mission_status(mission_id) == plan.CANCELLED:
                return plan.CANCELLED
            step = await self.store.pending_step(mission_id)
            if step is None:
                break
            if step["id"] != approve_step_id and plan.needs_checkpoint(
                step["title"], settings.autonomy
            ):
                await self.store.set_mission_status(mission_id, plan.BLOCKED)
                await self._notify(f"Mission #{mission_id} paused for your OK: {step['title']}")
                return plan.BLOCKED
            approve_step_id = None  # the pre-approved step is consumed
            await self.store.set_step(step["id"], plan.S_RUNNING)
            try:
                result = await self._run_step(mission["goal"], step["title"])
                await self.store.set_step(step["id"], plan.S_DONE, result)
            except Exception as exc:
                log.warning("step_failed", step=step["title"], error=str(exc))
                await self.store.set_step(step["id"], plan.S_FAILED, str(exc))
            if plan.mission_outcome(await self.store.step_statuses(mission_id)) == plan.FAILED:
                await self.store.set_mission_status(mission_id, plan.FAILED)
                await self._notify(f"Mission #{mission_id} hit a problem and stopped.")
                return plan.FAILED
        await self.store.set_mission_status(mission_id, plan.DONE)
        await self._notify(f"Mission #{mission_id} is done.")
        return plan.DONE

    async def resume(self, mission_id: int) -> str:
        """Approve the currently-blocked step and continue the mission."""
        step = await self.store.pending_step(mission_id)
        if step is None:
            await self.store.set_mission_status(mission_id, plan.DONE)
            return plan.DONE
        return await self.run_mission(mission_id, approve_step_id=step["id"])
