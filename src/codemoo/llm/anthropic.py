"""Anthropic LLM backend implementation."""

import json
import os
from typing import overload

import anthropic as anthropic_sdk

from codemoo.core.backend import LLMBackend, Message, ToolUse
from codemoo.core.tools import ToolDef
from codemoo.llm.exceptions import BackendUnavailableError


def _serialize(
    messages: list[Message],
) -> tuple[str, list[dict[str, object]]]:
    """Split messages into (system_prompt, conversation_messages) for Anthropic.

    Anthropic requires the system prompt as a separate parameter, not a message.
    Tool result content uses a list format; tool call info is carried in
    tool_calls_json on the assistant message.
    """
    system = ""
    result: list[dict[str, object]] = []
    for m in messages:
        if m.role == "system":
            system = m.content
            continue
        if m.role == "tool":
            # Tool result: Anthropic expects content as a list of blocks
            result.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": m.tool_call_id or "",
                            "content": m.content,
                        }
                    ],
                }
            )
        elif m.tool_calls_json is not None:
            # Assistant message carrying a tool call
            tool_calls = json.loads(m.tool_calls_json)
            content: list[dict[str, object]] = []
            for tc in tool_calls:
                raw_args = tc.get("function", {}).get("arguments", "{}")
                content.append(
                    {
                        "type": "tool_use",
                        "id": tc.get("id", ""),
                        "name": tc.get("function", {}).get("name", ""),
                        "input": (
                            json.loads(raw_args)
                            if isinstance(raw_args, str)
                            else raw_args
                        ),
                    }
                )
            result.append({"role": "assistant", "content": content})
        else:
            result.append({"role": m.role, "content": m.content})
    return system, result


def _tool_schema(tool: ToolDef) -> dict[str, object]:
    """Convert a ToolDef to the Anthropic tool wire format."""
    properties = {
        p.name: {"type": p.type, "description": p.description} for p in tool.parameters
    }
    required = [p.name for p in tool.parameters if p.required]
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


class _AnthropicBackend:
    """LLMBackend implementation backed by the Anthropic API."""

    def __init__(self, client: anthropic_sdk.AsyncAnthropic, model: str) -> None:
        self._client = client
        self._model = model

    @overload
    async def complete(self, messages: list[Message], tools: None = ...) -> str: ...

    @overload
    async def complete(
        self, messages: list[Message], tools: list[ToolDef]
    ) -> str | ToolUse: ...

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDef] | None = None,
    ) -> str | ToolUse:
        """Call Anthropic messages API; return text or a tool-call descriptor."""
        system, conversation = _serialize(messages)
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=conversation,  # ty: ignore[invalid-argument-type]
            tools=[_tool_schema(t) for t in tools] if tools else [],  # ty: ignore[invalid-argument-type]
        )
        for block in response.content:
            if block.type == "tool_use":
                tool_call_id = block.id
                assistant_message = Message(
                    role="assistant",
                    content="",
                    tool_calls_json=json.dumps(
                        [
                            {
                                "id": tool_call_id,
                                "type": "function",
                                "function": {
                                    "name": block.name,
                                    "arguments": json.dumps(block.input),
                                },
                            }
                        ]
                    ),
                )
                return ToolUse(
                    name=block.name,
                    arguments=dict(block.input),
                    call_id=tool_call_id,
                    assistant_message=assistant_message,
                )
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""


def create_anthropic_backend(model: str) -> LLMBackend:
    """Create an Anthropic-backed LLMBackend.

    Reads ANTHROPIC_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        msg = (
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Set it to your Anthropic API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    return _AnthropicBackend(
        client=anthropic_sdk.AsyncAnthropic(api_key=api_key),
        model=model,
    )
