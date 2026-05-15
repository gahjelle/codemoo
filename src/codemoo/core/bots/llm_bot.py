"""Stateless LLM-powered bot that responds to each message in isolation."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)
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
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond to message using only its text; ignore context."""
        llm_messages = [Message(role="user", content=message.text)]
        response = await self.llm.complete(llm_messages)
        return [
            ContextItem(
                content=AssistantMessageContent(response),
                turn_id=next_turn_id(context),
            )
        ]
