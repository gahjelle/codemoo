from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.system_bot import SystemBot
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
        backend=backend,
        human_name="You",
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
    history = [_msg("You", "earlier"), _msg("Sigma", "reply")]
    await system_bot.on_message(_msg("You", "now"), history)

    sent = backend.calls[0]
    assert sent[0] == Message(
        role="system", content="You are a terse coding assistant."
    )


@pytest.mark.asyncio
async def test_filters_out_other_bot_messages(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    history = [
        _msg("You", "hi"),
        _msg("OtherBot", "noise"),
        _msg("Sigma", "reply"),
    ]
    await system_bot.on_message(_msg("You", "follow up"), history)

    sent = backend.calls[0]
    contents = [m.content for m in sent]
    assert "noise" not in contents


@pytest.mark.asyncio
async def test_clips_history_to_max_messages(backend: _MockBackend) -> None:
    bot = SystemBot(
        name="Sigma",
        emoji="\N{PERFORMING ARTS}",
        backend=backend,
        human_name="You",
        instructions="Be terse.",
        max_messages=2,
    )
    history = [
        _msg("You", "msg1"),
        _msg("Sigma", "reply1"),
        _msg("You", "msg2"),
        _msg("Sigma", "reply2"),
    ]
    await bot.on_message(_msg("You", "msg3"), history)

    sent = backend.calls[0]
    # system + 2 clipped history + current
    assert len(sent) == 4
    assert sent[0].role == "system"
    assert sent[1].content == "msg2"
    assert sent[2].content == "reply2"
    assert sent[3].content == "msg3"


@pytest.mark.asyncio
async def test_reply_sender_is_bot_name(
    system_bot: SystemBot, backend: _MockBackend
) -> None:
    reply = await system_bot.on_message(_msg("You", "hello"), [])

    assert reply is not None
    assert reply.sender == "Sigma"
