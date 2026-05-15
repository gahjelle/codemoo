"""Simple bot that echoes every message back to the chat."""

import dataclasses
from typing import ClassVar

from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    next_turn_id,
)


@dataclasses.dataclass(eq=False)
class EchoBot:
    """A bot participant that mirrors each human message verbatim."""

    name: str
    emoji: str
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Echo the triggering message back. context[-1] is always the trigger."""
        return [
            ContextItem(
                content=AssistantMessageContent(context[-1].content.text),  # ty: ignore[unresolved-attribute]
                turn_id=next_turn_id(context),
            )
        ]
