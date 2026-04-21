"""Simple bot that echoes every message back to the chat."""

import dataclasses
from typing import ClassVar

from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class EchoBot:
    """A bot participant that mirrors each human message verbatim."""

    name: str
    emoji: str
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Echo the message, or return None if the sender is this bot."""
        if message.sender == self.name:
            return None

        return dataclasses.replace(message, sender=self.name)
