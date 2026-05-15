"""Single-round-trip tool-call loop shared by ToolBot and its subclasses."""

import dataclasses
import json
from typing import ClassVar

from codemoo.core.backend import (
    LLMBackend,
    Message,
    ToolUse,
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

_INTERRUPTED = "(tool executed, process interrupted)"


@dataclasses.dataclass(eq=False)
class SingleTurnToolBot:
    """Base class for bots that do a single tool-call round-trip before replying.

    Subclasses re-declare `instructions` with their own default constant to supply
    a bot-appropriate system prompt while still allowing callers to override it.
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    commentator: CommentatorBot | None = None
    is_human: ClassVar[bool] = False

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond, invoking a tool first if the LLM requests one."""
        messages: list[Message] = [
            Message(role="system", content=self.instructions),
            *build_context(context),
        ]
        turn = next_turn_id(context)
        response = await self.llm.complete(messages, self.tools)
        if isinstance(response, ToolUse):
            tool_map = {t.name: t for t in self.tools}
            if self.commentator is not None:
                await self.commentator.comment(
                    ToolCallEvent(
                        bot_name=self.name,
                        tool_name=response.name,
                        arguments=response.arguments,
                    )
                )
            tool_output = await dispatch_tool(
                tool_map[response.name], response.arguments, self.name, self.commentator
            )
            tool_use_item = ToolUseContent(
                name=response.name,
                arguments_json=json.dumps(response.arguments),
                call_id=response.call_id,
                output=tool_output,
            )
            follow_up = [
                *messages,
                response.assistant_message,
                Message(
                    role="tool", content=tool_output, tool_call_id=response.call_id
                ),
            ]
            text = await self.llm.complete(follow_up) or _INTERRUPTED
            return [
                ContextItem(content=tool_use_item, turn_id=turn),
                ContextItem(content=AssistantMessageContent(text), turn_id=turn),
            ]
        return [ContextItem(content=AssistantMessageContent(response), turn_id=turn)]
