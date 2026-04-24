"""Side-channel commentary bot that narrates tool calls during agentic loops."""

import dataclasses
import random
from collections.abc import Callable

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage


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
_STREIK_EMOJI = "\N{PLACARD}"

_PERSONAS: list[Persona] = [
    Persona(
        name="Arne",
        emoji="\N{PARTY POPPER}",
        instructions=(
            "You are Arne, an enthusiastic and excitable commentator in a live"
            " coding agent demonstration. You love watching AI agents use tools"
            " and find every step genuinely thrilling. Comment on the tool call"
            " happening right now in one short, excited sentence."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
    Persona(
        name="Herwich",
        emoji="\N{CLIPBOARD}",
        instructions=(
            "You are Herwich, a precise and formal commentator in a live coding"
            " agent demonstration. You narrate AI tool usage with measured"
            " professionalism and bureaucratic clarity. Comment on the tool call"
            " happening right now in one concise, formal sentence."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
    Persona(
        name="Sølve",
        emoji="\N{ROCK}",
        instructions=(
            "You are Sølve, a dry and unimpressed commentator in a live coding"
            " agent demonstration. You have seen it all before and find nothing"
            " surprising. Comment on the tool call happening right now in one"
            " specific, but terse and deadpan sentence."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
    Persona(
        name="Rike",
        emoji="\N{FACE WITH ONE EYEBROW RAISED}",
        instructions=(
            "You are Rike, a skeptical commentator in a live coding agent"
            " demonstration. You question whether each tool call is really"
            " necessary and wonder if there is a better way. Comment on the tool"
            " call happening right now in one short, skeptical sentence."
            " Don't use quotes (' or \") around your answer."
        ),
    ),
]


def _format_args(arguments: dict[str, object]) -> str:
    """Format tool arguments as a function-call signature string."""
    if not arguments:
        return ""
    parts = [
        f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}" for k, v in arguments.items()
    ]
    return ", ".join(parts)


@dataclasses.dataclass(eq=False)
class CommentatorBot:
    """Side-channel observer that narrates tool calls via a registered post callback.

    Not a ChatParticipant — messages bypass history and the dispatch loop.
    Call register() before the first comment() to wire it to the UI.
    """

    backend: LLMBackend
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
        call_sig = f"call {event.tool_name}({_format_args(event.arguments)})"
        try:
            prompt = (
                f"{event.bot_name} is calling the '{event.tool_name}' tool"
                f" with arguments: {_format_args(event.arguments)}."
                " Give a brief, in-character one-sentence aside to the viewer."
            )
            system = f"{persona.instructions} Answer in {self.language}"
            messages = [
                Message(role="system", content=system),
                Message(role="user", content=prompt),
            ]
            text = await self.backend.complete(messages)
        except Exception:  # noqa: BLE001
            fallback = (
                f"{event.bot_name} calls"
                f" {event.tool_name}({_format_args(event.arguments)})"
            )
            self._post_fn(ChatMessage(sender=_STREIK_NAME, text=fallback))
            return
        short_sig = (call_sig[: min(70, len(call_sig) - 1)] + call_sig[-1]).replace(
            "\n", " "
        )
        self._post_fn(
            ChatMessage(sender=persona.name, text=f"[dim]{short_sig}[/]\n{text}")
        )
