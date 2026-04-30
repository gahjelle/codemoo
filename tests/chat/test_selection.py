"""Tests for SelectionApp's pure helper functions."""

from codemoo.chat.selection import _bot_label
from codemoo.config.schema import ResolvedBotConfig


def _resolved(
    *,
    bot_type: str = "EchoBot",
    name: str = "Coco",
    emoji: str = "\N{PARROT}",
    variant: str = "default",
) -> ResolvedBotConfig:
    return ResolvedBotConfig(
        bot_type=bot_type,  # type: ignore[arg-type]
        name=name,
        emoji=emoji,
        variant=variant,
        sources=[],
        description="",
        tools=[],
        prompts=[],
        instructions="",
    )


def test_label_includes_name_type_and_variant() -> None:
    bot = _resolved(
        bot_type="LlmBot", name="Mono", emoji="\N{SPARKLES}", variant="default"
    )
    assert _bot_label(bot) == "\N{SPARKLES} Mono (LlmBot) \N{BULLET} default"


def test_label_echo_bot() -> None:
    bot = _resolved(
        bot_type="EchoBot", name="Coco", emoji="\N{PARROT}", variant="default"
    )
    assert _bot_label(bot) == "\N{PARROT} Coco (EchoBot) \N{BULLET} default"


def test_label_guard_bot_business_variant() -> None:
    bot = _resolved(
        bot_type="GuardBot", name="Cato", emoji="\N{LOCK}", variant="business"
    )
    assert _bot_label(bot) == "\N{LOCK} Cato (GuardBot) \N{BULLET} business"
