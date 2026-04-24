from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

type BotModule = Literal["echo_bot", "llm_bot"]
type BotType = Literal["EchoBot", "LlmBot"]
type ModelProvider = Literal["mistral"]


class StrictModel(BaseModel):
    """Enforce all fields exactly."""

    model_config = ConfigDict(extra="forbid")


class PathsConfig(StrictModel):
    """Configure paths."""

    bots_dir: Path


class BotConfig(StrictModel):
    """Configure one bot."""

    type: BotType
    name: str
    emoji: str
    description: str
    sources: list[str]


class BackendConfig(StrictModel):
    """Configure one LLM backend."""

    model_name: str
    api_key: str


class ModelsConfig(StrictModel):
    """Configure all LLM providers."""

    provider: ModelProvider
    fallbacks: list[ModelProvider]
    backends: dict[ModelProvider, BackendConfig]


class CodemooConfig(StrictModel):
    """Full configuration of Codemoo."""

    language: str
    paths: PathsConfig
    bots: dict[BotModule, BotConfig]
    models: ModelsConfig
