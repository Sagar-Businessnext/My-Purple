"""Dead-simple energy-based voice activity detection over int16 PCM frames."""

from __future__ import annotations

import numpy as np


def rms(frame: np.ndarray) -> float:
    """Root-mean-square amplitude of an int16 frame."""
    if frame.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(frame.astype(np.float64) ** 2)))


def is_speech(frame: np.ndarray, threshold: float) -> bool:
    """True if the frame is louder than the silence threshold."""
    return rms(frame) >= threshold
