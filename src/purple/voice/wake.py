"""Wake-word detection via openWakeWord.

The model is injectable so the detection logic can be tested without audio hardware.
'hey_jarvis' is a built-in pretrained model and a fitting stand-in until we train a
custom 'hey_purple' model (openWakeWord ships a training pipeline for that).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("voice.wake")


class WakeListener:
    def __init__(
        self,
        model: Any | None = None,
        threshold: float | None = None,
        wake_model: str | None = None,
    ) -> None:
        self._model = model
        self.threshold = threshold if threshold is not None else settings.wake_threshold
        self.wake_model = wake_model or settings.wake_model

    def is_custom_model(self) -> bool:
        """True if wake_model points at a trained model file (e.g. hey_purple.onnx)
        rather than a built-in pretrained name like 'hey_jarvis'."""
        return self.wake_model.endswith((".onnx", ".tflite")) or Path(self.wake_model).exists()

    def _ensure_model(self) -> Any:
        if self._model is None:
            from openwakeword.model import Model

            if self.is_custom_model():
                log.info("loading_custom_wake_model", path=self.wake_model)
            else:
                # Built-in pretrained word: fetch it (no-op if already cached / offline).
                try:
                    from openwakeword.utils import download_models

                    download_models([self.wake_model])
                except Exception:
                    pass
                log.info("loading_pretrained_wake_model", model=self.wake_model)
            self._model = Model(wakeword_models=[self.wake_model])
        return self._model

    def score(self, frame: np.ndarray) -> float:
        """Highest wake-word confidence for this 16 kHz int16 frame (~1280 samples)."""
        preds = self._ensure_model().predict(frame)
        return float(max(preds.values())) if preds else 0.0

    def is_wake(self, frame: np.ndarray) -> bool:
        return self.score(frame) >= self.threshold

    def reset(self) -> None:
        if self._model is not None and hasattr(self._model, "reset"):
            self._model.reset()
