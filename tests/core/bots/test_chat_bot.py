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
        human_name="You",
    )


def test_chat_bot_is_not_human(chat_bot: ChatBot) -> None:
    assert chat_bot.is_human is False


@pytest.mark.asyncio
async def test_chat_bot_filters_out_other_bot_messages(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    history = [
        _msg("You", "hello"),
        _msg("EchoBot", "hello"),  # should be excluded
        _msg("ChatBot", "hi there"),
    ]
    await chat_bot.on_message(_msg("You", "how are you?"), history)

    sent = chat_backend.calls[0]
    assert sent == [
        Message(role="user", content="hello"),
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


@pytest.mark.asyncio
async def test_chat_bot_clips_history_to_max_messages() -> None:
    backend = _MockBackend()
    bot = ChatBot(
        name="ChatBot",
        emoji="\N{ROBOT FACE}",
        backend=backend,
        human_name="You",
        max_messages=2,
    )
    history = [
        _msg("You", "msg1"),
        _msg("ChatBot", "reply1"),
        _msg("You", "msg2"),
        _msg("ChatBot", "reply2"),
    ]
    await bot.on_message(_msg("You", "msg3"), history)

    sent = backend.calls[0]
    assert len(sent) == 3
    assert sent[0].content == "msg2"
    assert sent[1].content == "reply2"
    assert sent[2].content == "msg3"


@pytest.mark.asyncio
async def test_chat_bot_does_not_clip_when_within_limit(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    history = [_msg("You", "a"), _msg("ChatBot", "b")]
    await chat_bot.on_message(_msg("You", "c"), history)

    sent = chat_backend.calls[0]
    assert len(sent) == 3
