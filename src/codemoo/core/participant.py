"""Protocol and built-in participant types for the chat loop."""

import dataclasses
from typing import Protocol, runtime_checkable

from codemoo.core.context_items import ContextItem


@runtime_checkable
class ChatParticipant(Protocol):
    """Structural protocol that every participant must satisfy."""

    name: str
    emoji: str

    async def on_message(self, context: list[ContextItem]) -> list[ContextItem]:
        """Receive context and return any new context items produced this turn.

        Precondition: context is non-empty and context[-1] is the triggering
        message for this turn. The dispatch shell guarantees this invariant.
        """
        ...


@dataclasses.dataclass
class HumanParticipant:
    """Display metadata for the human user — name and emoji only."""

    name: str = "You"
    emoji: str = "\N{ADULT}"
