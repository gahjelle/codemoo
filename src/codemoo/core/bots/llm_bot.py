"""Stateless LLM-powered bot that responds to each message in isolation."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class LlmBot:
    """Chat participant that responds using only the current message.

    The full conversation history is ignored; only the triggering message
    is sent to the LLM. Intended for demonstration purposes.
    """

    name: str
    emoji: str
    llm: LLMBackend
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Respond to message using only its text; ignore history."""
        context = [Message(role="user", content=message.text)]
        response = await self.llm.complete(context)
        return ChatMessage(sender=self.name, text=response)
