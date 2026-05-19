"""CompactBot: full RetryBot feature set with automatic context summarisation."""

import dataclasses
import json
from collections.abc import Awaitable, Callable
from pathlib import Path

from codemoo.core.backend import (
    LLMBackend,
    Message,
    ToolUse,
)
from codemoo.core.bots.approval import (
    ApprovalRequest,
    Denied,
    GuardDecision,
    _async_approved,
    _denial_message,
)
from codemoo.core.bots.commentator_bot import CommentatorBot, ContextEvent
from codemoo.core.context import read_memory_file, read_project_context
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    InjectedContent,
    ItemMode,
    ToolUseContent,
    next_turn_id,
)
from codemoo.core.token_counter import estimate_tokens
from codemoo.core.tools import ToolDef, dispatch_tool, format_tool_call

_RETRY_BUDGET = 3
_RECENT_WINDOW_FRACTION = 0.3
_DEFAULT_COMPACT_THRESHOLD = 8000

_SUMMARISE_PROMPT = """\
Summarise the conversation history below. Preserve:
- Decisions made and their rationale
- Files created, read, or modified (include paths)
- Explicit user instructions or constraints
- Open questions or next steps

Omit tool call traces and raw command output — those can be re-derived if needed.
Be concise. The summary will be injected as context for the next LLM turn.

--- CONVERSATION HISTORY ---
{history}
--- END ---"""


@dataclasses.dataclass(eq=False)
class CompactBot:
    """Chat participant that summarises old context when the token budget is exceeded.

    Reimplements the full RetryBot feature set (context, memory, approval gates,
    per-turn retry budget) and adds a compact() method. When the token count of
    build_context(context) reaches compact_threshold, older turns are condensed
    into a single InjectedContent summary item and disabled, keeping the LLM
    context manageable without losing important decisions or file references.
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    context_source: dict[str, str] | None
    memory_file: Path | None
    session_folder: Path
    compact_threshold: int
    commentator: CommentatorBot | None = None
    context: str | None = None
    memory: str | None = None

    def __post_init__(self) -> None:  # noqa: D105
        self._ask_fn = _async_approved
        self._compacted = False

    def register_guard(
        self, ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
    ) -> None:
        """Register the callback used to request approval for dangerous tool calls."""
        self._ask_fn = ask_fn

    async def startup(self) -> None:
        """Load project context and memory; reset compaction state."""
        self._compacted = False
        if self.commentator is not None:
            self.context = await read_project_context(
                context_source=self.context_source,
                bot_name=self.name,
                commentator=self.commentator,
                session_folder=self.session_folder,
            )
            if self.memory_file is not None:
                self.memory = await read_memory_file(
                    memory_file_path=self.memory_file,
                    bot_name=self.name,
                    commentator=self.commentator,
                )

    async def compact(self, context: list[ContextItem]) -> list[ContextItem]:
        """Summarise old context items when the token budget is exceeded.

        Returns context unchanged if below compact_threshold. When at or above
        threshold, disables old items (preserving pinned ones) and injects a
        single summary InjectedContent item before the recent window.
        """
        if estimate_tokens(build_context(context)) < self.compact_threshold:
            return context

        recent_budget = int(self.compact_threshold * _RECENT_WINDOW_FRACTION)
        recent_start = len(context)
        recent_tokens = 0
        for i in range(len(context) - 1, -1, -1):
            item_tokens = estimate_tokens(build_context([context[i]]))
            if recent_tokens + item_tokens <= recent_budget:
                recent_tokens += item_tokens
                recent_start = i
            else:
                break

        items_to_summarise = [
            item for item in context[:recent_start] if not item.pinned
        ]
        summary_text = await self._summarise(items_to_summarise)

        new_context: list[ContextItem] = []
        for item in context[:recent_start]:
            if item.pinned:
                new_context.append(item)
            else:
                new_context.append(dataclasses.replace(item, mode=ItemMode.DISABLED))

        summary_turn = (
            context[recent_start].turn_id if recent_start < len(context) else 0
        )
        new_context.append(
            ContextItem(
                content=InjectedContent(
                    label="Conversation summary",
                    text=summary_text,
                    role="user",
                ),
                turn_id=summary_turn,
                pinned=True,
            )
        )
        new_context.extend(context[recent_start:])
        self._compacted = True
        if self.commentator is not None:
            await self.commentator.comment(
                ContextEvent(
                    kind="compact",
                    bot_name=self.name,
                    items_affected=len(items_to_summarise),
                    preview=summary_text[:300],
                )
            )
        return new_context

    async def _summarise(self, items: list[ContextItem]) -> str:
        """Call the LLM to produce a focused summary of the given context items."""
        messages = build_context(items)
        history_lines: list[str] = []
        for msg in messages:
            role = msg.role.upper()
            history_lines.append(f"[{role}] {msg.content or ''}")
        history = "\n".join(history_lines)
        prompt = _SUMMARISE_PROMPT.format(history=history)
        summary_messages: list[Message] = [Message(role="user", content=prompt)]
        response = await self.llm.complete(summary_messages, [])
        if isinstance(response, ToolUse):
            return "(Summary unavailable)"
        return response

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond using context and memory, escalating after repeated tool failures."""
        system_content = self.instructions
        if self.context:
            system_content = f"{system_content}\n\n# Project Context\n\n{self.context}"
        if self.memory:
            system_content = f"{system_content}\n\n# Memory\n\n{self.memory}"

        messages: list[Message] = [
            Message(role="system", content=system_content),
            *build_context(context),
        ]
        tool_map = {t.name: t for t in self.tools}
        turn = next_turn_id(context)
        tool_use_items: list[ToolUseContent] = []
        retry_counts: dict[tuple[str, str], int] = {}
        successful_calls: list[str] = []

        while True:
            response = await self.llm.complete(messages, self.tools)
            if not isinstance(response, ToolUse):
                return [
                    *[ContextItem(content=tu, turn_id=turn) for tu in tool_use_items],
                    ContextItem(
                        content=AssistantMessageContent(response), turn_id=turn
                    ),
                ]

            retry_key = (response.name, json.dumps(response.arguments, sort_keys=True))
            if retry_counts.get(retry_key, 0) >= _RETRY_BUDGET:
                escalation = self._escalation_message(retry_key[0], successful_calls)
                return [
                    *[ContextItem(content=tu, turn_id=turn) for tu in tool_use_items],
                    ContextItem(
                        content=AssistantMessageContent(escalation), turn_id=turn
                    ),
                ]

            tool = tool_map[response.name]
            if tool.requires_approval:
                decision = await self._ask_fn(
                    ApprovalRequest(bot_name=self.name, tool_use=response)
                )
                if isinstance(decision, Denied):
                    tool_output = _denial_message(decision)
                else:
                    tool_output = await dispatch_tool(
                        tool, response.arguments, self.name, self.commentator
                    )
            else:
                tool_output = await dispatch_tool(
                    tool, response.arguments, self.name, self.commentator
                )

            retry_counts[retry_key] = retry_counts.get(retry_key, 0) + 1

            if not tool_output.startswith("Error "):
                successful_calls.append(
                    format_tool_call(
                        response.name, response.arguments, max_value_len=40
                    )
                )

            tool_use_items.append(
                ToolUseContent(
                    name=response.name,
                    arguments_json=json.dumps(response.arguments),
                    call_id=response.call_id,
                    output=tool_output,
                )
            )
            messages = [
                *messages,
                response.assistant_message,
                Message(
                    role="tool", content=tool_output, tool_call_id=response.call_id
                ),
            ]

    def _escalation_message(self, tool_name: str, successful_calls: list[str]) -> str:
        """Build the failure summary returned when the retry budget is exhausted."""
        lines = [
            f"I tried calling `{tool_name}` {_RETRY_BUDGET} times but kept getting"
            " the same error. I'm stopping here rather than continuing in a loop."
        ]
        if successful_calls:
            lines.append("\nCompleted before the failure:")
            lines.extend(f"  • {call}" for call in successful_calls)
        lines.append("\nPlease let me know how you'd like to proceed.")
        return "\n".join(lines)
