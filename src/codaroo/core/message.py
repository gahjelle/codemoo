"""Immutable value type representing a single chat message."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChatMessage:
    """An immutable record of one message sent by a named participant."""

    sender: str
    text: str
    timestamp: datetime
