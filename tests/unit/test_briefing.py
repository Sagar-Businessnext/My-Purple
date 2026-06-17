"""Briefing + scheduler-catch-up pure tests: RSS parsing, weather formatting, overdue."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from purple import briefing, jobs

_RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>Feed</title>
  <item><title>First headline</title><link>x</link></item>
  <item><title>Second headline</title></item>
  <item><title>Third headline</title></item>
  <item><title>Fourth headline</title></item>
</channel></rss>"""


def test_parse_rss_limit_and_order():
    out = briefing.parse_rss(_RSS, limit=3)
    assert out == ["First headline", "Second headline", "Third headline"]


def test_parse_rss_bad_xml_is_empty():
    assert briefing.parse_rss("<not xml", limit=3) == []
    assert briefing.parse_rss("", limit=3) == []


def test_weather_line():
    assert briefing.weather_line(21.4, 61) == "21°C, light rain"
    assert briefing.weather_line(30.0, 0) == "30°C, clear"
    assert briefing.weather_line(25.0, 999) == "25°C"  # unknown code → temp only


def test_is_overdue():
    now = datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
    assert jobs.is_overdue(None, 86400, now) is True  # never ran
    assert jobs.is_overdue(now - timedelta(hours=25), 86400, now) is True  # >1 day
    assert jobs.is_overdue(now - timedelta(hours=2), 86400, now) is False  # ran recently
