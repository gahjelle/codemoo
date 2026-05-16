"""Stateless LLM-powered bot that responds to each message in isolation."""

import dataclasses

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)


@dataclasses.dataclass(eq=False)
class LlmBot:
    """Chat participant that responds using only the current message.

    The full conversation history is ignored; only the triggering message
    is sent to the LLM. Intended for demonstration purposes.
    """

    name: str
    emoji: str
    llm: LLMBackend

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond to context[-1] only; ignore earlier history."""
        llm_messages = [Message(role="user", content=context[-1].content.text)]  # ty: ignore[unresolved-attribute]
        response = await self.llm.complete(llm_messages)
        return [
            ContextItem(
                content=AssistantMessageContent(response),
                turn_id=next_turn_id(context),
            )
        ]
