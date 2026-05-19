"""Side-channel commentary bot that narrates tool calls during agentic loops."""

import dataclasses
import random
from collections.abc import Callable
from typing import Literal

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.message import ChatMessage
from codemoo.core.tools import format_tool_call


@dataclasses.dataclass(frozen=True)
class ToolEvent:
    """Emitted by dispatch_tool for every tool dispatch outcome."""

    outcome: Literal["call", "blocked", "error"]
    bot_name: str
    tool_name: str
    arguments: dict[str, object]
    detail: str | None = None


@dataclasses.dataclass(frozen=True)
class LoadEvent:
    """Emitted when a bot loads project context or its memory file."""

    kind: Literal["context", "memory"]
    bot_name: str
    source: str
    path: str
    content: str


@dataclasses.dataclass(frozen=True)
class ContextEvent:
    """Emitted on context window operations: full restart or compaction."""

    kind: Literal["restart", "compact"]
    bot_name: str
    items_affected: int
    preview: str


@dataclasses.dataclass(frozen=True)
class Persona:
    """Name, emoji, and system prompt for a CommentatorBot personality."""

    name: str
    emoji: str
    instructions: str


_STREIK_NAME = "Streik"
_STREIK_EMOJI = "\N{PUBLIC ADDRESS LOUDSPEAKER}"
_ERROR_TRUNCATE_LEN = 60
_PREVIEW_LEN = 600


@dataclasses.dataclass(eq=False)
class CommentatorBot:
    """Side-channel observer that narrates tool calls via a registered post callback.

    Not a ChatParticipant — messages bypass history and the dispatch loop.
    Call register() before the first comment() to wire it to the UI.
    """

    llm: LLMBackend
    personas: list[Persona]
    templates: dict[str, str]
    language: str = "English"
    _post_fn: Callable[[ChatMessage], None] = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:  # noqa: D105
        self._post_fn = lambda _: None

    def register(self, post_fn: Callable[[ChatMessage], None]) -> None:
        """Store the callable used to post commentary messages to the UI."""
        self._post_fn = post_fn

    def sender_info(self) -> dict[str, tuple[str, str]]:
        """Return sender-info entries for all personas and the Streik fallback."""
        info: dict[str, tuple[str, str]] = {
            p.name: (p.emoji, "bubble--commentator") for p in self.personas
        }
        info[_STREIK_NAME] = (_STREIK_EMOJI, "bubble--commentator")
        return info

    async def comment(
        self,
        event: ToolEvent | LoadEvent | ContextEvent,
    ) -> None:
        """Generate and post a persona-driven aside for the given event."""
        if isinstance(event, ToolEvent):
            await self._comment_on_tool(event)
        elif isinstance(event, LoadEvent):
            await self._comment_on_load(event)
        elif isinstance(event, ContextEvent):
            await self._comment_on_context(event)

    async def _comment_on_tool(self, event: ToolEvent) -> None:
        """Generate commentary about a tool dispatch outcome."""
        full_sig = format_tool_call(event.tool_name, event.arguments)
        display_sig = format_tool_call(
            event.tool_name, event.arguments, max_value_len=40
        )
        detail = event.detail or ""
        prompt = self.templates[event.outcome].format(
            bot_name=event.bot_name,
            tool_name=event.tool_name,
            sig=full_sig,
            detail=detail,
        )
        if event.outcome == "call":
            fallback = f"{event.bot_name} calls {full_sig}"
            dim_prefix = display_sig
        elif event.outcome == "blocked":
            fallback = f"Blocked: {detail}"
            dim_prefix = f"Blocked: {detail}"
        else:
            if len(detail) > _ERROR_TRUNCATE_LEN:
                truncated = detail[:_ERROR_TRUNCATE_LEN] + "\N{HORIZONTAL ELLIPSIS}"
            else:
                truncated = detail
            fallback = f"{display_sig} → {truncated}"
            dim_prefix = fallback
        await self._generate_comment(
            prompt=prompt, fallback=fallback, dim_prefix=dim_prefix
        )

    async def _comment_on_load(self, event: LoadEvent) -> None:
        """Generate commentary about a context or memory load."""
        preview = event.content[:_PREVIEW_LEN]
        source_desc = "SharePoint" if event.source == "sharepoint" else event.path
        prompt = self.templates[event.kind].format(
            bot_name=event.bot_name,
            source_desc=source_desc,
            path=event.path,
            content_len=len(event.content),
            preview=preview,
        )
        if event.kind == "memory":
            fallback = f"{event.bot_name} loaded memory from {event.path}"
            dim_prefix = f"Loaded memory ({len(event.content):,} chars)"
        else:
            fallback = f"{event.bot_name} loaded project context from {source_desc}"
            dim_prefix = f"Loaded {source_desc} ({len(event.content):,} chars)"
        await self._generate_comment(
            prompt=prompt, fallback=fallback, dim_prefix=dim_prefix
        )

    async def _comment_on_context(self, event: ContextEvent) -> None:
        """Generate commentary about a context window operation."""
        prompt = self.templates[event.kind].format(
            bot_name=event.bot_name,
            items_affected=event.items_affected,
            preview=event.preview,
        )
        if event.kind == "restart":
            fallback = (
                f"{event.bot_name} restarted — {event.items_affected} items dropped"
            )
            dim_prefix = f"Restarted — {event.items_affected} items dropped"
        else:
            fallback = f"Compacted {event.items_affected} items"
            dim_prefix = f"Compacted {event.items_affected} items"
        await self._generate_comment(
            prompt=prompt, fallback=fallback, dim_prefix=dim_prefix
        )

    async def _generate_comment(
        self,
        prompt: str,
        fallback: str,
        dim_prefix: str,
    ) -> None:
        """Generate and post commentary using a random persona."""
        if not self.personas:
            self._post_fn(ChatMessage(sender=_STREIK_NAME, text=fallback))
            return
        persona = random.choice(self.personas)  # noqa: S311
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
