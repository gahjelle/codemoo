"""Protocol and built-in participant types for the chat loop."""

import dataclasses
from typing import ClassVar, Protocol, runtime_checkable

from codemoo.core.context_items import ContextItem
from codemoo.core.message import ChatMessage


@runtime_checkable
class ChatParticipant(Protocol):
    """Structural protocol that every participant must satisfy."""

    name: str
    emoji: str
    is_human: ClassVar[bool]

    async def on_message(
        self, message: ChatMessage, context: list[ContextItem]
    ) -> list[ContextItem]:
        """Receive a message and return any new context items produced this turn."""
        ...


@dataclasses.dataclass(eq=False)
class HumanParticipant:
    """Represents the human user in the participant slot system.

    The human's messages originate from keyboard input in the UI, not from
    on_message. This participant exists so the human has a named slot and
    receives dispatched messages, but always returns (None, []).
    """

    name: str = "You"
    emoji: str = "\N{ADULT}"
    is_human: ClassVar[bool] = True

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        context: list[ContextItem],  # noqa: ARG002
    ) -> list[ContextItem]:
        """Return [] — the human replies via keyboard, not programmatically."""
        return []
