"""Smart-home pure-helper tests: state parsing, entity domains, action→service mapping.
(Live Home Assistant calls are verified on the user's network once HA + a device exist.)"""

from __future__ import annotations

from purple import smarthome


def test_domain_of():
    assert smarthome.domain_of("light.kitchen") == "light"
    assert smarthome.domain_of("switch.fan") == "switch"
    assert smarthome.domain_of("nodots") == ""


def test_parse_states():
    raw = [
        {"entity_id": "light.kitchen", "state": "on", "attributes": {"friendly_name": "Kitchen"}},
        {"entity_id": "sensor.temp", "state": "21.5", "attributes": {}},
    ]
    out = smarthome.parse_states(raw)
    assert out[0] == {"entity_id": "light.kitchen", "name": "Kitchen", "state": "on", "domain": "light"}
    assert out[1]["name"] == "sensor.temp" and out[1]["domain"] == "sensor"
    assert smarthome.parse_states([]) == []


def test_action_to_service():
    assert smarthome.action_to_service("on") == "turn_on"
    assert smarthome.action_to_service("OFF") == "turn_off"
    assert smarthome.action_to_service("toggle") == "toggle"
    assert smarthome.action_to_service("explode") is None


def test_client_not_configured(monkeypatch):
    from purple.config import settings

    monkeypatch.setattr(settings, "ha_base_url", "")
    monkeypatch.setattr(settings, "ha_token", "")
    assert smarthome.HAClient().configured() is False
    monkeypatch.setattr(settings, "ha_base_url", "http://homeassistant.local:8123")
    monkeypatch.setattr(settings, "ha_token", "tok")
    assert smarthome.HAClient().configured() is True


async def test_control_rejects_bad_action(monkeypatch):
    from purple.config import settings

    monkeypatch.setattr(settings, "ha_base_url", "http://h:8123")
    monkeypatch.setattr(settings, "ha_token", "t")
    res = await smarthome.HAClient().control("light.kitchen", "explode")
    assert res["ok"] is False and "unknown action" in res["error"]
