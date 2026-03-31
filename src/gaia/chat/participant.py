"""Protocol and built-in participant types for the chat loop."""

from typing import Protocol, runtime_checkable

from gaia.chat.message import ChatMessage


@runtime_checkable
class ChatParticipant(Protocol):
    """Structural protocol that every participant must satisfy."""

    @property
    def name(self) -> str:
        """Return the participant's display name."""
        ...

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:
        """Receive a message and optionally return a reply."""
        ...


class HumanParticipant:
    """Represents the human user in the participant slot system.

    The human's messages originate from keyboard input in the UI, not from
    on_message. This participant exists so the human has a named slot and
    receives dispatched messages, but always returns None (no programmatic reply).
    """

    @property
    def name(self) -> str:
        """Return the human's display name."""
        return "You"

    async def on_message(self, _message: ChatMessage) -> ChatMessage | None:
        """Return None — the human replies via the keyboard, not programmatically."""
        return None
