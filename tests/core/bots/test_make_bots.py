import pytest

from codemoo.config import config
from codemoo.config.schema import BotConfig, BotRef, BotVariantConfig
from codemoo.core.bots import make_bots
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.project_bot import ProjectBot


class _MockBackend:
    async def complete(self, messages: object, tools: object = None) -> str:
        return ""


async def _bots() -> list:
    bots, _ = await make_bots(
        _MockBackend(),
        cfg=config.bots,
        bot_refs=config.scripts["default"].bots,
    )
    return bots


@pytest.mark.asyncio
async def test_make_bots_returns_ten_bots() -> None:
    assert len(await _bots()) == 10


@pytest.mark.asyncio
async def test_make_bots_first_is_echo_bot() -> None:
    assert isinstance((await _bots())[0], EchoBot)


@pytest.mark.asyncio
async def test_make_bots_last_is_project_bot() -> None:
    assert isinstance((await _bots())[-1], ProjectBot)


@pytest.mark.asyncio
async def test_make_bots_resolved_configs_carry_variant_prompts() -> None:
    """Resolved configs must surface prompts from the active BotVariantConfig."""
    mock_bots: dict = {
        "EchoBot": BotConfig(
            name="Coco",
            emoji="PARROT",
            sources=["echo_bot.py"],
            variants={
                "default": BotVariantConfig(
                    description="A mirror.",
                    prompts=["Prompt A", "Prompt B"],
                )
            },
        )
    }
    _, resolved = await make_bots(
        _MockBackend(),
        cfg=mock_bots,
        bot_refs=[BotRef(type="EchoBot", variant="default")],
    )
    assert resolved[0].prompts == ["Prompt A", "Prompt B"]
