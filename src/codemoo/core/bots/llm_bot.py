"""Stateless LLM-powered bot that responds to each message in isolation."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class LLMBot:
    """Chat participant that responds using only the current message.

    The full conversation history is ignored; only the triggering message
    is sent to the LLM. Intended for demonstration purposes.
    """

    name: str
    emoji: str
    backend: LLMBackend
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Respond to message using only its text; ignore history."""
        if message.sender == self.name:
            return None
        response = await self.backend.complete(
            [Message(role="user", content=message.text)]
        )
        return dataclasses.replace(message, sender=self.name, text=response)
