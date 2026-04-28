"""Single-round-trip tool-call loop shared by ToolBot and its subclasses."""

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

_INTERRUPTED = "(tool executed, process interrupted)"


@dataclasses.dataclass(eq=False)
class GeneralToolBot:
    """Base class for bots that do a single tool-call round-trip before replying.

    Subclasses re-declare `instructions` with their own default constant to supply
    a bot-appropriate system prompt while still allowing callers to override it.
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
        """Respond, invoking a tool first if the LLM requests one."""
        context = build_llm_context(
            history,
            message,
            bot_name=self.name,
            human_name=self.human_name,
            max_messages=self.max_messages,
            system=self.instructions,
        )
        step = await self.backend.complete_step(context, self.tools)
        if isinstance(step, ToolUse):
            tool_map = {t.name: t for t in self.tools}
            if self.commentator is not None:
                await self.commentator.comment(
                    ToolCallEvent(
                        bot_name=self.name,
                        tool_name=step.name,
                        arguments=step.arguments,
                    )
                )
            tool_output = tool_map[step.name].fn(**step.arguments)
            follow_up = [
                *context,
                step.assistant_message,
                Message(role="tool", content=tool_output, tool_call_id=step.call_id),
            ]
            text = await self.backend.complete(follow_up) or _INTERRUPTED
        else:
            text = step.text  # TextResponse
        return ChatMessage(sender=self.name, text=text)
