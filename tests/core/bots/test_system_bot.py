from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.system_bot import SystemBot
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


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


@pytest.fixture
def backend() -> _MockBackend:
    return _MockBackend(response="system response")


@pytest.fixture
def system_bot(backend: _MockBackend) -> SystemBot:
    return SystemBot(
        name="Sigma",
        emoji="\N{PERFORMING ARTS}",
        llm=backend,
        instructions="You are a terse coding assistant.",
    )


def test_system_bot_is_not_human(system_bot: SystemBot) -> None:
    assert system_bot.is_human is False


@pytest.mark.asyncio
async def test_system_message_is_first_in_context(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    await system_bot.on_message(_msg("You", "hello"), [])

    sent = backend.calls[0]
    assert sent[0] == Message(
        role="system", content="You are a terse coding assistant."
    )


@pytest.mark.asyncio
async def test_system_message_present_with_history(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    ctx = [
        ContextItem(content=UserMessageContent("earlier")),
        ContextItem(content=AssistantMessageContent("reply")),
    ]
    await system_bot.on_message(_msg("You", "now"), ctx)

    sent = backend.calls[0]
    assert sent[0] == Message(
        role="system", content="You are a terse coding assistant."
    )


@pytest.mark.asyncio
async def test_includes_context_items_in_correct_roles(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    ctx = [
        ContextItem(content=UserMessageContent("hi")),
        ContextItem(content=AssistantMessageContent("reply")),
    ]
    await system_bot.on_message(_msg("You", "follow up"), ctx)

    sent = backend.calls[0]
    assert sent[0].role == "system"
    assert sent[1] == Message(role="user", content="hi")
    assert sent[2] == Message(role="assistant", content="reply")


@pytest.mark.asyncio
async def test_reply_sender_is_bot_name(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    reply, _ = await system_bot.on_message(_msg("You", "hello"), [])

    assert reply is not None
    assert reply.sender == "Sigma"
