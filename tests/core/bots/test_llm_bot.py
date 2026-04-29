from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.llm_bot import LlmBot
from codemoo.core.message import ChatMessage


class _MockBackend:
    """Captures calls and returns a fixed response."""

    def __init__(self, response: str = "mock response") -> None:
        self.response = response
        self.calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        self.calls.append(list(messages))
        return self.response


_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


@pytest.fixture
def mock_backend() -> _MockBackend:
    return _MockBackend()


@pytest.fixture
def llm_bot(mock_backend: _MockBackend) -> LlmBot:
    return LlmBot(name="LLMBot", emoji="\N{ROBOT FACE}", llm=mock_backend)


def test_llm_bot_is_not_human(llm_bot: LlmBot) -> None:
    assert llm_bot.is_human is False


@pytest.mark.asyncio
async def test_llm_bot_sends_only_current_message(
    llm_bot: LlmBot, mock_backend: _MockBackend
) -> None:
    history = [_msg("You", "earlier message")]
    await llm_bot.on_message(_msg("You", "latest"), history)

    assert len(mock_backend.calls) == 1
    assert mock_backend.calls[0] == [Message(role="user", content="latest")]


@pytest.mark.asyncio
async def test_llm_bot_returns_response_as_chat_message(
    llm_bot: LlmBot, mock_backend: _MockBackend
) -> None:
    mock_backend.response = "I am a bot"
    reply = await llm_bot.on_message(_msg("You", "hi"), [])

    assert reply is not None
    assert reply.sender == "LLMBot"
    assert reply.text == "I am a bot"
