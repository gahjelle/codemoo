from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.chat_bot import ChatBot
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
def chat_backend() -> _MockBackend:
    return _MockBackend(response="chat response")


@pytest.fixture
def chat_bot(chat_backend: _MockBackend) -> ChatBot:
    return ChatBot(
        name="ChatBot",
        emoji="\N{ROBOT FACE}",
        backend=chat_backend,
    )


def test_chat_bot_is_not_human(chat_bot: ChatBot) -> None:
    assert chat_bot.is_human is False


@pytest.mark.asyncio
async def test_chat_bot_includes_other_bot_messages_as_user_role(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    history = [
        _msg("You", "hello"),
        _msg("EchoBot", "hello"),  # now included as user role
        _msg("ChatBot", "hi there"),
    ]
    await chat_bot.on_message(_msg("You", "how are you?"), history)

    sent = chat_backend.calls[0]
    assert sent == [
        Message(role="user", content="hello"),
        Message(role="user", content="hello"),  # EchoBot message as user
        Message(role="assistant", content="hi there"),
        Message(role="user", content="how are you?"),
    ]


@pytest.mark.asyncio
async def test_chat_bot_maps_own_history_to_assistant_role(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    history = [_msg("ChatBot", "previous reply")]
    await chat_bot.on_message(_msg("You", "follow up"), history)

    sent = chat_backend.calls[0]
    assert Message(role="assistant", content="previous reply") in sent


@pytest.mark.asyncio
async def test_chat_bot_maps_human_history_to_user_role(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    history = [_msg("You", "earlier question")]
    await chat_bot.on_message(_msg("You", "now"), history)

    sent = chat_backend.calls[0]
    assert Message(role="user", content="earlier question") in sent


@pytest.mark.asyncio
async def test_chat_bot_current_message_is_last_user_turn(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    history = [_msg("You", "first"), _msg("ChatBot", "reply")]
    await chat_bot.on_message(_msg("You", "final"), history)

    sent = chat_backend.calls[0]
    assert sent[-1] == Message(role="user", content="final")
