"""CompactBot: full MemoryBot feature set with automatic context summarisation."""

import dataclasses
import json
from collections.abc import Awaitable, Callable
from pathlib import Path

from codemoo.core.approval import (
    ApprovalRequest,
    Denied,
    GuardDecision,
    _async_approved,
    _denial_message,
)
from codemoo.core.backend import (
    LLMBackend,
    Message,
    merge_tool_uses,
)
from codemoo.core.commentator import CommentatorBot
from codemoo.core.context import read_memory_file, read_project_context
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    ToolUseContent,
    next_turn_id,
)
from codemoo.core.tools import ToolDef, dispatch_tool


@dataclasses.dataclass(eq=False)
class CompactBot:
    """Chat participant that summarises old context when the token budget is exceeded.

    Reimplements the full MemoryBot feature set (context, memory, approval gates,
    catch_errors=True) and adds a compact_threshold field. When the token count of
    build_context(context) reaches compact_threshold, app.py calls compact_context()
    before on_message to keep the LLM context manageable.
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    context_source: dict[str, str] | None
    memory_file: Path | None
    session_folder: Path
    compact_threshold: int | None
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
        """Load project context and memory."""
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
        """Respond using context and memory; tool errors feed back to the LLM."""
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
            if not isinstance(response, list):
                return [
                    *[ContextItem(content=tu, turn_id=turn) for tu in tool_use_items],
                    ContextItem(
                        content=AssistantMessageContent(response), turn_id=turn
                    ),
                ]

            tool_result_messages: list[Message] = []
            for use in response:
                tool = tool_map[use.name]
                if tool.requires_approval:
                    decision = await self._ask_fn(
                        ApprovalRequest(bot_name=self.name, tool_use=use)
                    )
                    if isinstance(decision, Denied):
                        tool_output = _denial_message(decision)
                    else:
                        tool_output = await dispatch_tool(
                            tool,
                            use.arguments,
                            self.name,
                            self.commentator,
                            catch_errors=True,
                        )
                else:
                    tool_output = await dispatch_tool(
                        tool,
                        use.arguments,
                        self.name,
                        self.commentator,
                        catch_errors=True,
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
