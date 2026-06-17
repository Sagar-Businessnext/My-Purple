"""Auto-memory tuning + pure helpers — no DB / LLM / network imports, so this stays
cheap to import and easy to unit-test. The Memory store calls into these.

Auto-learning has three modes (PURPLE_AUTO_MEMORY_MODE):
  - moderate  : only clearly durable, important facts (default)
  - high      : the above plus softer signals (interests, habits, recurring topics)
  - aggressive: capture most novel info about the user, even minor/one-off details
"""

from __future__ import annotations

AUTO_MEMORY_MODES = ("moderate", "high", "aggressive")

_MODE: dict[str, dict] = {
    "moderate": {
        "max_facts": 3,
        "guideline": (
            "Only clearly durable, important facts: stable preferences, key people, "
            "ongoing projects, commitments and dates. Ignore small talk and anything "
            "transient or one-off."
        ),
    },
    "high": {
        "max_facts": 6,
        "guideline": (
            "Durable facts plus softer signals: interests, opinions, habits and "
            "recurring topics. Still skip purely transient details."
        ),
    },
    "aggressive": {
        "max_facts": 12,
        "guideline": (
            "Capture most novel information about the user, even minor preferences and "
            "one-off details, as long as it could plausibly matter later."
        ),
    },
}

# Fact categories (stored in Fact.kind).
CATEGORIES = ("preference", "person", "project", "routine", "fact")

# Categories that are about a person/place/etc. and worth promoting to an Entity.
_DEDUP_THRESHOLD = 0.90  # cosine similarity at/above which a "new" fact is a duplicate


def mode_params(mode: str) -> dict:
    """Extraction knobs for an auto-memory mode (falls back to moderate)."""
    return _MODE.get(mode, _MODE["moderate"])


def normalize_mode(mode: str) -> str:
    return mode if mode in AUTO_MEMORY_MODES else "moderate"


def normalize_category(category: str) -> str:
    return category if category in CATEGORIES else "fact"


def split_aliases(raw: str) -> list[str]:
    return [a.strip() for a in (raw or "").split(",") if a.strip()]


def is_duplicate(similarity: float, threshold: float = _DEDUP_THRESHOLD) -> bool:
    """A candidate fact duplicates an existing one when their embeddings are this close."""
    return similarity >= threshold


def profile_summary(profile: dict[str, str]) -> str:
    """One-line summary of the structured profile, common keys first."""
    if not profile:
        return ""
    order = ["name", "location", "work", "comms_style"]
    items = sorted(
        ((k, v) for k, v in profile.items() if v),
        key=lambda kv: (order.index(kv[0]) if kv[0] in order else 99, kv[0]),
    )
    return "; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in items)


def should_summarize(message_count: int, every: int = 10) -> bool:
    """Refresh the rolling session summary every `every` messages."""
    return message_count > 0 and every > 0 and message_count % every == 0


def summarize_prompt(conversation: str) -> str:
    return (
        "Summarize this conversation into a few sentences for your future self: what the "
        "user wanted, decisions made, and any durable facts or preferences revealed. Be "
        "concise.\n\n" + conversation
    )


def is_decayable(category: str, age_days: float, max_age_days: int) -> bool:
    """Should an old memory be forgotten? Only plain 'fact' entries decay — preferences,
    people, projects and routines are kept. Off when max_age_days <= 0. Pure."""
    if max_age_days <= 0:
        return False
    return category == "fact" and age_days > max_age_days


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two equal-length vectors (0.0 if either is empty/zero)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def extraction_prompt(mode: str, user_text: str, assistant_text: str) -> str:
    """Build the LLM prompt that pulls durable facts from one exchange, tuned by mode."""
    p = mode_params(normalize_mode(mode))
    cats = " | ".join(CATEGORIES)
    return (
        "From the exchange below, extract facts worth remembering long-term about the "
        f"user. {p['guideline']} Return at most {p['max_facts']}. Reply ONLY with a JSON "
        'array of objects like {"text": "...", "category": "preference"} where category is '
        f"one of: {cats}. Return [] if nothing is worth keeping. Do NOT include secrets, "
        "passwords, financial-account numbers, or health details.\n\n"
        f"User: {user_text}\nAssistant: {assistant_text}"
    )
