"""Single-round-trip tool-call loop shared by ToolBot and its subclasses."""

import dataclasses
import json

from codemoo.core.backend import (
    LLMBackend,
    Message,
)
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    ToolUseContent,
    next_turn_id,
)
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

    async def on_message(
        self,
        context: list[ContextItem],
    ) -> list[ContextItem]:
        """Respond, invoking a tool first if the LLM requests one."""
        messages: list[Message] = [
            Message(role="system", content=self.instructions),
            *build_context(context),
        ]
        turn = next_turn_id(context)
        response = await self.llm.complete(messages, self.tools)
        if isinstance(response, list):
            use = response[0]
            tool_map = {t.name: t for t in self.tools}
            tool_output = await dispatch_tool(
                tool_map[use.name], use.arguments, self.name, self.commentator
            )
            tool_use_item = ToolUseContent(
                name=use.name,
                arguments_json=json.dumps(use.arguments),
                call_id=use.call_id,
                output=tool_output,
            )
            follow_up = [
                *messages,
                use.assistant_message,
                Message(role="tool", content=tool_output, tool_call_id=use.call_id),
            ]
            text = await self.llm.complete(follow_up) or _INTERRUPTED
            return [
                ContextItem(content=tool_use_item, turn_id=turn),
                ContextItem(content=AssistantMessageContent(text), turn_id=turn),
            ]
        return [ContextItem(content=AssistantMessageContent(response), turn_id=turn)]
