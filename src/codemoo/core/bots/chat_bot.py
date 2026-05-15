"""Context-aware LLM bot that maintains conversation history."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class ChatBot:
    """Chat participant that maintains conversation context.

    Uses build_context(context) to construct LLM input from the full context list.
    Stateless — context is injected by the shell.
    """

    name: str
    emoji: str
    llm: LLMBackend
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, context: list[ContextItem]  # noqa: ARG002
    ) -> tuple[ChatMessage | None, list[ContextItem]]:
        """Respond using conversation context."""
        response = await self.llm.complete(build_context(context))
        reply = ChatMessage(sender=self.name, text=response)
        new_item = ContextItem(
            content=AssistantMessageContent(reply.text),
            turn_id=next_turn_id(context),
        )
        return reply, [new_item]
