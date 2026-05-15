import pytest

from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.context_items import AssistantMessageContent

from .conftest import user_ctx


@pytest.fixture
def bot() -> EchoBot:
    return EchoBot(name="Echo", emoji="\N{ROBOT FACE}")


def test_name_is_non_empty(bot: EchoBot) -> None:
    assert bot.name


@pytest.mark.asyncio
async def test_echoes_human_message(bot: EchoBot) -> None:
    ctx = user_ctx("hello there")
    [item] = await bot.on_message(ctx)

    assert isinstance(item.content, AssistantMessageContent)
    assert item.content.text == "hello there"


@pytest.mark.asyncio
async def test_returns_one_assistant_context_item(bot: EchoBot) -> None:
    from codemoo.core.context_items import ItemMode

    [item] = await bot.on_message(user_ctx("hello"))

    assert isinstance(item.content, AssistantMessageContent)
    assert item.mode == ItemMode.ORIGINAL
