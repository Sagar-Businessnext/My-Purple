"""The boot greeting — a short, time-aware hello when Purple starts.

Time shapes the opener (morning = offer to help, later = ask about the day) and it's picked
at random from a few variants so she doesn't say the exact same thing every time. Weather is
only volunteered in the MORNING — or, at any hour, as a heads-up when rough weather is current
or coming up in the next few hours (otherwise an 8pm temperature reading is just noise). The
news offer is shown any time (there are headlines around the clock). One self-suggestion may
be appended. Wording logic is pure + unit-tested; the fetches are best-effort.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import contextlib
from datetime import datetime
import random

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("greeting")

# {who} is "" or ", Name". Multiple variants per time bucket -> not the same line every boot.
_MORNING = (
    "Good morning{who}. What can I help you get done today?",
    "Morning{who}! What's first on the list today?",
    "Rise and shine{who} — what can I take off your plate today?",
    "Good morning{who}. Where would you like to start?",
)
_AFTERNOON = (
    "Good afternoon{who}. How's the day going so far?",
    "Hey{who} — how's your day shaping up?",
    "Afternoon{who}. What are we working on?",
    "Hi{who}. How's it going so far today?",
)
_EVENING = (
    "Good evening{who}. How was your day?",
    "Evening{who} — how did today go?",
    "Hey{who}, how was your day?",
    "Good evening{who}. How are you winding down?",
)
_NIGHT = (
    "Hi{who} — you're up late. Anything I can do for you?",
    "Burning the midnight oil{who}? How can I help?",
    "Still up{who}? What do you need?",
    "Late one{who} — what can I do for you?",
)

# WMO codes that warrant a heads-up at any hour (heavy rain/snow, freezing, thunderstorms).
SEVERE_CODES = frozenset({65, 67, 75, 77, 82, 85, 86, 95, 96, 99})


def _bucket(hour: int) -> Sequence[str]:
    if 5 <= hour < 12:
        return _MORNING
    if 12 <= hour < 17:
        return _AFTERNOON
    if 17 <= hour < 22:
        return _EVENING
    return _NIGHT


def greeting_line(
    hour: int, name: str | None = None, *, pick: Callable[[Sequence[str]], str] = random.choice
) -> str:
    """Pure: a random, time-appropriate opener. `hour` is the local 24h hour (0-23).

    `pick` is injectable so tests are deterministic (defaults to random.choice).
    """
    who = f", {name}" if name else ""
    return pick(_bucket(hour)).format(who=who)


def is_morning(hour: int) -> bool:
    return 5 <= hour < 12


def should_show_weather(hour: int, current_code: int, upcoming_codes: Sequence[int]) -> bool:
    """Pure: volunteer weather in the morning, or any time rough weather is here/coming."""
    if is_morning(hour):
        return True
    if current_code in SEVERE_CODES:
        return True
    return any(c in SEVERE_CODES for c in upcoming_codes)


def weather_sentence(
    hour: int, line: str, current_code: int, upcoming_codes: Sequence[int], location: str
) -> str:
    """Pure: phrase the weather. A plain morning report, or a heads-up when it's rough."""
    if current_code in SEVERE_CODES:
        return f"Heads-up — rough weather in {location} right now: {line}."
    if not is_morning(hour) and any(c in SEVERE_CODES for c in upcoming_codes):
        return f"Heads-up — rough weather expected later in {location} (currently {line})."
    return f"It's {line} in {location} right now."


async def _user_name() -> str | None:
    with contextlib.suppress(Exception):
        from purple.runtime import get_memory

        profile = await get_memory().get_profile()
        return (profile.get("name") or "").strip() or None
    return None


async def build_greeting() -> str:
    hour = datetime.now().hour
    name = await _user_name()
    parts = [greeting_line(hour, name)]

    with contextlib.suppress(Exception):
        from purple.briefing import _fetch_weather_context

        ctx = await _fetch_weather_context()
        if ctx and should_show_weather(hour, ctx["code"], ctx["upcoming"]):
            parts.append(
                weather_sentence(
                    hour, ctx["line"], ctx["code"], ctx["upcoming"], settings.weather_location
                )
            )

    parts.append("Want today's headlines? Just say 'news' and I'll pull them.")

    with contextlib.suppress(Exception):
        from purple import suggestions

        for tip in await suggestions.collect_suggestions(limit=1):
            parts.append(f"One thought: {tip}")

    return " ".join(parts)


async def deliver(text: str) -> None:
    """Surface the greeting: UI feed + toast + speak (if it can be heard). Best-effort."""
    from purple import audio
    from purple.events import bus
    from purple.triggers import notify

    with contextlib.suppress(Exception):
        await bus.broadcast(
            {"type": "alert", "priority": "normal", "source": "greeting",
             "title": "Purple is ready", "detail": text}
        )
    with contextlib.suppress(Exception):
        await notify.toast("Purple", text[:200])
    if audio.can_be_heard():
        with contextlib.suppress(Exception):
            await notify.speak(text)


async def greet_on_boot() -> None:
    """Build and deliver the startup greeting. Safe to fire-and-forget."""
    try:
        await deliver(await build_greeting())
        log.info("greeting_delivered")
    except Exception as exc:
        log.warning("greeting_failed", error=str(exc))
