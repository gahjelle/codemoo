"""LLM backend port: types, protocol, and pure context-building function."""

import dataclasses
from typing import Literal, Protocol

from codemoo.core.message import ChatMessage

type Role = Literal["user", "assistant", "system"]


@dataclasses.dataclass(frozen=True)
class Message:
    """Immutable message in an LLM conversation context."""

    role: Role
    content: str


class LLMBackend(Protocol):
    """Structural protocol for LLM completion backends."""

    async def complete(self, messages: list[Message]) -> str:
        """Send messages to the LLM and return the response text."""
        ...


def build_llm_context(
    history: list[ChatMessage],
    current: ChatMessage,
    bot_name: str,
    human_name: str,
    max_messages: int,
) -> list[Message]:
    """Build a filtered, clipped Message list for an LLM completion call.

    Pure function: filters history to human + bot messages, clips to the most
    recent max_messages, maps senders to roles, then appends current as the
    final user turn.
    """
    relevant = [m for m in history if m.sender in (human_name, bot_name)]
    clipped = relevant[-max_messages:]
    messages = [
        Message(
            role="assistant" if m.sender == bot_name else "user",
            content=m.text,
        )
        for m in clipped
    ]
    messages.append(Message(role="user", content=current.text))
    return messages
