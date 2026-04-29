"""Context-aware LLM bot with a fixed system prompt."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class SystemBot:
    """Chat participant that injects a system prompt into every LLM context.

    Identical to ChatBot except that it prepends a fixed system-role message,
    giving the LLM a persona or behavioral instructions it cannot override.
    """

    name: str
    emoji: str
    backend: LLMBackend
    instructions: str
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using conversation history prefixed by the system prompt."""
        context = [
            Message(role="system", content=self.instructions),
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
