"""Tests for config schema validators."""

import pytest
from pydantic import ValidationError

from codemoo.config.schema import (
    BackendConfig,
    BotConfig,
    BotRef,
    BotVariantConfig,
    ModelsConfig,
    ResolvedBotConfig,
    resolve,
)

# ---------------------------------------------------------------------------
# ModelsConfig.backend — empty-string sentinel normalised to None
# ---------------------------------------------------------------------------


def _models_config(**kwargs: object) -> ModelsConfig:
    defaults: dict[str, object] = {
        "fallbacks": ["mistral"],
        "backends": {"mistral": BackendConfig(model_name="mistral-small-latest")},
    }
    return ModelsConfig(**defaults | kwargs)


def test_models_config_backend_defaults_to_none() -> None:
    cfg = _models_config()
    assert cfg.backend is None


def test_models_config_backend_empty_string_becomes_none() -> None:
    cfg = _models_config(backend="")
    assert cfg.backend is None


def test_models_config_backend_accepts_valid_backend_name() -> None:
    cfg = _models_config(backend="mistral")
    assert cfg.backend == "mistral"


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
    with pytest.raises(ValueError, match="Unknown variant"):
        resolve(bots, ref)  # type: ignore[arg-type]


def test_resolve_error_message_contains_variant_info() -> None:
    bots = {
        "EchoBot": BotConfig(
            name="Coco",
            emoji="PARROT",
            sources=[],
            variants={
                "zebra": _variant(),
                "alpha": _variant(),
                "beta": _variant(),
            },
        )
    }
    ref = BotRef(type="EchoBot", variant="bad")
    with pytest.raises(ValueError, match="Unknown variant") as exc_info:
        resolve(bots, ref)  # type: ignore[arg-type]

    msg = str(exc_info.value)
    assert "bad" in msg
    assert "EchoBot" in msg
    assert "alpha" in msg
    assert "beta" in msg
    assert "zebra" in msg


# ---------------------------------------------------------------------------
# BotVariantConfig.capabilities
# ---------------------------------------------------------------------------


def test_bot_variant_config_capabilities_default_to_empty() -> None:
    v = _variant()
    assert v.capabilities == []


def test_bot_variant_config_accepts_valid_capability() -> None:
    v = _variant(capabilities=["context_management"])
    assert v.capabilities == ["context_management"]


def test_bot_variant_config_rejects_unknown_capability() -> None:
    with pytest.raises(ValidationError):
        _variant(capabilities=["does_not_exist"])


# ---------------------------------------------------------------------------
# ResolvedBotConfig.capabilities propagation
# ---------------------------------------------------------------------------


def _bots_with_capability(capabilities: list[str]) -> dict:  # type: ignore[type-arg]
    return {
        "EchoBot": BotConfig(
            name="Coco",
            emoji="PARROT",
            sources=[],
            variants={
                "default": BotVariantConfig(
                    description="A bot.",
                    capabilities=capabilities,  # type: ignore[arg-type]
                )
            },
        )
    }


def test_resolve_threads_capabilities_through() -> None:
    bots = _bots_with_capability(["context_management"])
    result = resolve(bots, BotRef(type="EchoBot", variant="default"))  # type: ignore[arg-type]
    assert result.capabilities == ["context_management"]


def test_resolve_threads_empty_capabilities_through() -> None:
    bots = _bots_with_capability([])
    result = resolve(bots, BotRef(type="EchoBot", variant="default"))  # type: ignore[arg-type]
    assert result.capabilities == []
