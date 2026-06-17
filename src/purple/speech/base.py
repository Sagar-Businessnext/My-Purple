"""Speech provider interface + factory.

The whole point of this abstraction: v1 runs fully local (faster-whisper + Piper),
but switching to Sarvam's cloud voice is a one-line config change
(PURPLE_SPEECH_PROVIDER=sarvam) with zero code rewrite. Not a future migration —
it's pluggable by design.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from purple.config import settings


class SpeechProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str) -> str:
        """Speech -> text. Takes a path to an audio file, returns the transcript."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Text -> speech. Returns WAV audio bytes."""


def get_speech_provider() -> SpeechProvider:
    if settings.speech_provider.lower() == "sarvam":
        from purple.speech.sarvam_provider import SarvamSpeech

        return SarvamSpeech()
    from purple.speech.local_provider import LocalSpeech

    return LocalSpeech()
