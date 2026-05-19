"""RetryBot: full MemoryBot feature set with a per-turn retry budget."""

import dataclasses
import json
from collections.abc import Awaitable, Callable
from pathlib import Path

from codemoo.core.backend import (
    LLMBackend,
    Message,
    merge_tool_uses,
)
from codemoo.core.bots.approval import (
    ApprovalRequest,
    Denied,
    GuardDecision,
    _async_approved,
    _denial_message,
)
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.context import read_memory_file, read_project_context
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    ToolUseContent,
    next_turn_id,
)
from codemoo.core.tools import ToolDef, dispatch_tool, format_tool_call

_RETRY_BUDGET = 3


@dataclasses.dataclass(eq=False)
class RetryBot:
    """Chat participant that escalates after repeated identical tool failures.

    Reimplements the full MemoryBot feature set (context, memory, approval gates)
    and adds a per-turn retry counter. When the same (tool, args) pair is called
    _RETRY_BUDGET times in a single turn, the loop exits and returns a failure
    summary with any partial progress instead of continuing silently.
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    context_source: dict[str, str] | None
    memory_file: Path | None
    session_folder: Path
    commentator: CommentatorBot | None = None
    context: str | None = None
    memory: str | None = None

    def __post_init__(self) -> None:  # noqa: D105
        self._ask_fn = _async_approved

    def register_guard(
        self, ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
    ) -> None:
        """Register the callback used to request approval for dangerous tool calls."""
        self._ask_fn = ask_fn

    async def startup(self) -> None:
        """Load project context and memory file before the first message."""
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
            if not isinstance(response, list):
                return [
                    *[ContextItem(content=tu, turn_id=turn) for tu in tool_use_items],
                    ContextItem(
                        content=AssistantMessageContent(response), turn_id=turn
                    ),
                ]

            tool_result_messages: list[Message] = []
            for use in response:
                retry_key = (use.name, json.dumps(use.arguments, sort_keys=True))
                if retry_counts.get(retry_key, 0) >= _RETRY_BUDGET:
                    escalation = self._escalation_message(
                        retry_key[0], successful_calls
                    )
                    return [
                        *[
                            ContextItem(content=tu, turn_id=turn)
                            for tu in tool_use_items
                        ],
                        ContextItem(
                            content=AssistantMessageContent(escalation), turn_id=turn
                        ),
                    ]

                tool = tool_map[use.name]
                if tool.requires_approval:
                    decision = await self._ask_fn(
                        ApprovalRequest(bot_name=self.name, tool_use=use)
                    )
                    if isinstance(decision, Denied):
                        tool_output = _denial_message(decision)
                    else:
                        tool_output = await dispatch_tool(
                            tool, use.arguments, self.name, self.commentator
                        )
                else:
                    tool_output = await dispatch_tool(
                        tool, use.arguments, self.name, self.commentator
                    )

                retry_counts[retry_key] = retry_counts.get(retry_key, 0) + 1

                if not tool_output.startswith("Error "):
                    successful_calls.append(
                        format_tool_call(use.name, use.arguments, max_value_len=40)
                    )

                tool_use_items.append(
                    ToolUseContent(
                        name=use.name,
                        arguments_json=json.dumps(use.arguments),
                        call_id=use.call_id,
                        output=tool_output,
                    )
                )
                tool_result_messages.append(
                    Message(role="tool", content=tool_output, tool_call_id=use.call_id)
                )
            messages = [*messages, merge_tool_uses(response), *tool_result_messages]

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
