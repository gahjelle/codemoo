"""GuardBot: full RetryBot feature set with human approval before dangerous tools."""

import dataclasses
import json
from collections.abc import Awaitable, Callable

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
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    ToolUseContent,
    next_turn_id,
)
from codemoo.core.tools import ToolDef, dispatch_tool


@dataclasses.dataclass(eq=False)
class GuardBot:
    """Chat participant that loops tool calls with catch_errors and human approval.

    Extends RetryBot: passes catch_errors=True to all dispatch_tool calls and
    additionally gates tools flagged requires_approval=True behind a GuardDecision
    from the registered ask_fn. The loop continues in all cases.
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    commentator: CommentatorBot | None = None

    def __post_init__(self) -> None:  # noqa: D105
        self._ask_fn = _async_approved

    def register_guard(
        self, ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
    ) -> None:
        """Register the callback used to request approval for dangerous tool calls."""
        self._ask_fn = ask_fn

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond, invoking tools repeatedly until the LLM returns plain text."""
        messages: list[Message] = [
            Message(role="system", content=self.instructions),
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
