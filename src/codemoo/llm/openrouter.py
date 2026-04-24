"""OpenRouter LLM backend implementation (OpenAI-compatible API)."""

import json
import os

import openai

from codemoo.core.backend import Message, TextResponse, ToolLLMBackend, ToolUse
from codemoo.core.tools import ToolDef
from codemoo.llm.exceptions import BackendUnavailableError

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _serialize(messages: list[Message]) -> list[dict[str, object]]:
    """Convert Message objects to OpenAI-compatible dicts."""
    result: list[dict[str, object]] = []
    for m in messages:
        msg: dict[str, object] = {"role": m.role, "content": m.content}
        if m.tool_call_id is not None:
            msg["tool_call_id"] = m.tool_call_id
        if m.tool_calls_json is not None:
            msg["tool_calls"] = json.loads(m.tool_calls_json)
        result.append(msg)
    return result


def _tool_schema(tool: ToolDef) -> dict[str, object]:
    """Convert a ToolDef to the OpenAI/OpenRouter function-calling wire format."""
    properties = {
        p.name: {"type": p.type, "description": p.description} for p in tool.parameters
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


class _OpenRouterBackend:
    """LLMBackend implementation backed by OpenRouter (OpenAI-compatible)."""

    def __init__(self, client: openai.AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    async def complete(self, messages: list[Message]) -> str:
        """Call OpenRouter chat completion and return the response text."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=_serialize(messages),  # ty: ignore[invalid-argument-type]
        )
        content = response.choices[0].message.content
        return content if isinstance(content, str) else str(content)

    async def complete_step(
        self,
        messages: list[Message],
        tools: list[ToolDef],
    ) -> TextResponse | ToolUse:
        """Call OpenRouter with tools; return TextResponse or ToolUse."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=_serialize(messages),  # ty: ignore[invalid-argument-type]
            tools=[_tool_schema(t) for t in tools] if tools else openai.NOT_GIVEN,  # ty: ignore[invalid-argument-type]
        )
        message = response.choices[0].message
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            raw_args = tool_call.function.arguments
            arguments: dict[str, object] = (
                json.loads(raw_args) if isinstance(raw_args, str) else {}
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
                                "arguments": raw_args,
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
        return TextResponse(text=content if isinstance(content, str) else str(content))


def create_openrouter_backend(model: str) -> ToolLLMBackend:
    """Create an OpenRouter-backed ToolLLMBackend.

    Reads OPENROUTER_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        msg = (
            "OPENROUTER_API_KEY environment variable is not set. "
            "Set it to your OpenRouter API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    return _OpenRouterBackend(
        client=openai.AsyncOpenAI(api_key=api_key, base_url=_OPENROUTER_BASE_URL),
        model=model,
    )
