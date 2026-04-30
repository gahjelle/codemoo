"""Tests verifying the unified complete() interface across backends."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from codemoo.core.backend import Message, ToolUse
from codemoo.core.tools import reverse_string
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


@pytest.fixture
def mock_api() -> AsyncMock:
    return AsyncMock()


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

    assert isinstance(result, ToolUse)


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
async def test_complete_replaces_complete_step_for_tool_bots(
    mistral_backend: _MistralBackend, mock_api: AsyncMock
) -> None:
    """complete(messages, tools) is the unified replacement for complete_step."""
    mock_api.return_value = _make_tool_response("reverse_string", {"text": "hello"})

    result = await mistral_backend.complete(
        [Message(role="user", content="reverse hello")], tools=[reverse_string]
    )

    assert isinstance(result, ToolUse)
    assert result.name == "reverse_string"
    assert result.arguments == {"text": "hello"}
    assert result.assistant_message.tool_calls_json is not None
    parsed = json.loads(result.assistant_message.tool_calls_json)
    assert parsed[0]["function"]["name"] == "reverse_string"
