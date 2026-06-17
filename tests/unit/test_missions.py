"""Mission tests: pure planning/state (plan.py) + the sequential executor loop with a
fake in-memory store + fake agent (no DB, no LLM)."""

from __future__ import annotations

from typing import Any

from purple.autonomy import plan
from purple.autonomy.missions import MissionRunner
from purple.config import settings


def test_parse_plan_json():
    out = plan.parse_plan('Here you go: ["Research laptops", "Compare specs", "Draft table"]')
    assert out == ["Research laptops", "Compare specs", "Draft table"]


def test_parse_plan_numbered_and_bulleted():
    assert plan.parse_plan("1. First\n2) Second\n- Third\n* Fourth") == [
        "First", "Second", "Third", "Fourth"
    ]
    assert plan.parse_plan("   ") == []


def test_planning_prompt_has_goal_and_json():
    p = plan.planning_prompt("book a trip")
    assert "book a trip" in p and "JSON array" in p


def test_next_pending():
    assert plan.next_pending(["done", "pending", "pending"]) == 1
    assert plan.next_pending(["done", "done"]) is None


def test_mission_outcome():
    assert plan.mission_outcome([]) == plan.DONE
    assert plan.mission_outcome(["done", "skipped"]) == plan.DONE
    assert plan.mission_outcome(["done", "failed", "pending"]) == plan.FAILED
    assert plan.mission_outcome(["done", "pending"]) == plan.RUNNING


class FakeStore:
    def __init__(self, goal: str, steps: list[str]) -> None:
        self.goal = goal
        self.steps = [
            {"id": i, "ordinal": i, "title": t, "status": "pending", "result": ""}
            for i, t in enumerate(steps)
        ]
        self._status = "planned"

    async def get(self, _mid: int) -> dict[str, Any]:
        return {"id": 1, "goal": self.goal, "status": self._status, "steps": self.steps}

    async def set_mission_status(self, _mid: int, status: str) -> None:
        self._status = status

    async def mission_status(self, _mid: int) -> str:
        return self._status

    async def pending_step(self, _mid: int) -> dict[str, Any] | None:
        for st in self.steps:
            if st["status"] == "pending":
                return {"id": st["id"], "ordinal": st["ordinal"], "title": st["title"]}
        return None

    async def set_step(self, sid: int, status: str, result: str | None = None) -> None:
        for st in self.steps:
            if st["id"] == sid:
                st["status"] = status
                if result is not None:
                    st["result"] = result

    async def step_statuses(self, _mid: int) -> list[str]:
        return [st["status"] for st in self.steps]


class FakeLLM:
    def __init__(self, subplan: str = "") -> None:
        self.subplan = subplan
        self.chats = 0

    async def chat(self, _messages: Any) -> dict:
        self.chats += 1
        return {"content": self.subplan}


class FakeAgent:
    def __init__(self, fail_on: str | None = None, on_step: Any = None, subplan: str = "") -> None:
        self.llm = FakeLLM(subplan)
        self.fail_on = fail_on
        self.on_step = on_step
        self.calls: list[str] = []

    async def respond(self, prompt: str, approver: Any = None) -> str:
        self.calls.append(prompt)
        if self.on_step:
            self.on_step()
        if self.fail_on and self.fail_on in prompt:
            raise RuntimeError("step blew up")
        return "did it"


async def test_run_mission_happy_path():
    store = FakeStore("ship it", ["a", "b", "c"])
    agent = FakeAgent()
    status = await MissionRunner(agent, store).run_mission(1)
    assert status == plan.DONE
    assert [s["status"] for s in store.steps] == ["done", "done", "done"]
    assert len(agent.calls) == 3 and store._status == plan.DONE


async def test_run_mission_stops_on_failure():
    store = FakeStore("ship it", ["a", "boom", "c"])
    status = await MissionRunner(FakeAgent(fail_on="boom"), store).run_mission(1)
    assert status == plan.FAILED
    assert [s["status"] for s in store.steps] == ["done", "failed", "pending"]


async def test_run_mission_cancel_midway():
    store = FakeStore("ship it", ["a", "b", "c"])

    def _cancel_after_first() -> None:
        if store.steps[0]["status"] in ("running", "done"):
            store._status = plan.CANCELLED

    status = await MissionRunner(FakeAgent(on_step=_cancel_after_first), store).run_mission(1)
    assert status == plan.CANCELLED
    assert store.steps[2]["status"] == "pending"  # never reached the last step


def test_needs_checkpoint():
    assert plan.needs_checkpoint("Research laptops", "act") is False
    assert plan.needs_checkpoint("Send the email to the boss", "act") is True
    assert plan.needs_checkpoint("Research laptops", "confirm") is True


async def test_run_mission_blocks_at_checkpoint(monkeypatch):
    monkeypatch.setattr(settings, "autonomy", "confirm")
    store = FakeStore("g", ["a", "b"])
    agent = FakeAgent()
    status = await MissionRunner(agent, store).run_mission(1)
    assert status == plan.BLOCKED and store._status == "blocked"
    assert agent.calls == []  # paused before the first step, nothing ran


async def test_resume_runs_one_then_blocks(monkeypatch):
    monkeypatch.setattr(settings, "autonomy", "confirm")
    store = FakeStore("g", ["a", "b"])
    agent = FakeAgent()
    runner = MissionRunner(agent, store)
    await runner.run_mission(1)  # blocks at a
    await runner.resume(1)  # approve a → run it → block at b
    assert store.steps[0]["status"] == "done" and store.steps[1]["status"] == "pending"
    assert len(agent.calls) == 1 and store._status == "blocked"


async def test_act_runs_until_commit_step(monkeypatch):
    monkeypatch.setattr(settings, "autonomy", "act")
    store = FakeStore("g", ["research options", "compare them", "send the email"])
    agent = FakeAgent()
    status = await MissionRunner(agent, store).run_mission(1)
    assert status == plan.BLOCKED  # ran the two safe steps, paused at the commit step
    assert [s["status"] for s in store.steps] == ["done", "done", "pending"]
    assert len(agent.calls) == 2


def test_is_complex_step_and_should_delegate():
    assert plan.is_complex_step("research and compare three laptops") is True
    assert plan.is_complex_step("say hi") is False
    assert plan.should_delegate(0, 1, True) is True
    assert plan.should_delegate(1, 1, True) is False  # depth limit
    assert plan.should_delegate(0, 1, False) is False  # not complex


async def test_run_step_delegates_complex(monkeypatch):
    monkeypatch.setattr(settings, "mission_max_depth", 1)
    agent = FakeAgent(subplan='["fetch specs", "summarize"]')
    result = await MissionRunner(agent)._run_step("buy a laptop", "research and compare laptops", 0)
    assert "sub-agent handled" in result
    assert agent.llm.chats == 1  # planned sub-steps once; no deeper recursion at depth 1
    assert len(agent.calls) == 2  # the two sub-steps ran inline at depth 1


async def test_run_step_no_delegate_when_simple(monkeypatch):
    monkeypatch.setattr(settings, "mission_max_depth", 1)
    agent = FakeAgent(subplan='["x", "y"]')
    result = await MissionRunner(agent)._run_step("g", "say hi", 0)
    assert result == "did it"
    assert agent.llm.chats == 0 and len(agent.calls) == 1  # ran inline, never planned sub-steps
