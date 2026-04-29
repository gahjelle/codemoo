"""LLM bot that loops tool calls until the model produces a plain text reply."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import (
    Message,
    ToolLLMBackend,
    ToolUse,
    build_llm_context,
)
from codemoo.core.bots.commentator_bot import CommentatorBot, ToolCallEvent
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef


@dataclasses.dataclass(eq=False)
class AgentBot:
    """Chat participant that loops tool calls until the LLM decides it is done.

    Unlike SingleTurnToolBot (one optional tool call), AgentBot feeds each tool
    result back into context and calls complete_step again, continuing until
    the model returns a plain TextResponse.
    """

    name: str
    emoji: str
    backend: ToolLLMBackend
    human_name: str
    tools: list[ToolDef]
    instructions: str
    max_messages: int = 20
    commentator: CommentatorBot | None = None
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond, invoking tools repeatedly until the LLM returns plain text."""
        context = build_llm_context(
            history,
            message,
            bot_name=self.name,
            human_name=self.human_name,
            max_messages=self.max_messages,
            system=self.instructions,
        )
        tool_map = {t.name: t for t in self.tools}
        messages: list[Message] = list(context)

        while True:
            step = await self.backend.complete_step(messages, self.tools)
            if not isinstance(step, ToolUse):
                return ChatMessage(sender=self.name, text=step.text)
            if self.commentator is not None:
                await self.commentator.comment(
                    ToolCallEvent(
                        bot_name=self.name,
                        tool_name=step.name,
                        arguments=step.arguments,
                    )
                )
            tool_output = tool_map[step.name].fn(**step.arguments)
            messages = [
                *messages,
                step.assistant_message,
                Message(role="tool", content=tool_output, tool_call_id=step.call_id),
            ]
