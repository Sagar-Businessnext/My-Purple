"""Real-time voice streaming: turn a token/text stream into speakable sentences and play
them as they arrive — cancelably, so Purple can be interrupted mid-reply (barge-in, M4b).

The sentence splitting is pure + unit-tested; StreamingVoice takes injected synth/play
callables so its cancel behaviour is testable without audio hardware.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
import re

_BOUNDARY = re.compile(r"[.!?](?=\s|$)|\n")


def word_groups(text: str, size: int = 4) -> list[str]:
    """Split text into small groups of words for progressive display in the chat UI
    (display-streaming). Pure; preserves spacing so the chunks concatenate back."""
    words = (text or "").split()
    if not words:
        return []
    groups: list[str] = []
    for i in range(0, len(words), max(1, size)):
        chunk = " ".join(words[i : i + size])
        groups.append(chunk if i == 0 else " " + chunk)
    return groups


def should_barge_in(is_speaking: bool, speech_detected: bool) -> bool:
    """Interrupt Purple only while she's speaking AND new speech is heard. Pure.
    (The interrupting utterance is still speaker-gated before it's acted on.)"""
    return is_speaking and speech_detected


def conversation_continues(transcript: str, conversation_mode: bool) -> bool:
    """Stay in the back-and-forth only if conversation mode is on and the user actually
    said something this turn (an empty/timed-out capture ends the session). Pure."""
    return conversation_mode and bool(transcript.strip())


def flush_sentences(buffer: str) -> tuple[list[str], str]:
    """Split off complete sentences from `buffer`, returning (sentences, remainder). Pure.

    A sentence ends at . ? ! (followed by space/end) or a newline. The remainder is the
    trailing, not-yet-complete text to keep accumulating."""
    sentences: list[str] = []
    last = 0
    for m in _BOUNDARY.finditer(buffer):
        chunk = buffer[last : m.end()].strip()
        if chunk:
            sentences.append(chunk)
        last = m.end()
    return sentences, buffer[last:]


async def stream_sentences(tokens: AsyncIterator[str]) -> AsyncIterator[str]:
    """Accumulate a token stream and yield whole sentences as soon as they complete,
    then the final trailing fragment."""
    buf = ""
    async for tok in tokens:
        buf += tok
        done, buf = flush_sentences(buf)
        for s in done:
            yield s
    tail = buf.strip()
    if tail:
        yield tail


class StreamingVoice:
    """Synthesize + play a stream of sentences, cancelably.

    synth(text) -> wav bytes (async); play(wav) -> None (async). cancel() stops after the
    current step so a new (enrolled) speaker can barge in."""

    def __init__(
        self,
        synth: Callable[[str], Awaitable[bytes]],
        play: Callable[[bytes], Awaitable[None]],
    ) -> None:
        self._synth = synth
        self._play = play
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    async def speak(self, sentences: AsyncIterator[str]) -> int:
        """Play each sentence until exhausted or cancelled. Returns sentences spoken."""
        self._cancelled = False
        spoken = 0
        async for sentence in sentences:
            if self._cancelled:
                break
            audio = await self._synth(sentence)
            if self._cancelled:
                break
            if audio:
                await self._play(audio)
            spoken += 1
        return spoken
