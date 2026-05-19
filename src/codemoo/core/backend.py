"""LLM backend port: types, protocol, and pure context-building function."""

import dataclasses
import json
from typing import TYPE_CHECKING, Literal, Protocol, overload

if TYPE_CHECKING:
    from codemoo.core.tools import ToolDef

type Role = Literal["user", "assistant", "system", "tool"]


@dataclasses.dataclass(frozen=True)
class Message:
    """Immutable message in an LLM conversation context."""

    role: Role
    content: str
    tool_call_id: str | None = None
    # JSON-serialized tool_calls; only set on assistant messages that request a tool
    tool_calls_json: str | None = None


@dataclasses.dataclass
class ToolUse:
    """A single tool-call request returned by complete().

    Carries everything needed to invoke the tool and re-submit the result:
    the tool name, parsed arguments, the call ID for correlation, and the
    assistant message that must precede the tool-result message in the
    follow-up context. The assistant_message contains only this one call;
    use merge_tool_uses() to build a combined message for a batch.
    """

    name: str
    arguments: dict[str, object]
    call_id: str
    assistant_message: Message


def merge_tool_uses(uses: list[ToolUse]) -> Message:
    """Combine a batch of ToolUse objects into one shared assistant Message.

    The returned Message.tool_calls_json lists all calls in order, suitable
    for inclusion in the messages list passed to a subsequent complete() call
    when multiple tool results must be submitted together.
    """
    all_calls: list[object] = []
    for use in uses:
        if use.assistant_message.tool_calls_json is not None:
            all_calls.extend(json.loads(use.assistant_message.tool_calls_json))
    return Message(role="assistant", content="", tool_calls_json=json.dumps(all_calls))


class LLMBackend(Protocol):
    """Structural protocol for LLM completion backends.

    Pass tools to enable tool calling; omit tools (or pass None) for plain
    text completion. The overloads allow callers to get a plain str return type
    when they know no tools are involved, avoiding unnecessary type narrowing.
    """

    @overload
    async def complete(
        self,
        messages: list[Message],
        tools: None = ...,
    ) -> str: ...

    @overload
    async def complete(
        self,
        messages: list[Message],
        tools: "list[ToolDef]",
    ) -> "str | list[ToolUse]": ...

    async def complete(
        self,
        messages: list[Message],
        tools: "list[ToolDef] | None" = None,
    ) -> "str | list[ToolUse]":
        """Send messages to the LLM; return text or a non-empty list of tool calls."""
        ...
