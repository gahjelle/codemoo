"""Context-aware LLM bot that maintains conversation history."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class ChatBot:
    """Chat participant that maintains conversation context.

    Prepends history to the current message before sending to the LLM.
    Stateless — history is injected by the shell.
    """

    name: str
    emoji: str
    backend: LLMBackend
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using conversation history."""
        context = [
            *[
                Message(
                    role="assistant" if m.sender == self.name else "user",
                    content=m.text,
                )
                for m in history
            ],
            Message(role="user", content=message.text),
        ]
        response = await self.backend.complete(context)
        return ChatMessage(sender=self.name, text=response)
