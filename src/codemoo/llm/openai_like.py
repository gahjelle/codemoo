"""Base class for OpenAI-compatible LLM backends (Mistral, OpenRouter, etc.)."""

import json
from abc import abstractmethod
from typing import overload

from codemoo.core.backend import Message, ToolUse
from codemoo.core.tools import ToolDef


class OpenAILikeBackend:
    """Common implementation of the unified complete() method for OpenAI-format APIs.

    Subclasses only need to implement _call(); the serialization, schema
    conversion, and response parsing are shared here because the OpenAI wire
    format is identical across providers.
    """

    def _serialize(self, messages: list[Message]) -> list[dict[str, object]]:
        """Convert Message objects to OpenAI-compatible request dicts."""
        result: list[dict[str, object]] = []
        for m in messages:
            msg: dict[str, object] = {"role": m.role, "content": m.content}
            if m.tool_call_id is not None:
                msg["tool_call_id"] = m.tool_call_id
            if m.tool_calls_json is not None:
                msg["tool_calls"] = json.loads(m.tool_calls_json)
            result.append(msg)
        return result

    def _tool_schema(self, tool: ToolDef) -> dict[str, object]:
        """Convert a ToolDef to the OpenAI function-calling wire format."""
        properties = {
            p.name: {"type": p.type, "description": p.description}
            for p in tool.parameters
        }
        required = [p.name for p in tool.parameters if p.required]
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    @abstractmethod
    async def _call(
        self,
        serialized_messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]] | None,
    ) -> object:
        """Invoke the provider API; return the raw response object."""
        ...

    @overload
    async def complete(self, messages: list[Message], tools: None = ...) -> str: ...

    @overload
    async def complete(
        self, messages: list[Message], tools: list[ToolDef]
    ) -> str | ToolUse: ...

    async def complete(
        self, messages: list[Message], tools: list[ToolDef] | None = None
    ) -> str | ToolUse:
        """Unified completion: handles both text and tool-calling responses."""
        serialized = self._serialize(messages)
        tool_schemas = [self._tool_schema(t) for t in tools] if tools else None
        response = await self._call(serialized, tool_schemas)
        message = response.choices[0].message  # ty: ignore[unresolved-attribute]
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            raw_args = tool_call.function.arguments
            arguments: dict[str, object] = (
                json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
            )
            assistant_message = Message(
                role="assistant",
                content="",
                tool_calls_json=json.dumps(
                    [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": (
                                    raw_args
                                    if isinstance(raw_args, str)
                                    else json.dumps(raw_args)
                                ),
                            },
                        }
                    ]
                ),
            )
            return ToolUse(
                name=tool_call.function.name,
                arguments=arguments,
                call_id=tool_call.id or "",
                assistant_message=assistant_message,
            )
        content = message.content
        return content if isinstance(content, str) else str(content or "")
