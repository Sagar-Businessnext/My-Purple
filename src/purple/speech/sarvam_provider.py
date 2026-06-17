"""Sarvam AI cloud speech — the optional, higher-quality Indian-language backup.

NOTE: This sends audio/text to Sarvam's servers and is NOT local. It only runs when
PURPLE_SPEECH_PROVIDER=sarvam and an API key is set. Endpoint names/params follow
Sarvam's current REST API — re-check https://docs.sarvam.ai before enabling.
"""

from __future__ import annotations

import base64
from pathlib import Path

import httpx

from purple.config import settings
from purple.speech.base import SpeechProvider

STT_URL = "https://api.sarvam.ai/speech-to-text"
TTS_URL = "https://api.sarvam.ai/text-to-speech"


class SarvamSpeech(SpeechProvider):
    def __init__(self) -> None:
        if not settings.sarvam_api_key:
            raise RuntimeError("PURPLE_SARVAM_API_KEY is not set but speech provider is 'sarvam'.")
        self._headers = {"api-subscription-key": settings.sarvam_api_key}

    async def transcribe(self, audio_path: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            with Path(audio_path).open("rb") as fh:
                resp = await client.post(
                    STT_URL,
                    headers=self._headers,
                    files={"file": (audio_path, fh, "audio/wav")},
                    data={"model": "saaras:v2", "language_code": "unknown"},
                )
        resp.raise_for_status()
        return resp.json().get("transcript", "")

    async def synthesize(self, text: str) -> bytes:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                TTS_URL,
                headers=self._headers,
                json={
                    "text": text,
                    "target_language_code": "en-IN",
                    "speaker": "anushka",
                    "model": "bulbul:v2",
                },
            )
        resp.raise_for_status()
        audios = resp.json().get("audios", [])
        return base64.b64decode(audios[0]) if audios else b""
