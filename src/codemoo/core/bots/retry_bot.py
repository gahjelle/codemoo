"""RetryBot: full MemoryBot feature set with a per-turn retry budget."""

import dataclasses
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import ClassVar

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
from codemoo.core.bots.commentator_bot import CommentatorBot, ToolCallEvent
from codemoo.core.context import read_memory_file, read_project_context
from codemoo.core.message import ChatMessage
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
    is_human: ClassVar[bool] = False

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
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using context and memory, escalating after repeated tool failures."""
        system_content = self.instructions
        if self.context:
            system_content = f"{system_content}\n\n# Project Context\n\n{self.context}"
        if self.memory:
            system_content = f"{system_content}\n\n# Memory\n\n{self.memory}"

        messages: list[Message] = [
            Message(role="system", content=system_content),
            *[
                Message(
                    role="assistant" if m.sender == self.name else "user",
                    content=m.text,
                )
                for m in history
            ],
            Message(role="user", content=message.text),
        ]
        tool_map = {t.name: t for t in self.tools}

        retry_counts: dict[tuple[str, str], int] = {}
        successful_calls: list[str] = []

        while True:
            response = await self.llm.complete(messages, self.tools)
            if not isinstance(response, ToolUse):
                return ChatMessage(sender=self.name, text=response)

            retry_key = (response.name, json.dumps(response.arguments, sort_keys=True))
            if retry_counts.get(retry_key, 0) >= _RETRY_BUDGET:
                return self._escalation_message(retry_key[0], successful_calls)

            if self.commentator is not None:
                await self.commentator.comment(
                    ToolCallEvent(
                        bot_name=self.name,
                        tool_name=response.name,
                        arguments=response.arguments,
                    )
                )

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

            messages = [
                *messages,
                response.assistant_message,
                Message(
                    role="tool", content=tool_output, tool_call_id=response.call_id
                ),
            ]

    def _escalation_message(
        self, tool_name: str, successful_calls: list[str]
    ) -> ChatMessage:
        """Build the failure summary returned when the retry budget is exhausted."""
        lines = [
            f"I tried calling `{tool_name}` {_RETRY_BUDGET} times but kept getting"
            " the same error. I'm stopping here rather than continuing in a loop."
        ]
        if successful_calls:
            lines.append("\nCompleted before the failure:")
            lines.extend(f"  • {call}" for call in successful_calls)
        lines.append("\nPlease let me know how you'd like to proceed.")
        return ChatMessage(sender=self.name, text="\n".join(lines))
