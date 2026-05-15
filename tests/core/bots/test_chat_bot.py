from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    UserMessageContent,
)
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


def _user_item(text: str, turn_id: int = 0) -> ContextItem:
    return ContextItem(content=UserMessageContent(text), turn_id=turn_id)


def _assistant_item(text: str, turn_id: int = 0) -> ContextItem:
    return ContextItem(content=AssistantMessageContent(text), turn_id=turn_id)


@pytest.fixture
def chat_backend() -> _MockBackend:
    return _MockBackend(response="chat response")


@pytest.fixture
def chat_bot(chat_backend: _MockBackend) -> ChatBot:
    return ChatBot(
        name="ChatBot",
        emoji="\N{ROBOT FACE}",
        llm=chat_backend,
    )


def test_chat_bot_is_not_human(chat_bot: ChatBot) -> None:
    assert chat_bot.is_human is False


@pytest.mark.asyncio
async def test_chat_bot_sends_context_to_llm(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    ctx = [
        _user_item("hello", turn_id=0),
        _assistant_item("hi there", turn_id=0),
        _user_item("how are you?", turn_id=1),
    ]
    await chat_bot.on_message(
        ChatMessage(sender="You", text="how are you?", timestamp=_TS), ctx
    )

    sent = chat_backend.calls[0]
    assert sent == [
        Message(role="user", content="hello"),
        Message(role="assistant", content="hi there"),
        Message(role="user", content="how are you?"),
    ]


@pytest.mark.asyncio
async def test_chat_bot_returns_one_assistant_item(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    reply, new_items = await chat_bot.on_message(
        ChatMessage(sender="You", text="hi", timestamp=_TS), []
    )
    assert reply is not None
    assert reply.text == "chat response"
    assert len(new_items) == 1
    assert isinstance(new_items[0].content, AssistantMessageContent)
    assert new_items[0].content.text == "chat response"


@pytest.mark.asyncio
async def test_chat_bot_empty_context_sends_empty_messages(
    chat_bot: ChatBot, chat_backend: _MockBackend
) -> None:
    await chat_bot.on_message(
        ChatMessage(sender="You", text="first", timestamp=_TS), []
    )
    assert chat_backend.calls[0] == []
