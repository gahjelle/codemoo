"""Context-aware LLM bot with a fixed system prompt."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class SystemBot:
    """Chat participant that injects a system prompt into every LLM context.

    Identical to ChatBot except that it prepends a fixed system-role message,
    giving the LLM a persona or behavioral instructions it cannot override.
    """

    name: str
    emoji: str
    llm: LLMBackend
    instructions: str
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond using conversation context prefixed by the system prompt."""
        messages = [
            Message(role="system", content=self.instructions),
            *build_context(context),
        ]
        response = await self.llm.complete(messages)
        return [
            ContextItem(
                content=AssistantMessageContent(response),
                turn_id=next_turn_id(context),
            )
        ]
