"""LLM bot that loops tool calls, pausing for human approval before dangerous ones."""

import dataclasses
import json
from collections.abc import Awaitable, Callable
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
class GuardBot:
    """Chat participant that loops tool calls with human approval before dangerous ones.

    Identical to AgentBot except that tools flagged requires_approval=True are
    gated: the bot awaits a GuardDecision from the registered ask_fn before
    executing. The loop continues in all cases, feeding the result back to the LLM.
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    commentator: CommentatorBot | None = None
    is_human: ClassVar[bool] = False

    def __post_init__(self) -> None:  # noqa: D105
        self._ask_fn = _async_approved

    def register_guard(
        self, ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
    ) -> None:
        """Register the callback used to request approval for dangerous tool calls."""
        self._ask_fn = ask_fn

    async def on_message(
        self, message: ChatMessage, context: list[ContextItem]  # noqa: ARG002
    ) -> tuple[ChatMessage | None, list[ContextItem]]:
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
