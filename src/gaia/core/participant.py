"""Protocol and built-in participant types for the chat loop."""

from typing import Protocol, runtime_checkable

from gaia.core.message import ChatMessage


@runtime_checkable
class ChatParticipant(Protocol):
    """Structural protocol that every participant must satisfy."""

    @property
    def name(self) -> str:
        """Return the participant's display name."""
        ...

    @property
    def emoji(self) -> str:
        """Return the participant's display emoji."""
        ...

    @property
    def is_human(self) -> bool:
        """Return True if this participant represents the human user."""
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

    @property
    def emoji(self) -> str:
        """Return the human's display emoji."""
        return "\N{ADULT}"

    @property
    def is_human(self) -> bool:
        """Return True — this participant is the human user."""
        return True

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:  # noqa: ARG002
        """Return None — the human replies via the keyboard, not programmatically."""
        return None
