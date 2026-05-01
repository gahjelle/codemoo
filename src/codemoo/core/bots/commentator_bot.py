"""Side-channel commentary bot that narrates tool calls during agentic loops."""

import dataclasses
import random
from collections.abc import Callable

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.context import ContextLoadEvent
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

    async def comment(self, event: ToolCallEvent | ContextLoadEvent) -> None:
        """Generate and post a persona-driven aside for the given event."""
        if isinstance(event, ToolCallEvent):
            await self._comment_on_tool_call(event)
        elif isinstance(event, ContextLoadEvent):
            await self._comment_on_context(event)

    async def _comment_on_tool_call(self, event: ToolCallEvent) -> None:
        """Generate commentary about a tool call."""
        full_sig = format_tool_call(event.tool_name, event.arguments)
        display_sig = format_tool_call(
            event.tool_name, event.arguments, max_value_len=40
        )
        prompt = (
            f"{event.bot_name} is calling the '{event.tool_name}' tool"
            f" with arguments: {full_sig}."
            " Give a brief, in-character one-sentence aside to the viewer."
        )
        await self._generate_comment(
            prompt=prompt,
            fallback=f"{event.bot_name} calls {full_sig}",
            dim_prefix=display_sig,
        )

    async def _comment_on_context(self, event: ContextLoadEvent) -> None:
        """Generate commentary about context loading."""
        preview_len = 200
        content_preview = (
            event.content[:preview_len]
            if len(event.content) > preview_len
            else event.content
        )
        source_desc = "SharePoint" if event.source == "sharepoint" else event.path
        prompt = (
            f"{event.bot_name} just loaded project context from {source_desc}."
            f" The context is {len(event.content)} characters long"
            f" and starts with:\n\n{content_preview}\n\n"
            f"Give a brief, in-character reaction to what {event.bot_name} now"
            f" knows about the project."
        )
        await self._generate_comment(
            prompt=prompt,
            fallback=f"{event.bot_name} loaded project context from {source_desc}",
            dim_prefix=f"Loaded {source_desc}",
        )

    async def _generate_comment(
        self,
        prompt: str,
        fallback: str,
        dim_prefix: str,
    ) -> None:
        """Generate and post commentary using a random persona."""
        persona = random.choice(_PERSONAS)  # noqa: S311
        try:
            system = f"{persona.instructions} Answer in {self.language}"
            messages = [
                Message(role="system", content=system),
                Message(role="user", content=prompt),
            ]
            response = await self.llm.complete(messages)
        except Exception:  # noqa: BLE001
            self._post_fn(ChatMessage(sender=_STREIK_NAME, text=fallback))
            return
        self._post_fn(
            ChatMessage(sender=persona.name, text=f"[dim]{dim_prefix}[/]\n{response}")
        )
