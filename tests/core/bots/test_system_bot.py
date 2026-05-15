import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.system_bot import SystemBot
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    UserMessageContent,
)

from .conftest import user_ctx


class _MockBackend:
    """Captures calls and returns a fixed response."""

    def __init__(self, response: str = "mock response") -> None:
        self.response = response
        self.calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        self.calls.append(list(messages))
        return self.response


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
    await system_bot.on_message(user_ctx("hello"))

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
        *user_ctx("now"),
    ]
    await system_bot.on_message(ctx)

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
        *user_ctx("follow up"),
    ]
    await system_bot.on_message(ctx)

    sent = backend.calls[0]
    assert sent[0].role == "system"
    assert sent[1] == Message(role="user", content="hi")
    assert sent[2] == Message(role="assistant", content="reply")


@pytest.mark.asyncio
async def test_reply_is_assistant_content(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    from codemoo.core.context_items import AssistantMessageContent

    [item] = await system_bot.on_message(user_ctx("hello"))

    assert isinstance(item.content, AssistantMessageContent)
    assert item.content.text == "system response"
