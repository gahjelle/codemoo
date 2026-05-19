"""Tests verifying the unified complete() interface across backends."""

import json
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from codemoo.core.backend import Message
from codemoo.core.tools import reverse_string
from codemoo.llm.anthropic import _AnthropicBackend, _serialize
from codemoo.llm.mistral import _MistralBackend


def _make_text_response(text: str) -> MagicMock:
    message = MagicMock()
    message.content = text
    message.tool_calls = None
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_tool_response(name: str, arguments: dict, call_id: str = "c1") -> MagicMock:
    fn_call = MagicMock()
    fn_call.name = name
    fn_call.arguments = json.dumps(arguments)
    tool_call = MagicMock()
    tool_call.id = call_id
    tool_call.function = fn_call
    message = MagicMock()
    message.content = None
    message.tool_calls = [tool_call]
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_anthropic_tool_use_response(name: str, arguments: dict) -> MagicMock:
    block = MagicMock(spec=["type", "id", "name", "input"])
    block.type = "tool_use"
    block.id = "tu_1"
    block.name = name
    block.input = arguments
    response = MagicMock()
    response.content = [block]
    return response


@pytest.fixture
def mock_api() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def anthropic_backend() -> _AnthropicBackend:
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock()
    return _AnthropicBackend(client=client, model="claude-haiku-4-5-20251001")


@pytest.fixture
def mistral_backend(mock_api: AsyncMock) -> _MistralBackend:
    client = MagicMock()
    client.chat.complete_async = mock_api
    return _MistralBackend(client=client, model="mistral-small-latest")


def test_mistral_backend_satisfies_llm_backend_protocol(
    mistral_backend: _MistralBackend,
) -> None:
    """Structural: backend has the complete() method the protocol requires."""
    assert callable(getattr(mistral_backend, "complete", None))


def test_mistral_backend_satisfies_tool_llm_backend_protocol(
    mistral_backend: _MistralBackend,
) -> None:
    assert callable(getattr(mistral_backend, "complete", None))


@pytest.mark.asyncio
async def test_complete_without_tools_returns_str(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("hello")

    result = await mistral_backend.complete([Message(role="user", content="hi")])

    assert isinstance(result, str)
    assert result == "hello"


@pytest.mark.asyncio
async def test_complete_with_none_tools_returns_str(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("hello")

    result = await mistral_backend.complete(
        [Message(role="user", content="hi")], tools=None
    )

    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_complete_with_tools_and_tool_call_returns_tool_use(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_tool_response("reverse_string", {"text": "hi"})

    result = await mistral_backend.complete(
        [Message(role="user", content="reverse hi")], tools=[reverse_string]
    )

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_complete_with_tools_and_text_response_returns_str(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("no tool needed")

    result = await mistral_backend.complete(
        [Message(role="user", content="hi")], tools=[reverse_string]
    )

    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_openai_like_without_tools_ignores_tool_calls_in_response(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_tool_response("reverse_string", {"text": "hello"})

    result = await mistral_backend.complete([Message(role="user", content="hi")])

    assert isinstance(result, str)
    assert result == ""


@pytest.mark.asyncio
async def test_anthropic_without_tools_ignores_tool_use_in_response(
    anthropic_backend: _AnthropicBackend,
) -> None:
    anthropic_backend._client.messages.create.return_value = (  # ty: ignore[unresolved-attribute]
        _make_anthropic_tool_use_response("reverse_string", {"text": "hello"})
    )

    result = await anthropic_backend.complete([Message(role="user", content="hi")])

    assert isinstance(result, str)
    assert result == ""


def test_anthropic_serialize_merges_consecutive_tool_messages() -> None:
    messages = [
        Message(role="user", content="go"),
        Message(
            role="assistant",
            content="",
            tool_calls_json=json.dumps(
                [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {"name": "f", "arguments": "{}"},
                    },
                    {
                        "id": "c2",
                        "type": "function",
                        "function": {"name": "g", "arguments": "{}"},
                    },
                ]
            ),
        ),
        Message(role="tool", content="r1", tool_call_id="c1"),
        Message(role="tool", content="r2", tool_call_id="c2"),
    ]
    _, serialized = _serialize(messages)

    tool_result_msgs = [
        m
        for m in serialized
        if m.get("role") == "user" and isinstance(m.get("content"), list)
    ]
    assert len(tool_result_msgs) == 1, (
        "consecutive tool results must be batched into one user message"
    )
    content = tool_result_msgs[0]["content"]
    assert isinstance(content, list)
    assert len(content) == 2
    ids = {cast("dict[str, object]", block)["tool_use_id"] for block in content}
    assert ids == {"c1", "c2"}


@pytest.mark.asyncio
async def test_complete_replaces_complete_step_for_tool_bots(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    """complete(messages, tools) is the unified replacement for complete_step."""
    mock_api.return_value = _make_tool_response("reverse_string", {"text": "hello"})

    result = await mistral_backend.complete(
        [Message(role="user", content="reverse hello")], tools=[reverse_string]
    )

    assert isinstance(result, list)
    assert result[0].name == "reverse_string"
    assert result[0].arguments == {"text": "hello"}
    assert result[0].assistant_message.tool_calls_json is not None
    parsed = json.loads(result[0].assistant_message.tool_calls_json)
    assert parsed[0]["function"]["name"] == "reverse_string"
