"""Context-aware LLM bot that maintains conversation history."""

import dataclasses
from datetime import UTC, datetime
from typing import ClassVar

from codemoo.core.backend import LLMBackend, build_llm_context
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class ChatBot:
    """Chat participant that maintains conversation context.

    Filters history to human + self messages only and clips to max_messages
    before sending to the LLM. Stateless — history is injected by the shell.
    """

    name: str
    emoji: str
    backend: LLMBackend
    human_name: str
    max_messages: int = 20
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using filtered conversation history."""
        if message.sender == self.name:
            return None
        context = build_llm_context(
            history, message, self.name, self.human_name, self.max_messages
        )
        response = await self.backend.complete(context)
        return ChatMessage(
            sender=self.name,
            text=response,
            timestamp=datetime.now(tz=UTC),
        )
