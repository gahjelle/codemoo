"""Context-aware LLM bot with a fixed system prompt."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, build_llm_context
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
    human_name: str
    instructions: str
    max_messages: int = 20
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using filtered conversation history prefixed by the system prompt."""
        context = build_llm_context(
            history,
            message,
            bot_name=self.name,
            human_name=self.human_name,
            max_messages=self.max_messages,
            system=self.instructions,
        )
        response = await self.backend.complete(context)
        return ChatMessage(sender=self.name, text=response)
