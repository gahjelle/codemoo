"""MemoryBot: reads and writes a persistent memory file across sessions."""

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
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    ToolUseContent,
    next_turn_id,
)
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef, dispatch_tool


@dataclasses.dataclass(eq=False)
class MemoryBot:
    """Chat participant that loads project context and personal memory at startup.

    Both are injected into every system prompt. The save_memory tool (injected
    at construction time) lets the LLM persist observations across sessions.
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
        self, message: ChatMessage, context: list[ContextItem]  # noqa: ARG002
    ) -> tuple[ChatMessage | None, list[ContextItem]]:
        """Respond using context and memory, invoking tools with approval gates."""
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

        while True:
            response = await self.llm.complete(messages, self.tools)
            if not isinstance(response, ToolUse):
                reply = ChatMessage(sender=self.name, text=response)
                new_items: list[ContextItem] = [
                    ContextItem(content=tu, turn_id=turn) for tu in tool_use_items
                ]
                new_items.append(
                    ContextItem(content=AssistantMessageContent(response), turn_id=turn)
                )
                return reply, new_items
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
