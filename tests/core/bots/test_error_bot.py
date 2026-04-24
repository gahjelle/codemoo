"""Tests for ErrorBot: persona selection, format_error LLM path, and fallback."""

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.error_bot import _PERSONAS, ErrorBot
from codemoo.core.message import ChatMessage


class _MockBackend:
    def __init__(self, response: str = "mock error response") -> None:
        self.response = response
        self.calls: list[object] = []

    async def complete(self, messages: object) -> str:
        self.calls.append(messages)
        return self.response


class _FailingBackend:
    async def complete(self, messages: object) -> str:
        msg = "LLM unavailable"
        raise ConnectionError(msg)


class _MockParticipant:
    name = "Iris"
    emoji = "\N{EYE}"
    is_human = False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],
    ) -> None:
        return None


def test_all_personas_are_distinct() -> None:
    names = {p.name for p in _PERSONAS}
    emojis = {p.emoji for p in _PERSONAS}
    prompts = {p.instructions for p in _PERSONAS}
    assert len(names) == len(_PERSONAS)
    assert len(emojis) == len(_PERSONAS)
    assert len(prompts) == len(_PERSONAS)


def test_persona_fields_are_non_empty() -> None:
    for persona in _PERSONAS:
        assert persona.name
        assert persona.emoji
        assert persona.instructions


def test_error_bot_name_and_emoji_match_a_known_persona() -> None:
    bot = ErrorBot(backend=_MockBackend())
    known_names = {p.name for p in _PERSONAS}
    known_emojis = {p.emoji for p in _PERSONAS}
    assert bot.name in known_names
    assert bot.emoji in known_emojis


def test_error_bot_is_not_human() -> None:
    bot = ErrorBot(backend=_MockBackend())
    assert bot.is_human is False


def test_error_bot_persona_is_stable_within_session() -> None:
    bot = ErrorBot(backend=_MockBackend())
    name_first = bot.name
    emoji_first = bot.emoji
    assert bot.name == name_first
    assert bot.emoji == emoji_first


@pytest.mark.asyncio
async def test_on_message_always_returns_none() -> None:
    bot = ErrorBot(backend=_MockBackend())
    msg = ChatMessage(sender="You", text="hello")
    result = await bot.on_message(msg, [])
    assert result is None


@pytest.mark.asyncio
async def test_format_error_returns_llm_response_when_available() -> None:
    bot = ErrorBot(backend=_MockBackend(response="Oh no, so sorry!"))
    result = await bot.format_error(_MockParticipant(), ValueError("oops"))
    assert result.text == "Oh no, so sorry!"
    assert result.sender == bot.name


@pytest.mark.asyncio
async def test_format_error_passes_instructions_to_backend() -> None:
    backend = _MockBackend()
    bot = ErrorBot(backend=backend)
    await bot.format_error(_MockParticipant(), ValueError("oops"))

    sent_messages = backend.calls[0]
    assert isinstance(sent_messages, list)
    expected = Message(
        role="system", content=f"{bot._persona.instructions} Answer in English"
    )
    assert sent_messages[0] == expected


@pytest.mark.asyncio
async def test_format_error_falls_back_to_plain_text_when_llm_fails() -> None:
    bot = ErrorBot(backend=_FailingBackend())
    exc = RuntimeError("connection refused")
    result = await bot.format_error(_MockParticipant(), exc)
    assert "Iris" in result.text
    assert "connection refused" in result.text
    assert result.sender == bot.name


@pytest.mark.asyncio
async def test_format_error_fallback_does_not_raise() -> None:
    bot = ErrorBot(backend=_FailingBackend())
    result = await bot.format_error(_MockParticipant(), Exception("total failure"))
    assert result is not None
