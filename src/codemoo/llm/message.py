"""Immutable value type for LLM chat messages."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class LLMMessage:
    """An immutable message in an LLM conversation context."""

    role: Literal["user", "assistant", "system"]
    content: str
