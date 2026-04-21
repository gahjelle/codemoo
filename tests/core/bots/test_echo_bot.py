from datetime import UTC, datetime

import pytest

from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.message import ChatMessage


@pytest.fixture
def bot() -> EchoBot:
    return EchoBot(name="Echo", emoji="\N{ROBOT FACE}")


@pytest.fixture
def human_message() -> ChatMessage:
    return ChatMessage(
        sender="human",
        text="hello there",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
    )


def test_name_is_non_empty(bot: EchoBot) -> None:
    assert bot.name


@pytest.mark.asyncio
async def test_echoes_human_message(bot: EchoBot, human_message: ChatMessage) -> None:
    reply = await bot.on_message(human_message, [])

    assert reply is not None
    assert reply.sender == bot.name
    assert reply.text == human_message.text


@pytest.mark.asyncio
async def test_reply_has_utc_timestamp(
    bot: EchoBot, human_message: ChatMessage
) -> None:
    before = datetime.now(tz=UTC)
    reply = await bot.on_message(human_message, [])
    after = datetime.now(tz=UTC)

    assert reply is not None
    assert reply.timestamp.tzinfo is UTC
    assert before <= reply.timestamp <= after
