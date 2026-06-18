"""Read/update Purple's configuration from the UI without touching code.

get_config() returns the editable settings (secrets masked). set_config() applies the
changes to the running settings object and persists them to the project ``.env`` so they
survive a restart. Some settings are read fresh at call time (require_confirmation,
auto_memory, vision_model) and take effect immediately; others are bound at startup and
are reported as needing a restart.
"""

from __future__ import annotations

from typing import Any

from purple.config import ROOT, settings

# Fields the UI may view/edit (non-secret).
EDITABLE = [
    "llm_model",
    "vision_model",
    "embed_model",
    "speech_provider",
    "whisper_model",
    "tts_engine",
    "kokoro_voice",
    "require_confirmation",
    "assistant_name",
    "persona_tone",
    "persona_style",
    "persona_use_profile",
    "autonomy",
    "vip_senders",
    "enable_triggers",
    "enable_self_watcher",
    "enable_phone_watchers",
    "download_dir",
    "cpu_high_pct",
    "ram_high_pct",
    "gpu_high_pct",
    "gpu_vram_high_pct",
    "enable_wake",
    "wake_model",
    "wake_threshold",
    "enable_scheduler",
    "briefing_hour",
    "briefing_minute",
    "weather_location",
    "enable_greeting",
    "observe_default",
    "observe_log_history",
    "observe_auto_off_hours",
    "auto_memory",
    "auto_memory_mode",
    "enable_tray",
    "enable_push_to_talk",
    "ptt_hotkey",
    "open_ui_on_start",
    "browser_headless",
    "browser_cdp_url",
    "ha_base_url",
    "host",
    "port",
]

# Secrets: settable but never returned in clear text.
SECRET = ["sarvam_api_key", "ha_token"]

# Settings bound at startup — changing them needs a restart to take effect.
RESTART_REQUIRED = {
    "llm_model",
    "embed_model",
    "host",
    "port",
    "enable_wake",
    "enable_tray",
    "enable_push_to_talk",
    "enable_scheduler",
    "enable_triggers",
    "enable_self_watcher",
    "enable_phone_watchers",
    "ptt_hotkey",
    "wake_model",
    "browser_cdp_url",
    "browser_headless",
}


def get_config() -> dict[str, Any]:
    out: dict[str, Any] = {k: getattr(settings, k) for k in EDITABLE}
    # Report secret presence, never the value.
    for k in SECRET:
        out[f"{k}_set"] = bool(getattr(settings, k))
    return out


def set_config(updates: dict[str, Any]) -> dict[str, Any]:
    applied: dict[str, Any] = {}
    for key, value in updates.items():
        if key in EDITABLE or key in SECRET:
            setattr(settings, key, value)  # live for settings read fresh each call
            applied[key] = value
    if applied:
        _merge_env(applied)
    return {
        "applied": sorted(applied),
        "restart_needed": sorted(k for k in applied if k in RESTART_REQUIRED),
    }


def _env_key(field: str) -> str:
    return "PURPLE_" + field.upper()


def _format(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _merge_env(updates: dict[str, Any]) -> None:
    """Merge updates into ROOT/.env, preserving existing lines/comments."""
    env_path = ROOT / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    wanted = {_env_key(k): _format(v) for k, v in updates.items()}
    seen: set[str] = set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key in wanted:
            lines[i] = f"{key}={wanted[key]}"
            seen.add(key)
    for key, val in wanted.items():
        if key not in seen:
            lines.append(f"{key}={val}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
