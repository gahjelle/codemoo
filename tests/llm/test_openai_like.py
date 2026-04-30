"""Tests for OpenAILikeBackend base class."""

import json
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from codemoo.core.backend import Message, ToolUse
from codemoo.core.tools import reverse_string
from codemoo.llm.mistral import _MistralBackend
from codemoo.llm.openai_like import OpenAILikeBackend


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


@pytest.fixture
def mock_api() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def backend(mock_api: AsyncMock) -> _MistralBackend:
    client = MagicMock()
    client.chat.complete_async = mock_api
    return _MistralBackend(client=client, model="mistral-small-latest")


def test_mistral_backend_is_openai_like(backend: _MistralBackend) -> None:
    assert isinstance(backend, OpenAILikeBackend)


def test_serialize_simple_message(backend: _MistralBackend) -> None:
    msgs = [Message(role="user", content="hello")]
    result = backend._serialize(msgs)
    assert result == [{"role": "user", "content": "hello"}]


def test_serialize_tool_call_id(backend: _MistralBackend) -> None:
    msg = Message(role="tool", content="result", tool_call_id="c1")
    result = backend._serialize([msg])
    assert result[0]["tool_call_id"] == "c1"


def test_serialize_tool_calls_json(backend: _MistralBackend) -> None:
    tc = json.dumps(
        [{"id": "c1", "type": "function", "function": {"name": "f", "arguments": "{}"}}]
    )
    msg = Message(role="assistant", content="", tool_calls_json=tc)
    result = backend._serialize([msg])
    assert "tool_calls" in result[0]
    tool_calls = cast("list[dict[str, object]]", result[0]["tool_calls"])
    assert tool_calls[0]["id"] == "c1"


def test_tool_schema_structure(backend: _MistralBackend) -> None:
    schema = backend._tool_schema(reverse_string)
    assert schema["type"] == "function"
    fn = cast("dict[str, object]", schema["function"])
    assert fn["name"] == "reverse_string"
    assert "parameters" in fn


@pytest.mark.asyncio
async def test_complete_without_tools_returns_str(
    backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("hi there")

    result = await backend.complete([Message(role="user", content="hi")])

    assert isinstance(result, str)
    assert result == "hi there"


@pytest.mark.asyncio
async def test_complete_with_tools_and_text_response_returns_str(
    backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("use no tools")

    result = await backend.complete(
        [Message(role="user", content="hi")], tools=[reverse_string]
    )

    assert isinstance(result, str)
    assert result == "use no tools"


@pytest.mark.asyncio
async def test_complete_with_tools_and_tool_call_returns_tool_use(
    backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_tool_response(
        "reverse_string", {"text": "hello"}, call_id="c42"
    )

    result = await backend.complete(
        [Message(role="user", content="reverse hello")], tools=[reverse_string]
    )

    assert isinstance(result, ToolUse)
    assert result.name == "reverse_string"
    assert result.arguments == {"text": "hello"}
    assert result.call_id == "c42"


@pytest.mark.asyncio
async def test_complete_without_tools_passes_none_to_call(
    backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("ok")

    await backend.complete([Message(role="user", content="hi")])

    _, kwargs = mock_api.call_args
    assert kwargs["tools"] is None


@pytest.mark.asyncio
async def test_complete_with_tools_passes_schemas_to_call(
    backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    mock_api.return_value = _make_text_response("ok")

    await backend.complete([Message(role="user", content="hi")], tools=[reverse_string])

    _, kwargs = mock_api.call_args
    assert kwargs["tools"] == [backend._tool_schema(reverse_string)]
