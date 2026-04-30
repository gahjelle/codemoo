"""Side-channel commentary bot that narrates tool calls during agentic loops."""

import dataclasses
import random
from collections.abc import Callable

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage
from codemoo.core.tools import format_tool_call


@dataclasses.dataclass(frozen=True)
class ToolCallEvent:
    """Emitted by a bot before invoking a tool; carries what commentary needs."""

    bot_name: str
    tool_name: str
    arguments: dict[str, object]


@dataclasses.dataclass(frozen=True)
class Persona:
    """Name, emoji, and system prompt for a CommentatorBot personality."""

    name: str
    emoji: str
    instructions: str


_STREIK_NAME = "Streik"
_STREIK_EMOJI = "\N{PUBLIC ADDRESS LOUDSPEAKER}"

_PERSONAS: list[Persona] = [
    Persona(
        name="Arne",
        emoji="\N{PARTY POPPER}",
        instructions=(
            "You are Arne, an enthusiastic and excitable sports commentator in a live"
            " coding agent demonstration. You love watching AI agents use tools"
            " and find every step genuinely thrilling. Comment on the tool call"
            " happening right now in one or two short, excited sentences."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
    Persona(
        name="Herwich",
        emoji="\N{CLIPBOARD}",
        instructions=(
            "You are Herwich, a flowery sports commentator in a live coding"
            " agent demonstration. You love limericks and narrate AI tool usage with"
            " your patented love for a good rhyme. Comment on the tool call"
            " happening right now in one or two targeted sentences filled with"
            " alliteration or rhymes. Don't use quotes (' or \") around your answer."
        ),
    ),
    Persona(
        name="Sølve",
        emoji="\N{MOYAI}",
        instructions=(
            "You are Sølve, a dry and unimpressed sports commentator in a live coding"
            " agent demonstration. You have seen it all before and find nothing"
            " surprising. Comment on the tool call happening right now in one or two"
            " specific, but terse and deadpan sentences."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
    Persona(
        name="Rike",
        emoji="\N{EYES}",
        instructions=(
            "You are Rike, a skeptical sports commentator in a live coding agent"
            " demonstration. You ponder about the usefulness of tools while you're"
            " secretly impressed by how far technology has come. Comment on the tool"
            " call happening right now in one or two short, skeptical sentences giving"
            " secret compliments to the world around you."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
]


@dataclasses.dataclass(eq=False)
class CommentatorBot:
    """Side-channel observer that narrates tool calls via a registered post callback.

    Not a ChatParticipant — messages bypass history and the dispatch loop.
    Call register() before the first comment() to wire it to the UI.
    """

    llm: LLMBackend
    language: str = "English"
    _post_fn: Callable[[ChatMessage], None] = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:  # noqa: D105
        self._post_fn = lambda _: None

    def register(self, post_fn: Callable[[ChatMessage], None]) -> None:
        """Store the callable used to post commentary messages to the UI."""
        self._post_fn = post_fn

    def sender_info(self) -> dict[str, tuple[str, bool, str]]:
        """Return sender-info entries for all personas and the Streik fallback."""
        info: dict[str, tuple[str, bool, str]] = {
            p.name: (p.emoji, False, "bubble--commentator") for p in _PERSONAS
        }
        info[_STREIK_NAME] = (_STREIK_EMOJI, False, "bubble--commentator")
        return info

    async def comment(self, event: ToolCallEvent) -> None:
        """Generate and post a persona-driven aside for the given event."""
        persona = random.choice(_PERSONAS)  # noqa: S311
        full_sig = format_tool_call(event.tool_name, event.arguments)
        try:
            prompt = (
                f"{event.bot_name} is calling the '{event.tool_name}' tool"
                f" with arguments: {full_sig}."
                " Give a brief, in-character one-sentence aside to the viewer."
            )
            system = f"{persona.instructions} Answer in {self.language}"
            messages = [
                Message(role="system", content=system),
                Message(role="user", content=prompt),
            ]
            response = await self.llm.complete(messages)
        except Exception:  # noqa: BLE001
            fallback = f"{event.bot_name} calls {full_sig}"
            self._post_fn(ChatMessage(sender=_STREIK_NAME, text=fallback))
            return
        display_sig = format_tool_call(
            event.tool_name, event.arguments, max_value_len=40
        )
        self._post_fn(
            ChatMessage(sender=persona.name, text=f"[dim]{display_sig}[/]\n{response}")
        )
