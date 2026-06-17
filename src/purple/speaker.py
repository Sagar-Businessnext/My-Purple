"""Speaker identification — the voice access gate. Only enrolled voices may talk to Purple.

Embeddings come from Resemblyzer (local, CPU-friendly), imported lazily so it's an
*optional* dependency. The access decision is FAIL-CLOSED: once a voice is enrolled, a
missing or broken verifier denies voice — it never silently re-opens the gate. The pure
decision functions are unit-tested; the encoder itself runs on the user's PC.
"""

from __future__ import annotations

import json
from pathlib import Path

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("speaker")


# --- voiceprint storage (name -> list of embeddings) ---
def _prints_path() -> Path:
    return settings.models_dir / "voiceprints.json"


def load_prints() -> dict[str, list[list[float]]]:
    p = _prints_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


def save_prints(prints: dict[str, list[list[float]]]) -> None:
    p = _prints_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(prints), encoding="utf-8")


def has_enrollments() -> bool:
    return bool(load_prints())


def list_speakers() -> list[str]:
    return sorted(load_prints().keys())


def remove_speaker(name: str) -> bool:
    prints = load_prints()
    if name not in prints:
        return False
    del prints[name]
    save_prints(prints)
    return True


# --- pure matching / access decision (unit-tested) ---
def _cosine(a: list[float], b: list[float]) -> float:
    import numpy as np

    va, vb = np.asarray(a, dtype="float32"), np.asarray(b, dtype="float32")
    if va.shape != vb.shape or va.size == 0:
        return 0.0
    na, nb = float(np.linalg.norm(va)), float(np.linalg.norm(vb))
    return float(va @ vb / (na * nb)) if na and nb else 0.0


def best_match(embedding: list[float], prints: dict[str, list[list[float]]]) -> tuple[str | None, float]:
    """Highest cosine similarity of `embedding` against every enrolled print. Pure."""
    best_name: str | None = None
    best_score = 0.0
    for name, vecs in (prints or {}).items():
        for v in vecs:
            score = _cosine(embedding, v)
            if score > best_score:
                best_name, best_score = name, score
    return best_name, best_score


def _match(score: float, threshold: float | None = None) -> bool:
    thr = settings.speaker_threshold if threshold is None else threshold
    return score >= thr


def decide_access(*, enabled: bool, enrolled: bool, model_available: bool, recognized: bool) -> str:
    """Pure gate decision → 'allow' | 'deny'. FAIL-CLOSED once a voice is enrolled.

    - gate off            → allow
    - no voice enrolled   → allow (don't lock the user out before they enroll)
    - enrolled, no model  → DENY (verifier can't confirm it's you → refuse, never open)
    - enrolled, model ok  → allow only if the voice is recognized
    """
    if not enabled or not enrolled:
        return "allow"
    if not model_available:
        return "deny"
    return "allow" if recognized else "deny"


# --- encoder (Resemblyzer; lazy + optional) ---
_encoder = None


def available() -> bool:
    try:
        import resemblyzer  # noqa: F401

        return True
    except Exception:
        return False


def _get_encoder() -> object:
    global _encoder
    if _encoder is None:
        from resemblyzer import VoiceEncoder

        log.info("loading_speaker_encoder")
        _encoder = VoiceEncoder()
    return _encoder


def embed(samples: object, sample_rate: int) -> list[float]:
    """Voice embedding for an int16/float audio array. Requires resemblyzer."""
    import numpy as np
    from resemblyzer import preprocess_wav

    arr = np.asarray(samples)
    if arr.dtype.kind == "i":  # int16 PCM -> float [-1, 1]
        arr = arr.astype("float32") / 32768.0
    wav = preprocess_wav(arr, source_sr=sample_rate)
    return _get_encoder().embed_utterance(wav).tolist()


def enroll(name: str, samples: object, sample_rate: int) -> int:
    """Add a voice sample for `name`. Returns how many samples that speaker now has."""
    emb = embed(samples, sample_rate)
    prints = load_prints()
    prints.setdefault(name, []).append(emb)
    save_prints(prints)
    log.info("voice_enrolled", name=name, samples=len(prints[name]))
    return len(prints[name])


def identify(samples: object, sample_rate: int) -> tuple[str | None, float]:
    return best_match(embed(samples, sample_rate), load_prints())


def is_recognized(samples: object, sample_rate: int) -> bool:
    _name, score = identify(samples, sample_rate)
    return _match(score)


def embed_file(path: str | Path) -> list[float]:
    """Embed a saved audio file (any format librosa can read). Requires resemblyzer."""
    from resemblyzer import preprocess_wav

    wav = preprocess_wav(Path(path))
    return _get_encoder().embed_utterance(wav).tolist()


def enroll_file(name: str, path: str | Path) -> int:
    emb = embed_file(path)
    prints = load_prints()
    prints.setdefault(name, []).append(emb)
    save_prints(prints)
    log.info("voice_enrolled", name=name, samples=len(prints[name]))
    return len(prints[name])


def _run_gate(get_match: object) -> dict:
    """Shared gate logic. `get_match()` returns (name, score) or raises. Never raises;
    a verifier error becomes 'verifier_unavailable' → a DENY once enrolled (fail-closed)."""
    enabled = settings.require_enrolled_voice
    enrolled = has_enrollments()
    if not enabled or not enrolled:
        return {"allow": True, "reason": "open", "speaker": None}
    model_ok = available()
    name: str | None = None
    recognized = False
    if model_ok:
        try:
            name, score = get_match()
            recognized = _match(score)
            if not recognized:
                name = None
        except Exception as exc:
            log.warning("voice_verify_failed", error=str(exc))
            model_ok = False
    decision = decide_access(
        enabled=enabled, enrolled=enrolled, model_available=model_ok, recognized=recognized
    )
    reason = (
        "recognized" if decision == "allow"
        else ("verifier_unavailable" if not model_ok else "unrecognized")
    )
    return {"allow": decision == "allow", "reason": reason, "speaker": name}


def authorize(samples: object, sample_rate: int) -> dict:
    """Gate a voice clip (int16/float samples). See _run_gate for the result shape."""
    return _run_gate(lambda: identify(samples, sample_rate))


def authorize_file(path: str | Path) -> dict:
    """Gate a saved audio file (e.g. an uploaded recording)."""
    return _run_gate(lambda: best_match(embed_file(path), load_prints()))
