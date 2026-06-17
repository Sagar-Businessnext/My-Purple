"""Automation tool tests: the NL-managed add/list/toggle/remove backed by a fake store."""

from __future__ import annotations

import purple.tools.automations as auto


class FakeMem:
    def __init__(self) -> None:
        self.rules: dict[int, dict] = {}
        self._next = 1

    async def add_rule(
        self, name, keywords, source, min_priority, effect, action="", action_args=None
    ) -> int:
        rid = self._next
        self._next += 1
        self.rules[rid] = {
            "id": rid,
            "name": name,
            "keywords": keywords,
            "source": source,
            "min_priority": min_priority,
            "effect": effect,
            "enabled": True,
            "action": action,
            "action_args": action_args or {},
        }
        return rid

    async def list_rules_raw(self) -> list[dict]:
        return list(self.rules.values())

    async def set_rule_enabled(self, rid, enabled) -> bool:
        if rid not in self.rules:
            return False
        self.rules[rid]["enabled"] = enabled
        return True

    async def delete_rule(self, rid) -> bool:
        return self.rules.pop(rid, None) is not None


async def test_add_validates_effect(monkeypatch):
    monkeypatch.setattr(auto, "get_memory", lambda: FakeMem())
    out = await auto.add_automation("bad", effect="yell")
    assert "Unknown effect" in out


async def test_add_validates_priority(monkeypatch):
    monkeypatch.setattr(auto, "get_memory", lambda: FakeMem())
    out = await auto.add_automation("bad", effect="mute", min_priority="huge")
    assert "Unknown priority" in out


async def test_add_list_toggle_remove(monkeypatch):
    mem = FakeMem()
    monkeypatch.setattr(auto, "get_memory", lambda: mem)
    msg = await auto.add_automation("mute ads", effect="mute", keywords="sale, deal")
    assert "added" in msg
    assert mem.rules[1]["keywords"] == ["sale", "deal"]

    listed = await auto.list_automations()
    assert isinstance(listed, list) and listed[0]["name"] == "mute ads"

    assert "disabled" in await auto.toggle_automation(1, False)
    assert mem.rules[1]["enabled"] is False
    assert "No automation" in await auto.toggle_automation(99, True)

    assert "removed" in await auto.remove_automation(1)
    assert await auto.list_automations() == "No automations yet."
