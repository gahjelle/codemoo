"""LLM bot that loops tool calls, pausing for human approval before dangerous ones."""

import dataclasses
from collections.abc import Awaitable, Callable
from typing import ClassVar

from codemoo.core.backend import (
    Message,
    ToolLLMBackend,
    ToolUse,
)
from codemoo.core.bots.commentator_bot import CommentatorBot, ToolCallEvent
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


@dataclasses.dataclass(eq=False)
class GuardBot:
    """Chat participant that loops tool calls with human approval before dangerous ones.

    Identical to AgentBot except that tools flagged requires_approval=True are
    gated: the bot awaits a GuardDecision from the registered ask_fn before
    executing. The loop continues in all cases, feeding the result back to the LLM.
    """

    name: str
    emoji: str
    llm: ToolLLMBackend
    tools: list[ToolDef]
    instructions: str
    commentator: CommentatorBot | None = None
    is_human: ClassVar[bool] = False

    def __post_init__(self) -> None:  # noqa: D105
        ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
        ask_fn = lambda _: _async_approved()  # noqa: E731
        self._ask_fn = ask_fn

    def register_guard(
        self, ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]
    ) -> None:
        """Register the callback used to request approval for dangerous tool calls."""
        self._ask_fn = ask_fn

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond, invoking tools repeatedly until the LLM returns plain text."""
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
        tool_map = {t.name: t for t in self.tools}

        while True:
            step = await self.llm.complete_step(messages, self.tools)
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
            tool = tool_map[step.name]
            if tool.requires_approval:
                decision = await self._ask_fn(
                    ApprovalRequest(bot_name=self.name, tool_use=step)
                )
                if isinstance(decision, Denied):
                    tool_output = _denial_message(decision)
                else:
                    tool_output = tool.fn(**step.arguments)
            else:
                tool_output = tool.fn(**step.arguments)
            messages = [
                *messages,
                step.assistant_message,
                Message(role="tool", content=tool_output, tool_call_id=step.call_id),
            ]


async def _async_approved() -> GuardDecision:
    return Approved()
