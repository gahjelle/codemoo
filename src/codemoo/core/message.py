"""Immutable value type representing a single chat message."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ChatMessage:
    """An immutable record of one message sent by a named participant."""

    sender: str
    text: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    thinking_time: int | None = None
