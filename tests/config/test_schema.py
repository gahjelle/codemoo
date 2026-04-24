"""Tests for config schema validators."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from codemoo.config.schema import (
    BackendConfig,
    BotConfig,
    CodemooConfig,
    ModelsConfig,
    PathsConfig,
)


def _bot_config(**kwargs: object) -> BotConfig:
    defaults = {"name": "X", "emoji": "PARROT", "description": "", "sources": []}
    return BotConfig(**defaults | kwargs)


def test_emoji_resolved_from_unicode_name() -> None:
    cfg = _bot_config(emoji="PARROT")
    assert cfg.emoji == "🦜"


def test_invalid_emoji_name_raises() -> None:
    with pytest.raises(ValidationError):
        _bot_config(emoji="NOT_A_REAL_EMOJI")


def test_unknown_bot_type_key_raises(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        CodemooConfig(
            language="English",
            paths=PathsConfig(bots_dir=tmp_path),
            bots={
                "UnknownBot": BotConfig(
                    name="X", emoji="PARROT", description="", sources=[]
                )
            },
            models=ModelsConfig(
                backend="mistral",
                fallbacks=["mistral"],
                backends={"mistral": BackendConfig(model_name="m")},
            ),
        )
