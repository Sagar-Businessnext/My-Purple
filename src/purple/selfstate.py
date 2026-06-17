"""What Purple can tell about her own condition — fed into her reasoning so she can talk
about problems she's facing (e.g. "your speaker is muted, so I'll keep this on screen"),
and used by the SelfWatcher to proactively flag her own outages."""

from __future__ import annotations

from purple import audio


def voice_issue() -> str | None:
    """A short note if Purple's spoken voice can't currently be heard, else None."""
    if not audio.can_be_heard():
        return (
            f"Your audio output is unavailable ({audio.describe()}), so anything I say "
            "aloud won't reach you — keep replies on screen and mention it."
        )
    return None


def context_note() -> str | None:
    """A one-line system note about degraded self-state to inject into the agent, or None
    when everything's fine (so normal turns aren't cluttered)."""
    issues = [note for note in (voice_issue(),) if note]
    if not issues:
        return None
    return "System self-check — " + " ".join(issues)
