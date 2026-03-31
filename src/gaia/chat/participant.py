from typing import Protocol, runtime_checkable

from gaia.chat.message import ChatMessage


@runtime_checkable
class ChatParticipant(Protocol):
    @property
    def name(self) -> str: ...

    async def on_message(self, message: ChatMessage) -> ChatMessage | None: ...


class HumanParticipant:
    """Represents the human user in the participant slot system.

    The human's messages originate from keyboard input in the UI, not from
    on_message. This participant exists so the human has a named slot and
    receives dispatched messages, but always returns None (no programmatic reply).
    """

    @property
    def name(self) -> str:
        return "You"

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:
        return None
