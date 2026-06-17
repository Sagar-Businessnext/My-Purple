"""Persona / system-prompt composition tests — pure (args override settings)."""

from __future__ import annotations

from purple.agent import prompts


def test_name_substituted():
    p = prompts.build_system_prompt(name="Jarvis", tone="warm", style="", use_profile=False)
    assert "You are Jarvis," in p


def test_tone_presets_and_fallback():
    assert "extremely terse" in prompts.build_system_prompt(name="P", tone="terse", style="", use_profile=False)
    assert "businesslike" in prompts.build_system_prompt(name="P", tone="professional", style="", use_profile=False)
    # unknown tone falls back to warm
    assert "warm" in prompts.build_system_prompt(name="P", tone="???", style="", use_profile=False).lower()


def test_free_text_style_appended():
    p = prompts.build_system_prompt(name="P", tone="warm", style="Speak like a calm pilot.", use_profile=False)
    assert "Speak like a calm pilot." in p


def test_profile_personalization():
    profile = {"name": "Abhishek", "comms_style": "concise, no fluff"}
    p = prompts.build_system_prompt(profile, name="P", tone="warm", style="", use_profile=True)
    assert "Address the user as Abhishek." in p
    assert "concise, no fluff" in p


def test_profile_ignored_when_disabled():
    profile = {"name": "Abhishek"}
    p = prompts.build_system_prompt(profile, name="P", tone="warm", style="", use_profile=False)
    assert "Abhishek" not in p


def test_safety_and_capabilities_always_present():
    p = prompts.build_system_prompt(name="P", tone="playful", style="be silly", use_profile=False)
    # the non-negotiable rules survive any persona
    assert "confirm" in p and "irreversible" in p
    assert "Capabilities:" in p
