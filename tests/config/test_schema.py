"""Tests for config schema validators."""

import pytest
from pydantic import ValidationError

from codemoo.config.schema import (
    BotConfig,
    BotRef,
    BotVariantConfig,
    ModeName,
    ResolvedBotConfig,
    StrictModel,
    resolve,
)


class _MainBotHolder(StrictModel):
    """Minimal model to test main_bot field validation in isolation."""

    main_bot: dict[ModeName, BotRef]


def _variant(**kwargs: object) -> BotVariantConfig:
    defaults: dict[str, object] = {"description": "A bot."}
    return BotVariantConfig(**defaults | kwargs)


def _bot_config(**kwargs: object) -> BotConfig:
    defaults: dict[str, object] = {
        "name": "X",
        "emoji": "PARROT",
        "sources": [],
        "variants": {"default": _variant()},
    }
    return BotConfig(**defaults | kwargs)


def test_emoji_resolved_from_unicode_name() -> None:
    cfg = _bot_config(emoji="PARROT")
    assert cfg.emoji == "🦜"


def test_invalid_emoji_name_raises() -> None:
    with pytest.raises(ValidationError):
        _bot_config(emoji="NOT_A_REAL_EMOJI")


def test_bot_config_rejects_type_field() -> None:
    with pytest.raises(ValidationError):
        BotConfig(
            type="EchoBot",  # ty: ignore[unknown-argument]
            name="X",
            emoji="PARROT",
            sources=[],
            variants={"default": _variant()},
        )


def test_bot_config_rejects_empty_variants() -> None:
    with pytest.raises(ValidationError):
        _bot_config(variants={})


def test_bot_variant_config_tools_default_to_empty() -> None:
    v = _variant()
    assert v.tools == []


def test_bot_variant_config_prompts_default_to_empty() -> None:
    v = _variant()
    assert v.prompts == []


def test_bot_variant_config_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        BotVariantConfig(description="ok", unknown_field="bad")  # ty: ignore[unknown-argument]


def test_bot_ref_parses_type_and_variant() -> None:
    ref = BotRef(type="EchoBot", variant="default")
    assert ref.type == "EchoBot"
    assert ref.variant == "default"


def test_bot_ref_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        BotRef(type="UnknownBot", variant="default")  # type: ignore[arg-type]


def test_resolve_merges_identity_and_variant() -> None:
    bots = {
        "EchoBot": BotConfig(
            name="Coco",
            emoji="PARROT",
            sources=["echo_bot.py"],
            variants={
                "default": BotVariantConfig(
                    description="A mirror.", tools=[], prompts=["Hi"]
                )
            },
        )
    }
    ref = BotRef(type="EchoBot", variant="default")
    result = resolve(bots, ref)  # type: ignore[arg-type]
    assert isinstance(result, ResolvedBotConfig)
    assert result.bot_type == "EchoBot"
    assert result.name == "Coco"
    assert result.description == "A mirror."
    assert result.prompts == ["Hi"]


def test_main_bot_parses_per_mode_bot_refs() -> None:
    holder = _MainBotHolder(
        main_bot={
            "code": {"type": "GuardBot", "variant": "code"},
            "business": {"type": "GuardBot", "variant": "business"},
        }
    )
    assert holder.main_bot["code"].type == "GuardBot"
    assert holder.main_bot["code"].variant == "code"
    assert holder.main_bot["business"].variant == "business"


def test_main_bot_rejects_invalid_bot_type() -> None:
    with pytest.raises(ValidationError):
        _MainBotHolder(main_bot={"code": {"type": "UnknownBot", "variant": "code"}})


def test_main_bot_rejects_bare_string() -> None:
    with pytest.raises(ValidationError):
        _MainBotHolder(main_bot="GuardBot")  # type: ignore[arg-type]


def test_resolve_raises_for_unknown_variant() -> None:
    bots = {
        "EchoBot": BotConfig(
            name="Coco",
            emoji="PARROT",
            sources=[],
            variants={"default": _variant()},
        )
    }
    ref = BotRef(type="EchoBot", variant="nonexistent")
    with pytest.raises(KeyError):
        resolve(bots, ref)  # type: ignore[arg-type]
