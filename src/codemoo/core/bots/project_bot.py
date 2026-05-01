"""GuardBot that reads project context before acting."""

import dataclasses
from collections.abc import Awaitable, Callable
from typing import ClassVar

from codemoo.core.backend import (
    LLMBackend,
    Message,
    ToolUse,
)
from codemoo.core.bots.commentator_bot import CommentatorBot, ToolCallEvent
from codemoo.core.context import read_project_context
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef


@dataclasses.dataclass(frozen=True)
class Approved:
    """The user approved the tool call — execute as planned."""


@dataclasses.dataclass(frozen=True)
class Denied:
    """The user denied the tool call, with an optional instruction."""

    reason: str | None = None


type GuardDecision = Approved | Denied


@dataclasses.dataclass(frozen=True)
class ApprovalRequest:
    """Carries the context needed to display an approval modal."""

    bot_name: str
    tool_use: ToolUse


def _denial_message(decision: Denied) -> str:
    if decision.reason:
        return f"Tool call denied: {decision.reason}"
    return (
        "The user denied this tool call."
        " Do not attempt it again — move on to the next step."
    )


async def _async_approved(_: ApprovalRequest) -> GuardDecision:
    return Approved()


@dataclasses.dataclass(eq=False)
class ProjectBot:
    """Chat participant that loads project context and loops tool calls.

    Identical to GuardBot except that:
    1. Reads AGENTS.md (or SharePoint doc) on each message
    2. Injects context into system prompt
    3. Proceeds with standard tool loop + approval gates

    If context file is not found, proceeds without context (graceful degradation).
    """

    name: str
    emoji: str
    llm: LLMBackend
    tools: list[ToolDef]
    instructions: str
    context_source: dict[str, str] | None
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
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond, loading context and invoking tools with approval gates."""
        context = None
        if self.commentator is not None:
            context = await read_project_context(
                context_source=self.context_source,
                bot_name=self.name,
                commentator=self.commentator,
            )

        system_content = self.instructions
        if context:
            system_content = f"{self.instructions}\n\n# Project Context\n\n{context}"

        messages: list[Message] = [
            Message(role="system", content=system_content),
            *[
                Message(
                    role="assistant" if m.sender == self.name else "user",
                    content=m.text,
                )
                for m in history
            ],
            Message(role="user", content=message.text),
        ]
        tool_map = {t.name: t for t in self.tools}

        while True:
            response = await self.llm.complete(messages, self.tools)
            if not isinstance(response, ToolUse):
                return ChatMessage(sender=self.name, text=response)
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
                    tool_output = tool.fn(**response.arguments)
            else:
                tool_output = tool.fn(**response.arguments)
            messages = [
                *messages,
                response.assistant_message,
                Message(
                    role="tool", content=tool_output, tool_call_id=response.call_id
                ),
            ]
