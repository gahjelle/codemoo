import pytest

from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.message import ChatMessage


@pytest.fixture
def bot() -> EchoBot:
    return EchoBot(name="Echo", emoji="\N{ROBOT FACE}")


@pytest.fixture
def human_message() -> ChatMessage:
    return ChatMessage(sender="human", text="hello there")


def test_name_is_non_empty(bot: EchoBot) -> None:
    assert bot.name


@pytest.mark.asyncio
async def test_echoes_human_message(bot: EchoBot, human_message: ChatMessage) -> None:
    [item] = await bot.on_message(human_message, [])

    assert item.content.text == human_message.text


@pytest.mark.asyncio
async def test_returns_one_assistant_context_item(
    bot: EchoBot, human_message: ChatMessage
) -> None:
    from codemoo.core.context_items import AssistantMessageContent, ItemMode

    [item] = await bot.on_message(human_message, [])

    assert isinstance(item.content, AssistantMessageContent)
    assert item.mode == ItemMode.ORIGINAL
