"""Pure auto-memory helper tests (no DB / LLM): modes, categories, dedup, profile, prompt."""

from __future__ import annotations

from purple.memory import extract


def test_mode_params_scale_up():
    assert extract.mode_params("moderate")["max_facts"] < extract.mode_params("high")["max_facts"]
    assert extract.mode_params("high")["max_facts"] < extract.mode_params("aggressive")["max_facts"]


def test_normalize_mode_falls_back():
    assert extract.normalize_mode("aggressive") == "aggressive"
    assert extract.normalize_mode("nonsense") == "moderate"


def test_normalize_category():
    assert extract.normalize_category("preference") == "preference"
    assert extract.normalize_category("weird") == "fact"


def test_split_aliases():
    assert extract.split_aliases("Bob, Bobby ,  ") == ["Bob", "Bobby"]
    assert extract.split_aliases("") == []


def test_is_duplicate():
    assert extract.is_duplicate(0.95) is True
    assert extract.is_duplicate(0.80) is False


def test_profile_summary_orders_common_keys_first():
    summary = extract.profile_summary(
        {"comms_style": "concise", "name": "Abhishek", "location": "Kolkata", "hobby": "chess"}
    )
    # name before location before comms_style; unknown keys (hobby) last
    assert summary.index("name:") < summary.index("location:") < summary.index("comms style:")
    assert "hobby:" in summary
    assert extract.profile_summary({}) == ""


def test_extraction_prompt_includes_mode_guideline_and_cap():
    p = extract.extraction_prompt("aggressive", "I love mango lassi", "Noted!")
    assert "most novel information" in p  # aggressive guideline
    assert "at most 12" in p  # aggressive cap
    assert "I love mango lassi" in p and "preference" in p


def test_should_summarize():
    assert extract.should_summarize(10, 10) is True
    assert extract.should_summarize(20, 10) is True
    assert extract.should_summarize(7, 10) is False
    assert extract.should_summarize(0, 10) is False
    assert extract.should_summarize(10, 0) is False


def test_summarize_prompt_carries_conversation():
    p = extract.summarize_prompt("user: hi\nassistant: hello")
    assert "future self" in p and "user: hi" in p


def test_is_decayable():
    assert extract.is_decayable("fact", 40, 30) is True  # old plain fact, decay on
    assert extract.is_decayable("fact", 10, 30) is False  # not old enough
    assert extract.is_decayable("preference", 999, 30) is False  # never decay preferences
    assert extract.is_decayable("fact", 999, 0) is False  # decay off (0)


def test_cosine():
    assert extract.cosine([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert extract.cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert round(extract.cosine([1.0, 1.0], [1.0, 0.0]), 4) == 0.7071
    assert extract.cosine([], [1.0]) == 0.0  # mismatched / empty
    assert extract.cosine([0.0, 0.0], [1.0, 1.0]) == 0.0  # zero vector
