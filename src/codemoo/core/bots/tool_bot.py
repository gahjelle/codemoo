"""LLM bot that can invoke tools in a single explicit round-trip."""

import dataclasses
from typing import ClassVar, cast

from codemoo.core.backend import (
    Message,
    ToolLLMBackend,
    ToolUse,
    build_llm_context,
)
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef

_INSTRUCTIONS = """
You have tools available. Use them when they would help answer accurately.
""".strip()


@dataclasses.dataclass(eq=False)
class ToolBot:
    """Chat participant that can call tools before delivering a final reply.

    Demonstrates the tool-call round-trip explicitly:
    ask the LLM → detect a tool request → invoke the tool → re-ask with the result.
    """

    name: str
    emoji: str
    backend: ToolLLMBackend
    human_name: str
    tools: list[ToolDef]
    instructions: str = _INSTRUCTIONS
    max_messages: int = 20
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
            tool_map = {_tool_name(t): t for t in self.tools}
            tool_output = tool_map[step.name].fn(**step.arguments)  # type: ignore[call-arg]
            follow_up = [
                *context,
                step.assistant_message,
                Message(role="tool", content=tool_output, tool_call_id=step.call_id),
            ]
            text = await self.backend.complete(follow_up)
        else:
            text = step.text  # TextResponse
        return ChatMessage(sender=self.name, text=text)


def _tool_name(tool: ToolDef) -> str:
    """Extract the function name from a tool's schema."""
    fn_block = tool.schema.get("function")
    if not isinstance(fn_block, dict):
        return ""
    name = cast("dict[str, object]", fn_block).get("name")
    return name if isinstance(name, str) else ""
