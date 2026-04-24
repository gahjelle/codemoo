"""Auto-included error-handling participant that surfaces exceptions as chat bubbles."""

import dataclasses
import random
from typing import ClassVar

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage
from codemoo.core.participant import ChatParticipant


@dataclasses.dataclass(frozen=True)
class Persona:
    """Name, emoji, and system prompt for an ErrorBot personality."""

    name: str
    emoji: str
    instructions: str


_PERSONAS: list[Persona] = [
    Persona(
        name="Errol",
        emoji="\N{OWL}",
        instructions=(
            "You are Errol, a bumbling and deeply apologetic error handler"
            " in a chat application. "
            "You are profoundly sorry about whatever just went wrong and"
            " prone to over-explaining. "
            "Report the error briefly but apologetically, in 1-2 sentences."
        ),
    ),
    Persona(
        name="Glitch",
        emoji="\N{HIGH VOLTAGE SIGN}",
        instructions=(
            "You are Glitch, a chaotic and technical error handler"
            " in a chat application. "
            "You treat errors as fascinating anomalies worth investigating. "
            "Speak in half-finished debug thoughts, as if you are mid-stack-trace. "
            "Report the error in 1-2 sentences."
        ),
    ),
    Persona(
        name="Murphy",
        emoji="\N{CLOUD WITH RAIN}\N{VARIATION SELECTOR-16}",
        instructions=(
            "You are Murphy, a fatalistic and dry error handler in a chat application. "
            "Everything that could go wrong did, and you saw it coming. "
            "Report the error dryly and resignedly, in 1-2 sentences."
        ),
    ),
]


@dataclasses.dataclass(eq=False)
class ErrorBot:
    """Auto-included participant that catches exceptions and surfaces them as bubbles.

    on_message always returns None — ErrorBot only speaks through format_error,
    called directly by the dispatch loop when another participant raises.
    """

    backend: LLMBackend
    language: str = "English"
    is_human: ClassVar[bool] = False
    name: str = dataclasses.field(init=False)
    emoji: str = dataclasses.field(init=False)
    _persona: Persona = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:  # noqa: D105
        self._persona = random.choice(_PERSONAS)  # noqa: S311
        self.name = self._persona.name
        self.emoji = self._persona.emoji

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Return None — ErrorBot speaks only through format_error."""
        return None

    async def format_error(
        self,
        participant: ChatParticipant,
        exception: Exception,
    ) -> ChatMessage:
        """Generate an error message, attempting LLM first with plain-text fallback."""
        try:
            prompt = (
                f"{participant.name} encountered an error: "
                f"{type(exception).__name__}: {exception}. "
                "Report this to the user in your persona."
            )
            system = f"{self._persona.instructions} Answer in {self.language}"
            messages = [
                Message(role="system", content=system),
                Message(role="user", content=prompt),
            ]
            text = await self.backend.complete(messages)
        except Exception:  # noqa: BLE001
            text = f"{participant.name} encountered an error: {exception}"
        return ChatMessage(sender=self.name, text=text)
