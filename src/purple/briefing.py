"""The morning briefing — built from real data and actually delivered.

Sources: due reminders (DB), live weather (Open-Meteo — free, no key), and headlines from
your RSS feeds. No LLM-invented "news". deliver() pushes it to the UI feed, a toast, and
(if your speaker can be heard) speaks it. Parsing is pure + unit-tested; the fetches are
best-effort (a failed source is skipped, not faked).
"""

from __future__ import annotations

import contextlib
from datetime import datetime
from typing import Any
import xml.etree.ElementTree as ET

from purple.config import settings
from purple.runtime import get_memory
from purple.utils.logging import get_logger

log = get_logger("briefing")

# A few WMO weather codes → words (Open-Meteo's current.weather_code).
_WMO = {
    0: "clear", 1: "mainly clear", 2: "partly cloudy", 3: "overcast", 45: "foggy",
    48: "foggy", 51: "light drizzle", 53: "drizzle", 61: "light rain", 63: "rain",
    65: "heavy rain", 71: "light snow", 73: "snow", 80: "rain showers", 95: "thunderstorms",
}


def parse_rss(xml_text: str, limit: int = 3) -> list[str]:
    """Headline titles from an RSS/Atom feed. Pure; tolerant of malformed feeds."""
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []
    titles: list[str] = []
    for item in root.iter():
        tag = item.tag.split("}")[-1]  # strip namespace
        if tag in ("item", "entry"):
            for child in item:
                if child.tag.split("}")[-1] == "title" and (child.text or "").strip():
                    titles.append(child.text.strip())
                    break
        if len(titles) >= limit:
            break
    return titles[:limit]


def weather_line(temperature_c: float, code: int) -> str:
    """Format current conditions. Pure."""
    desc = _WMO.get(int(code), "")
    temp = f"{round(temperature_c)}°C"
    return f"{temp}, {desc}" if desc else temp


async def _fetch_weather_context() -> dict[str, Any] | None:
    """Current conditions + the next few hours' codes (for storm heads-ups).

    Returns {"line": "21°C, light rain", "code": 61, "upcoming": [63, 65, ...]} or None.
    """
    if not settings.weather_location:
        return None
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": settings.weather_location, "count": 1},
            )
            results = (geo.json() or {}).get("results") or []
            if not results:
                return None
            lat, lon = results[0]["latitude"], results[0]["longitude"]
            fc = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,weather_code",
                    "hourly": "weather_code",
                    "forecast_days": 1,
                    "timezone": "auto",
                },
            )
            data = fc.json() or {}
            cur = data.get("current") or {}
            if "temperature_2m" not in cur:
                return None
            code = int(cur.get("weather_code", -1))
            hourly = (data.get("hourly") or {}).get("weather_code") or []
            start = min(datetime.now().hour + 1, len(hourly))  # from the next hour on
            upcoming = [int(c) for c in hourly[start : start + 6] if c is not None]
            return {
                "line": weather_line(cur["temperature_2m"], code),
                "code": code,
                "upcoming": upcoming,
            }
    except Exception as exc:
        log.warning("weather_fetch_failed", error=str(exc))
        return None


async def _fetch_weather() -> str | None:
    """Just the current-conditions line (used by the on-demand tool + scheduled briefing)."""
    ctx = await _fetch_weather_context()
    return ctx["line"] if ctx else None


async def _fetch_news(limit: int = 3) -> list[str]:
    headlines: list[str] = []
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            for feed in settings.news_feeds:
                try:
                    resp = await client.get(feed)
                    headlines += parse_rss(resp.text, limit)
                except Exception as exc:
                    log.warning("news_feed_failed", feed=feed, error=str(exc))
    except Exception as exc:
        log.warning("news_fetch_failed", error=str(exc))
    return headlines[:limit]


async def build_briefing(agent: Any | None = None) -> str:
    parts = [f"Good morning. Here's your briefing for {datetime.now():%A, %d %B %Y}."]

    try:
        memory = get_memory()
        due = await memory.due_reminders()
        rems = await memory.list_reminders()
    except Exception as exc:
        log.warning("briefing_memory_failed", error=str(exc))
        due, rems = [], []
    if due:
        parts.append("Due now: " + "; ".join(due))
    if rems:
        parts.append(f"You have {len(rems)} open reminder(s).")
    if not due and not rems:
        parts.append("Nothing due and no open reminders.")

    weather = await _fetch_weather()
    if weather:
        parts.append(f"Weather in {settings.weather_location}: {weather}.")

    news = await _fetch_news()
    if news:
        parts.append("Top headlines:\n" + "\n".join(f"- {h}" for h in news))

    return "\n".join(parts)


async def deliver(text: str) -> None:
    """Surface the briefing: UI feed + toast + speak (if it can be heard). Best-effort."""
    from purple import audio
    from purple.events import bus
    from purple.triggers import notify

    with contextlib.suppress(Exception):
        await bus.broadcast(
            {"type": "alert", "priority": "normal", "source": "briefing",
             "title": "Morning briefing", "detail": text}
        )
    with contextlib.suppress(Exception):
        await notify.toast("Morning briefing", text[:200])
    if audio.can_be_heard():
        with contextlib.suppress(Exception):
            await notify.speak(text)
