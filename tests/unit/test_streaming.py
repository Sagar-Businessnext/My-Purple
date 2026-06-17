"""Streaming voice tests: pure sentence chunking + cancelable playback (no audio)."""

from __future__ import annotations

from purple.voice import streaming


def test_flush_sentences_splits_on_boundaries():
    s, rem = streaming.flush_sentences("Hello there. How are you")
    assert s == ["Hello there."] and rem == " How are you"


def test_flush_sentences_multiple_and_newline():
    s, rem = streaming.flush_sentences("Done! Next? ")
    assert s == ["Done!", "Next?"] and rem.strip() == ""
    s, rem = streaming.flush_sentences("line one\nline two")
    assert s == ["line one"] and rem == "line two"


def test_flush_sentences_no_boundary():
    assert streaming.flush_sentences("no boundary yet") == ([], "no boundary yet")


async def test_stream_sentences_from_tokens():
    async def toks():
        for t in ["Hel", "lo. ", "Wor", "ld! ", "tail"]:
            yield t

    out = [s async for s in streaming.stream_sentences(toks())]
    assert out == ["Hello.", "World!", "tail"]


async def test_streaming_voice_plays_all():
    synth_calls: list[str] = []
    play_calls: list[bytes] = []

    async def synth(t: str) -> bytes:
        synth_calls.append(t)
        return b"wav:" + t.encode()

    async def play(b: bytes) -> None:
        play_calls.append(b)

    async def sents():
        for s in ["one.", "two.", "three."]:
            yield s

    sv = streaming.StreamingVoice(synth, play)
    n = await sv.speak(sents())
    assert n == 3 and synth_calls == ["one.", "two.", "three."] and len(play_calls) == 3


def test_word_groups():
    assert streaming.word_groups("") == []
    groups = streaming.word_groups("one two three four five", size=2)
    assert groups == ["one two", " three four", " five"]
    assert "".join(groups) == "one two three four five"  # concatenates back cleanly


def test_should_barge_in():
    assert streaming.should_barge_in(is_speaking=True, speech_detected=True) is True
    assert streaming.should_barge_in(is_speaking=True, speech_detected=False) is False
    assert streaming.should_barge_in(is_speaking=False, speech_detected=True) is False


def test_conversation_continues():
    assert streaming.conversation_continues("what's the time", True) is True
    assert streaming.conversation_continues("   ", True) is False  # empty/timed-out turn ends it
    assert streaming.conversation_continues("hello", False) is False  # mode off = single exchange


async def test_streaming_voice_cancel_stops_early():
    played: list[bytes] = []
    holder: dict = {}

    async def synth(t: str) -> bytes:
        return b"x"

    async def play(b: bytes) -> None:
        played.append(b)
        holder["sv"].cancel()  # barge-in after the first sentence

    async def sents():
        for s in ["a.", "b.", "c."]:
            yield s

    sv = streaming.StreamingVoice(synth, play)
    holder["sv"] = sv
    n = await sv.speak(sents())
    assert n == 1 and len(played) == 1  # cancelled → stops before the rest
