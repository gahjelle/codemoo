"""RetryBot that reads project context before acting."""

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
from codemoo.core.context import read_project_context
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    ToolUseContent,
    next_turn_id,
)
from codemoo.core.tools import ToolDef, dispatch_tool


@dataclasses.dataclass(eq=False)
class ProjectBot:
    """Chat participant that loads project context once at startup and loops tool calls.

    Context is loaded in startup() before the first message and injected into
    every system prompt. Proceeds with standard tool loop + approval gates.

    If context file is not found, proceeds without context (graceful degradation).
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    context_source: dict[str, str] | None
    session_folder: Path
    commentator: CommentatorBot | None = None
    context: str | None = None

    def __post_init__(self) -> None:  # noqa: D105
        self._ask_fn = _async_approved

    def register_guard(
        self, ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
    ) -> None:
        """Register the callback used to request approval for dangerous tool calls."""
        self._ask_fn = ask_fn

    async def startup(self) -> None:
        """Load project context once before the first message."""
        if self.commentator is not None:
            self.context = await read_project_context(
                context_source=self.context_source,
                bot_name=self.name,
                commentator=self.commentator,
                session_folder=self.session_folder,
            )

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond using pre-loaded context and invoking tools with approval gates."""
        system_content = self.instructions
        if self.context:
            system_content = (
                f"{self.instructions}\n\n# Project Context\n\n{self.context}"
            )

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
