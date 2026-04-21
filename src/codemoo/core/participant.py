"""Protocol and built-in participant types for the chat loop."""

import dataclasses
from typing import ClassVar, Protocol, runtime_checkable

from codemoo.core.message import ChatMessage


@runtime_checkable
class ChatParticipant(Protocol):
    """Structural protocol that every participant must satisfy."""

    name: str
    emoji: str
    is_human: ClassVar[bool]

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Receive a message and optionally return a reply."""
        ...


@dataclasses.dataclass(eq=False)
class HumanParticipant:
    """Represents the human user in the participant slot system.

    The human's messages originate from keyboard input in the UI, not from
    on_message. This participant exists so the human has a named slot and
    receives dispatched messages, but always returns None (no programmatic reply).
    """

    name: str = "You"
    emoji: str = "\N{ADULT}"
    is_human: ClassVar[bool] = True

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Return None — the human replies via the keyboard, not programmatically."""
        return None
