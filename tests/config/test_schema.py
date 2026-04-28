"""Tests for config schema validators."""

import pytest
from pydantic import ValidationError

from codemoo.config.schema import BotConfig


def _bot_config(**kwargs: object) -> BotConfig:
    defaults = {
        "type": "EchoBot",
        "name": "X",
        "emoji": "PARROT",
        "description": "",
        "sources": [],
    }
    return BotConfig(**defaults | kwargs)


def test_emoji_resolved_from_unicode_name() -> None:
    cfg = _bot_config(emoji="PARROT")
    assert cfg.emoji == "🦜"


def test_invalid_emoji_name_raises() -> None:
    with pytest.raises(ValidationError):
        _bot_config(emoji="NOT_A_REAL_EMOJI")


def test_prompts_field_is_parsed() -> None:
    cfg = _bot_config(prompts=["Hello", "World"])
    assert cfg.prompts == ["Hello", "World"]


def test_prompts_defaults_to_empty_list() -> None:
    cfg = _bot_config()
    assert cfg.prompts == []


def test_unknown_bot_type_in_botconfig_raises() -> None:
    with pytest.raises(ValidationError):
        BotConfig(
            type="UnknownBotClass",  # type: ignore[arg-type]
            name="X",
            emoji="PARROT",
            description="",
            sources=[],
        )
