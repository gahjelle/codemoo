from datetime import UTC, datetime

import pytest

from gaia.core.echo_bot import EchoBot
from gaia.core.message import ChatMessage


@pytest.fixture
def bot() -> EchoBot:
    return EchoBot()


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
    reply = await bot.on_message(human_message)

    assert reply is not None
    assert reply.sender == bot.name
    assert reply.text == human_message.text


@pytest.mark.asyncio
async def test_reply_timestamp_matches_input(
    bot: EchoBot, human_message: ChatMessage
) -> None:
    # EchoBot must not call datetime.now(); the shell owns timestamp assignment
    reply = await bot.on_message(human_message)

    assert reply is not None
    assert reply.timestamp == human_message.timestamp


@pytest.mark.asyncio
async def test_does_not_echo_own_message(bot: EchoBot) -> None:
    own_message = ChatMessage(
        sender=bot.name,
        text="I said this",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    reply = await bot.on_message(own_message)

    assert reply is None
