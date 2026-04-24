"""Pydantic schema for the Codemoo TOML configuration."""

import unicodedata
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

type BotType = Literal[
    "EchoBot",
    "LlmBot",
    "ChatBot",
    "SystemBot",
    "ToolBot",
    "FileBot",
    "ShellBot",
    "AgentBot",
]
type ModelBackend = Literal["mistral", "anthropic", "openrouter"]


class StrictModel(BaseModel):
    """Enforce all fields exactly."""

    model_config = ConfigDict(extra="forbid")


class PathsConfig(StrictModel):
    """Configure paths."""

    bots_dir: Path


class BotConfig(StrictModel):
    """Configure one bot."""

    name: str
    emoji: str
    description: str
    sources: list[str]
    prompts: list[str] = []

    @field_validator("emoji", mode="before")
    @classmethod
    def resolve_emoji(cls, v: str) -> str:
        """Resolve a Unicode character name (e.g. 'PARROT') to its character."""
        try:
            return unicodedata.lookup(v)
        except KeyError:
            msg = f"Unknown Unicode character name: {v!r}"
            raise ValueError(msg) from None


class BackendConfig(StrictModel):
    """Configure one LLM backend."""

    model_name: str


class ModelsConfig(StrictModel):
    """Configure all LLM backends."""

    backend: ModelBackend
    fallbacks: list[ModelBackend]
    backends: dict[ModelBackend, BackendConfig]


class CodemooConfig(StrictModel):
    """Full configuration of Codemoo."""

    language: str
    paths: PathsConfig
    bots: dict[BotType, BotConfig]
    models: ModelsConfig
