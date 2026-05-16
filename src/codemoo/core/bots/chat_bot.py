"""Context-aware LLM bot that maintains conversation history."""

import dataclasses

from codemoo.core.backend import LLMBackend
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)


@dataclasses.dataclass(eq=False)
class ChatBot:
    """Chat participant that maintains conversation context.

    Uses build_context(context) to construct LLM input from the full context list.
    Stateless — context is injected by the shell.
    """

    name: str
    emoji: str
    llm: LLMBackend

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond using conversation context."""
        response = await self.llm.complete(build_context(context))
        return [
            ContextItem(
                content=AssistantMessageContent(response),
                turn_id=next_turn_id(context),
            )
        ]
