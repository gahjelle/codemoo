"""LLM bot that loops tool calls until the model produces a plain text reply."""

import dataclasses
import json

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
class AgentBot:
    """Chat participant that loops tool calls until the LLM decides it is done.

    Unlike SingleTurnToolBot (one optional tool call), AgentBot feeds each tool
    result back into context and calls complete again, continuing until
    the model returns a plain text string.
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
                tool_output = await dispatch_tool(
                    tool_map[use.name], use.arguments, self.name, self.commentator
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
