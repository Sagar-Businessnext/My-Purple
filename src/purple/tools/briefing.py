"""Briefing tools — give the agent real, current weather/news/briefing data.

The morning greeting offers headlines; when the user says "yes" / "news", the agent needs a
way to fetch the *actual* current headlines rather than inventing them (a local model can't
know today's news). These tools expose the same real sources the scheduled briefing uses:
Open-Meteo for weather, the configured RSS feeds for news.
"""

from __future__ import annotations

from purple.tools.registry import registry


@registry.tool(
    name="get_weather",
    description=(
        "Get the current weather for the user's configured location (Open-Meteo, live). Use "
        "this for 'what's the weather', not your own guess. Returns a short conditions string."
    ),
    parameters={"type": "object", "properties": {}},
)
async def get_weather() -> dict:
    from purple.briefing import _fetch_weather
    from purple.config import settings

    line = await _fetch_weather()
    if not line:
        return {
            "ok": False,
            "message": (
                "No weather location is set. Ask the user for their city and save it in "
                "Settings → weather location."
            ),
        }
    return {"ok": True, "location": settings.weather_location, "weather": line}


@registry.tool(
    name="get_news",
    description=(
        "Fetch today's real top headlines from the user's configured news feeds (RSS, live). "
        "Use this whenever the user asks for news/headlines — never invent headlines yourself."
    ),
    parameters={
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "how many headlines (default 5)"}
        },
    },
)
async def get_news(limit: int = 5) -> dict:
    from purple.briefing import _fetch_news

    headlines = await _fetch_news(limit=max(1, min(limit, 10)))
    if not headlines:
        return {"ok": False, "message": "Couldn't reach the news feeds right now."}
    return {"ok": True, "headlines": headlines}


@registry.tool(
    name="morning_briefing",
    description=(
        "Build the full briefing on demand (reminders due + weather + headlines), the same "
        "one delivered each morning. Use when the user asks for 'my briefing' / 'catch me up'."
    ),
    parameters={"type": "object", "properties": {}},
)
async def morning_briefing() -> dict:
    from purple.briefing import build_briefing

    return {"ok": True, "briefing": await build_briefing()}
