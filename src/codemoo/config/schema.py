"""Pydantic schema for the Codemoo TOML configuration."""

import dataclasses
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


class BotVariantConfig(StrictModel):
    """Profile-specific settings for one bot variant."""

    description: str
    tools: list[str] = []
    prompts: list[str] = []


class BotConfig(StrictModel):
    """Stable identity for one bot type."""

    name: str
    emoji: str
    sources: list[str]
    variants: dict[str, BotVariantConfig]

    @field_validator("emoji", mode="before")
    @classmethod
    def resolve_emoji(cls, v: str) -> str:
        """Resolve a Unicode character name (e.g. 'PARROT') to its character."""
        try:
            return unicodedata.lookup(v)
        except KeyError:
            msg = f"Unknown Unicode character name: {v!r}"
            raise ValueError(msg) from None

    @field_validator("variants")
    @classmethod
    def variants_not_empty(
        cls, v: dict[str, BotVariantConfig]
    ) -> dict[str, BotVariantConfig]:
        """Require at least one variant."""
        if not v:
            msg = "variants must have at least one entry"
            raise ValueError(msg)
        return v


class BotRef(StrictModel):
    """Reference to a specific bot type and variant."""

    type: BotType
    variant: str


@dataclasses.dataclass
class ResolvedBotConfig:
    """Merged bot identity + variant, produced at runtime — never parsed from TOML."""

    bot_type: BotType
    name: str
    emoji: str
    sources: list[str]
    description: str
    tools: list[str]
    prompts: list[str]


def resolve(bots: dict[BotType, BotConfig], ref: BotRef) -> ResolvedBotConfig:
    """Merge a BotConfig and one of its BotVariantConfigs into a ResolvedBotConfig."""
    cfg = bots[ref.type]
    variant = cfg.variants[ref.variant]
    return ResolvedBotConfig(
        bot_type=ref.type,
        name=cfg.name,
        emoji=cfg.emoji,
        sources=cfg.sources,
        description=variant.description,
        tools=variant.tools,
        prompts=variant.prompts,
    )


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
    bots: list[BotRef]


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
    bots: dict[BotType, BotConfig]
    scripts: dict[ScriptName, ScriptConfig]
    models: ModelsConfig
    m365: M365Config
