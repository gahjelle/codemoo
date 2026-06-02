"""Anthropic LLM backend implementation."""

import json
import os
from typing import overload

import anthropic as anthropic_sdk

from codemoo.core.backend import LLMBackend, Message, ToolUse
from codemoo.core.exceptions import BackendUnavailableError
from codemoo.core.tools import ToolDef
from codemoo.core.tracer import Tracer


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
    i = 0
    while i < len(messages):
        m = messages[i]
        if m.role == "system":
            system = m.content
            i += 1
            continue
        if m.role == "tool":
            # Collect all consecutive tool results into one batched user message.
            # Anthropic requires that all results for a parallel tool-use batch
            # arrive in a single user message.
            tool_results: list[dict[str, object]] = []
            while i < len(messages) and messages[i].role == "tool":
                tm = messages[i]
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tm.tool_call_id or "",
                        "content": tm.content,
                    }
                )
                i += 1
            result.append({"role": "user", "content": tool_results})
            continue
        if m.tool_calls_json is not None:
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
        i += 1
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

    def __init__(
        self,
        client: anthropic_sdk.AsyncAnthropic,
        model: str,
        tracer: Tracer | None = None,
    ) -> None:
        self._client = client
        self._model = model
        self._tracer = tracer
        self._url = str(client.base_url) + "/messages"

    @overload
    async def complete(self, messages: list[Message], tools: None = ...) -> str: ...

    @overload
    async def complete(
        self, messages: list[Message], tools: list[ToolDef]
    ) -> str | list[ToolUse]: ...

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolDef] | None = None,
    ) -> str | list[ToolUse]:
        """Call Anthropic messages API; return text or a tool-call descriptor."""
        system, conversation = _serialize(messages)
        tool_schemas = [_tool_schema(t) for t in tools] if tools else []
        payload: dict[str, object] = {
            "model": self._model,
            "max_tokens": 4096,
            "system": system,
            "messages": conversation,
            "tools": tool_schemas,
        }
        if self._tracer and self._tracer.on_request:
            self._tracer.on_request(self._url, payload)
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=conversation,  # ty: ignore[invalid-argument-type]
            tools=tool_schemas,  # ty: ignore[invalid-argument-type]
        )
        if self._tracer and self._tracer.on_response:
            self._tracer.on_response(response.model_dump())
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if tool_uses and tools:
            result = []
            for block in tool_uses:
                assistant_message = Message(
                    role="assistant",
                    content="",
                    tool_calls_json=json.dumps(
                        [
                            {
                                "id": block.id,
                                "type": "function",
                                "function": {
                                    "name": block.name,
                                    "arguments": json.dumps(block.input),
                                },
                            }
                        ]
                    ),
                )
                result.append(
                    ToolUse(
                        name=block.name,
                        arguments=dict(block.input),
                        call_id=block.id,
                        assistant_message=assistant_message,
                    )
                )
            return result
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""


def create_anthropic_backend(model: str, tracer: Tracer | None = None) -> LLMBackend:
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
        tracer=tracer,
    )
