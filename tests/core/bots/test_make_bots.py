from codemoo.config import config
from codemoo.config.schema import BotConfig, BotRef, BotVariantConfig
from codemoo.core.backend import TextResponse, ToolUse
from codemoo.core.bots import make_bots
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.guard_bot import GuardBot


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return ""

    async def complete_step(
        self, messages: object, tools: object
    ) -> TextResponse | ToolUse:
        return TextResponse(text="")


def _bots() -> list:
    bots, _ = make_bots(
        _MockBackend(),
        human_name="You",
        cfg=config.bots,
        bot_refs=config.scripts["default"].bots,
    )
    return bots


def test_make_bots_returns_nine_bots() -> None:
    assert len(_bots()) == 9


def test_make_bots_first_is_echo_bot() -> None:
    assert isinstance(_bots()[0], EchoBot)


def test_make_bots_last_is_guard_bot() -> None:
    assert isinstance(_bots()[-1], GuardBot)


def test_make_bots_resolved_configs_carry_variant_prompts() -> None:
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
    _, resolved = make_bots(
        _MockBackend(),
        human_name="You",
        cfg=mock_bots,
        bot_refs=[BotRef(type="EchoBot", variant="default")],
    )
    assert resolved[0].prompts == ["Prompt A", "Prompt B"]
