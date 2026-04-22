"""Concrete LLM backend implementations and factory functions."""

import json
import os

from mistralai.client import Mistral

from codemoo.core.backend import Message, TextResponse, ToolLLMBackend, ToolUse
from codemoo.core.tools import ToolDef


def _serialize(messages: list[Message]) -> list[dict[str, object]]:
    """Convert Message objects to Mistral-compatible dicts."""
    result: list[dict[str, object]] = []
    for m in messages:
        msg: dict[str, object] = {"role": m.role, "content": m.content}
        if m.tool_call_id is not None:
            msg["tool_call_id"] = m.tool_call_id
        if m.tool_calls_json is not None:
            msg["tool_calls"] = json.loads(m.tool_calls_json)
        result.append(msg)
    return result


class _MistralBackend:
    """LLMBackend implementation backed by the Mistral API."""

    def __init__(self, client: Mistral, model: str) -> None:
        self._client = client
        self._model = model

    async def complete(self, messages: list[Message]) -> str:
        """Call Mistral chat completion and return the response text."""
        response = await self._client.chat.complete_async(
            model=self._model,
            messages=_serialize(messages),  # type: ignore[arg-type]
        )
        content = response.choices[0].message.content
        return content if isinstance(content, str) else str(content)

    async def complete_step(
        self,
        messages: list[Message],
        tools: list[ToolDef],
    ) -> TextResponse | ToolUse:
        """Call Mistral with tools; return TextResponse or ToolUse.

        Does NOT invoke the tool or re-submit. The caller drives re-submission.
        """
        response = await self._client.chat.complete_async(
            model=self._model,
            messages=_serialize(messages),  # type: ignore[arg-type]
            tools=[t.schema for t in tools] if tools else None,  # type: ignore[arg-type]
        )
        message = response.choices[0].message
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            raw_args = tool_call.function.arguments
            arguments: dict[str, object] = (
                json.loads(raw_args) if isinstance(raw_args, str) else raw_args
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
                                "arguments": raw_args
                                if isinstance(raw_args, str)
                                else json.dumps(raw_args),
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


def create_mistral_backend(
    model: str = "mistral-small-latest",
    timeout_ms: int = 120_000,
) -> ToolLLMBackend:
    """Create a Mistral-backed ToolLLMBackend.

    Reads MISTRAL_API_KEY from the environment.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        msg = (
            "MISTRAL_API_KEY environment variable is not set. "
            "Set it to your Mistral API key before using this backend."
        )
        raise ValueError(msg)
    return _MistralBackend(
        client=Mistral(api_key=api_key, timeout_ms=timeout_ms), model=model
    )
