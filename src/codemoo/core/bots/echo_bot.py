"""Simple bot that echoes every message back to the chat."""

import dataclasses
from typing import ClassVar

from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)
from codemoo.core.message import ChatMessage


@dataclasses.dataclass(eq=False)
class EchoBot:
    """A bot participant that mirrors each human message verbatim."""

    name: str
    emoji: str
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        message: ChatMessage,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Echo the message back with this bot as sender."""
        return [
            ContextItem(
                content=AssistantMessageContent(message.text),
                turn_id=next_turn_id(context),
            )
        ]
