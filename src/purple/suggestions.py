"""Self-suggestions — Purple notices her own usage patterns and proposes improvements.

This is the "self-learning" surface: rather than the developer deciding "you use Spotify a
lot, let's add a Spotify tool", Purple watches how she's actually being used (purple.usage)
plus her own configuration gaps, and raises those suggestions herself — in her own voice,
in the morning greeting/briefing. The pattern logic is pure and unit-tested; the live
collector layers in config-gap nudges that need the running settings.
"""

from __future__ import annotations

from typing import Any

from purple.utils.logging import get_logger

log = get_logger("suggestions")

# Generic escape-hatch tools: heavy use of these is the signal that a frequent task
# deserves a dedicated, more reliable tool (the "build a Spotify tool" insight).
_ESCAPE_HATCHES = {
    "run_command": (
        "I've fallen back on raw PowerShell commands {n} times in the last couple of weeks. "
        "If there's one app you have me drive often — music, a specific tool — I can build a "
        "dedicated, sturdier tool for it. Tell me which and I'll set it up."
    ),
    "browser_open": (
        "I've driven the web browser {n} times recently. If it's mostly one service (say a "
        "music or email site), wiring up its real API as a dedicated tool would be faster and "
        "less fragile than clicking the page. Want me to look into it?"
    ),
    "pc_ui": (
        "I've been clicking through app windows {n} times lately. If that's a recurring chore, "
        "an automation or a purpose-built tool would be a lot more reliable. Worth a look?"
    ),
}


def derive_suggestions(
    counts: dict[str, int], *, min_uses: int = 8, limit: int = 1
) -> list[str]:
    """Pure: from tool-use counts, propose improvements in Purple's voice. Most-used first."""
    out: list[tuple[int, str]] = []
    for tool, template in _ESCAPE_HATCHES.items():
        n = counts.get(tool, 0)
        if n >= min_uses:
            out.append((n, template.format(n=n)))
    out.sort(key=lambda x: -x[0])
    return [msg for _, msg in out[:limit]]


def _config_gap_suggestions(settings: Any) -> list[str]:
    """Nudges based on configuration that would unlock a feature. Needs live settings."""
    tips: list[str] = []
    if not settings.weather_location:
        tips.append(
            "Tell me your city (Settings → weather location) and I'll add a weather line to "
            "your morning briefing and greeting."
        )
    return tips


async def collect_suggestions(limit: int = 1) -> list[str]:
    """Live: usage-pattern suggestions first, then config-gap nudges. Best-effort, never raises."""
    suggestions: list[str] = []
    try:
        from purple import usage

        suggestions += derive_suggestions(usage.recent_counts(days=14), limit=limit)
    except Exception as exc:
        log.warning("usage_suggestions_failed", error=str(exc))
    try:
        from purple.config import settings

        suggestions += _config_gap_suggestions(settings)
    except Exception as exc:
        log.warning("config_suggestions_failed", error=str(exc))
    return suggestions[:limit] if limit else suggestions
