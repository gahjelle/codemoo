"""Single-round-trip tool-call loop shared by ToolBot and its subclasses."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import (
    Message,
    ToolLLMBackend,
    ToolUse,
)
from codemoo.core.bots.commentator_bot import CommentatorBot, ToolCallEvent
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef

_INTERRUPTED = "(tool executed, process interrupted)"


@dataclasses.dataclass(eq=False)
class SingleTurnToolBot:
    """Base class for bots that do a single tool-call round-trip before replying.

    Subclasses re-declare `instructions` with their own default constant to supply
    a bot-appropriate system prompt while still allowing callers to override it.
    """

    name: str
    emoji: str
    llm: ToolLLMBackend
    tools: list[ToolDef]
    instructions: str
    commentator: CommentatorBot | None = None
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond, invoking a tool first if the LLM requests one."""
        messages: list[Message] = [
            Message(role="system", content=self.instructions),
            *[
                Message(
                    role="assistant" if m.sender == self.name else "user",
                    content=m.text,
                )
                for m in history
            ],
            Message(role="user", content=message.text),
        ]
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
            tool_output = tool_map[response.name].fn(**response.arguments)
            follow_up = [
                *messages,
                response.assistant_message,
                Message(
                    role="tool", content=tool_output, tool_call_id=response.call_id
                ),
            ]
            response = await self.llm.complete(follow_up) or _INTERRUPTED
        return ChatMessage(sender=self.name, text=response)
