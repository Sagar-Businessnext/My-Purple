"""Pure-logic tests for the boot greeting, observe auto-off, usage and self-suggestions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from purple import greeting, observe, suggestions, usage

_UTC = UTC


_FIRST = lambda opts: opts[0]  # noqa: E731 — deterministic pick for tests


def test_greeting_line_by_time():
    assert "morning" in greeting.greeting_line(8, pick=_FIRST).lower()
    assert "afternoon" in greeting.greeting_line(14, pick=_FIRST).lower()
    assert "evening" in greeting.greeting_line(19, pick=_FIRST).lower()
    assert "late" in greeting.greeting_line(2, pick=_FIRST).lower()


def test_greeting_line_is_randomized():
    # All variants for a bucket are reachable; first and last differ.
    assert greeting.greeting_line(8, pick=lambda o: o[0]) != greeting.greeting_line(
        8, pick=lambda o: o[-1]
    )


def test_greeting_line_uses_name():
    line = greeting.greeting_line(8, "Abhishek", pick=_FIRST)
    assert "Abhishek" in line and ", Abhishek" in line


def test_should_show_weather():
    # Morning: always show.
    assert greeting.should_show_weather(8, 1, []) is True
    # Evening, calm now and ahead: don't show (no 8pm temperature noise).
    assert greeting.should_show_weather(20, 1, [2, 3]) is False
    # Evening but a thunderstorm right now: show.
    assert greeting.should_show_weather(20, 95, []) is True
    # Evening, calm now but heavy rain coming: show heads-up.
    assert greeting.should_show_weather(20, 1, [3, 65]) is True


def test_weather_sentence_phrasing():
    morning = greeting.weather_sentence(8, "24°C, clear", 0, [], "Pune")
    assert "right now" in morning and "Heads-up" not in morning
    now_severe = greeting.weather_sentence(20, "26°C, thunderstorms", 95, [], "Pune")
    assert now_severe.startswith("Heads-up")
    soon_severe = greeting.weather_sentence(20, "27°C, clear", 1, [65], "Pune")
    assert "expected later" in soon_severe


def test_observe_auto_off():
    now = datetime(2026, 6, 17, 12, 0, tzinfo=_UTC)
    assert observe.should_auto_off(None, now, 4) is False  # not on
    assert observe.should_auto_off(now - timedelta(hours=5), now, 4) is True  # past window
    assert observe.should_auto_off(now - timedelta(hours=1), now, 4) is False  # still inside
    assert observe.should_auto_off(now - timedelta(hours=99), now, 0) is False  # 0 = never


def test_derive_suggestions_threshold_and_order():
    counts = {"run_command": 12, "browser_open": 9, "list_notes": 50}
    out = suggestions.derive_suggestions(counts, min_uses=8, limit=2)
    assert len(out) == 2
    assert "12" in out[0]  # most-used escape hatch first
    assert all("list_notes" not in s for s in out)  # not an escape hatch → no suggestion


def test_derive_suggestions_below_threshold_is_empty():
    assert suggestions.derive_suggestions({"run_command": 3}, min_uses=8) == []


def test_usage_summarize_window_and_bad_rows():
    now = datetime(2026, 6, 17, 12, 0, tzinfo=_UTC)
    since = now - timedelta(days=7)
    events = [
        {"tool": "run_command", "at": (now - timedelta(days=1)).isoformat()},  # in window
        {"tool": "run_command", "at": (now - timedelta(days=30)).isoformat()},  # too old
        {"tool": "get_news", "at": (now - timedelta(hours=2)).isoformat()},  # in window
        {"tool": "broken"},  # malformed: no timestamp
        "not-a-dict",  # malformed row
    ]
    counts = usage.summarize_counts(events, since, now)
    assert counts == {"run_command": 1, "get_news": 1}
