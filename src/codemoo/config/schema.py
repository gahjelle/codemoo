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
    "ReadBot",
    "ChangeBot",
    "AgentBot",
    "GuardBot",
    "ScanBot",
    "SendBot",
]
type ScriptName = Literal["default", "focused", "m365", "m365_lite"]
type ModeName = Literal["code", "business"]
type ModelBackend = Literal["mistral", "anthropic", "openrouter"]


class StrictModel(BaseModel):
    """Enforce all fields exactly."""

    model_config = ConfigDict(extra="forbid")


class PathsConfig(StrictModel):
    """Configure paths."""

    bots_dir: Path
    m365_token_path: Path


class BotConfig(StrictModel):
    """Configure one bot."""

    type: BotType
    name: str
    emoji: str
    description: str
    sources: list[str]
    tools: list[str] = []
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


class ScriptConfig(StrictModel):
    """Configure one demo script."""

    mode: ModeName
    bots: list[str]


class M365Config(StrictModel):
    """Configure Microsoft 365 / Graph API access."""

    tenant_id: str
    client_id: str
    sharepoint_host: str
    sharepoint_site: str
    graph_base_url: str


class CodemooConfig(StrictModel):
    """Full configuration of Codemoo."""

    language: str
    main_bot: BotType
    paths: PathsConfig
    bots: dict[str, BotConfig]
    scripts: dict[ScriptName, ScriptConfig]
    models: ModelsConfig
    m365: M365Config
