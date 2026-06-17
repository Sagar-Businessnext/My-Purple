"""Speaker-ID tests: the fail-closed access decision, cosine/match, best_match, and the
voiceprint storage roundtrip. Pure / file-only — no resemblyzer, no audio."""

from __future__ import annotations

from purple import speaker
from purple.config import settings


def test_decide_access_fail_closed():
    # gate off → always allow
    assert speaker.decide_access(enabled=False, enrolled=True, model_available=False, recognized=False) == "allow"
    # not enrolled yet → allow (don't lock the user out)
    assert speaker.decide_access(enabled=True, enrolled=False, model_available=False, recognized=False) == "allow"
    # enrolled but verifier missing/broken → DENY (fail-closed, never silently open)
    assert speaker.decide_access(enabled=True, enrolled=True, model_available=False, recognized=False) == "deny"
    # enrolled + model + recognized → allow
    assert speaker.decide_access(enabled=True, enrolled=True, model_available=True, recognized=True) == "allow"
    # enrolled + model + NOT recognized → deny
    assert speaker.decide_access(enabled=True, enrolled=True, model_available=True, recognized=False) == "deny"


def test_match_threshold(monkeypatch):
    monkeypatch.setattr(settings, "speaker_threshold", 0.75)
    assert speaker._match(0.80) is True
    assert speaker._match(0.70) is False
    assert speaker._match(0.60, threshold=0.5) is True


def test_cosine():
    assert speaker._cosine([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert speaker._cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert speaker._cosine([1.0, 0.0], [1.0, 0.0, 0.0]) == 0.0  # shape mismatch


def test_best_match_picks_highest():
    prints = {"abhishek": [[1.0, 0.0]], "guest": [[0.0, 1.0]]}
    name, score = speaker.best_match([0.96, 0.10], prints)
    assert name == "abhishek" and score > 0.9
    assert speaker.best_match([0.1, 0.1], {}) == (None, 0.0)


def test_voiceprint_storage_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "models_dir", tmp_path)
    assert speaker.has_enrollments() is False
    speaker.save_prints({"abhishek": [[0.1, 0.2]], "priya": [[0.3, 0.4]]})
    assert speaker.has_enrollments() is True
    assert speaker.list_speakers() == ["abhishek", "priya"]
    assert speaker.remove_speaker("priya") is True
    assert speaker.list_speakers() == ["abhishek"]
    assert speaker.remove_speaker("nobody") is False


def test_load_prints_missing_file_is_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "models_dir", tmp_path / "nope")
    assert speaker.load_prints() == {}


def _setup_gate(monkeypatch, *, enabled, enrolled, available, identify):
    monkeypatch.setattr(settings, "require_enrolled_voice", enabled)
    monkeypatch.setattr(settings, "speaker_threshold", 0.75)
    monkeypatch.setattr(speaker, "has_enrollments", lambda: enrolled)
    monkeypatch.setattr(speaker, "available", lambda: available)
    monkeypatch.setattr(speaker, "identify", identify)


def test_authorize_open_when_disabled_or_unenrolled(monkeypatch):
    _setup_gate(monkeypatch, enabled=False, enrolled=True, available=True,
                identify=lambda s, sr: ("x", 0.99))
    assert speaker.authorize([0.0], 16000)["reason"] == "open"
    _setup_gate(monkeypatch, enabled=True, enrolled=False, available=True,
                identify=lambda s, sr: ("x", 0.99))
    assert speaker.authorize([0.0], 16000)["allow"] is True


def test_authorize_recognized(monkeypatch):
    _setup_gate(monkeypatch, enabled=True, enrolled=True, available=True,
                identify=lambda s, sr: ("abhishek", 0.9))
    r = speaker.authorize([0.0], 16000)
    assert r["allow"] is True and r["reason"] == "recognized" and r["speaker"] == "abhishek"


def test_authorize_unrecognized_denies(monkeypatch):
    _setup_gate(monkeypatch, enabled=True, enrolled=True, available=True,
                identify=lambda s, sr: ("abhishek", 0.40))
    r = speaker.authorize([0.0], 16000)
    assert r["allow"] is False and r["reason"] == "unrecognized" and r["speaker"] is None


def test_authorize_fail_closed_when_model_missing(monkeypatch):
    _setup_gate(monkeypatch, enabled=True, enrolled=True, available=False,
                identify=lambda s, sr: ("x", 0.99))
    r = speaker.authorize([0.0], 16000)
    assert r["allow"] is False and r["reason"] == "verifier_unavailable"


def test_authorize_fail_closed_on_verifier_error(monkeypatch):
    def _boom(s, sr):
        raise RuntimeError("model exploded")

    _setup_gate(monkeypatch, enabled=True, enrolled=True, available=True, identify=_boom)
    r = speaker.authorize([0.0], 16000)
    assert r["allow"] is False and r["reason"] == "verifier_unavailable"  # error ≠ silent allow
