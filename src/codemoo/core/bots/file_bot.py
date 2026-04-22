"""LLM bot that can read files from disk via a single tool call."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import (
    Message,
    ToolLLMBackend,
    ToolUse,
    build_llm_context,
)
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef

_INSTRUCTIONS = """
You can read files using the read_file tool. When the user asks about a file or its
contents, call read_file with the file path to retrieve it before answering.
""".strip()


@dataclasses.dataclass(eq=False)
class FileBot:
    """Chat participant that reads files on demand before delivering a reply.

    Demonstrates tool use applied to the filesystem: ask the LLM → detect a
    read_file request → load the file → re-ask with the contents.
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
        """Respond, reading a file first if the LLM requests one."""
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
    name = fn_block.get("name")
    return name if isinstance(name, str) else ""
