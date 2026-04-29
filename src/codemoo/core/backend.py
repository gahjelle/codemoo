"""LLM backend port: types, protocol, and pure context-building function."""

import dataclasses
from typing import TYPE_CHECKING, Literal, Protocol

if TYPE_CHECKING:
    from codemoo.core.tools import ToolDef

type Role = Literal["user", "assistant", "system", "tool"]


@dataclasses.dataclass(frozen=True)
class Message:
    """Immutable message in an LLM conversation context."""

    role: Role
    content: str
    tool_call_id: str | None = None
    # JSON-serialized tool_calls; only set on assistant messages from complete_step
    tool_calls_json: str | None = None


@dataclasses.dataclass(frozen=True)
class TextResponse:
    """A plain-text LLM reply from complete_step."""

    text: str


@dataclasses.dataclass
class ToolUse:
    """A tool-call request returned by complete_step.

    Carries everything needed to invoke the tool and re-submit the result:
    the tool name, parsed arguments, the call ID for correlation, and the
    assistant message that must precede the tool-result message in the
    follow-up context.
    """

    name: str
    arguments: dict[str, object]
    call_id: str
    assistant_message: Message


class LLMBackend(Protocol):
    """Structural protocol for LLM completion backends."""

    async def complete(self, messages: list[Message]) -> str:
        """Send messages to the LLM and return the response text."""
        ...


class ToolLLMBackend(LLMBackend, Protocol):
    """LLMBackend extended with a single-step tool-aware call.

    Bots that need tools use this narrower protocol; bots that only do
    text completion continue using LLMBackend, keeping their mocks simple.
    """

    async def complete_step(
        self,
        messages: list[Message],
        tools: list["ToolDef"],
    ) -> TextResponse | ToolUse:
        """Send one LLM request with tools; return text or a tool-call descriptor.

        Does NOT invoke the tool or re-submit. The caller drives re-submission.
        """
        ...
