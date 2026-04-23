import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.tools import ToolDef, reverse_string
from codemoo.llm.backend import _MistralBackend


def _make_text_response(text: str) -> MagicMock:
    """Build a mock Mistral response that returns plain text."""
    message = MagicMock()
    message.content = text
    message.tool_calls = None
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_tool_response(
    name: str, arguments: dict, call_id: str = "call-1"
) -> MagicMock:
    """Build a mock Mistral response that requests a tool call."""
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
def mock_complete() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def backend(mock_complete: AsyncMock) -> _MistralBackend:
    client = MagicMock()
    client.chat.complete_async = mock_complete
    return _MistralBackend(client=client, model="mistral-small-latest")


@pytest.mark.asyncio
async def test_complete_step_text_response(
    backend: _MistralBackend, mock_complete: AsyncMock
) -> None:
    mock_complete.return_value = _make_text_response("hello there")

    result = await backend.complete_step([Message(role="user", content="hi")], [])

    assert isinstance(result, TextResponse)
    assert result.text == "hello there"


@pytest.mark.asyncio
async def test_complete_step_tool_use_returned(
    backend: _MistralBackend, mock_complete: AsyncMock
) -> None:
    mock_complete.return_value = _make_tool_response(
        "reverse_string", {"text": "hello"}, call_id="call-42"
    )

    result = await backend.complete_step(
        [Message(role="user", content="reverse hello")],
        [reverse_string],
    )

    assert isinstance(result, ToolUse)
    assert result.name == "reverse_string"
    assert result.arguments == {"text": "hello"}
    assert result.call_id == "call-42"


@pytest.mark.asyncio
async def test_complete_step_tool_use_does_not_invoke_fn(
    backend: _MistralBackend, mock_complete: AsyncMock
) -> None:
    """complete_step must NOT call the tool function — that's the caller's job."""
    invoked = []

    def spy_fn(**kwargs: object) -> str:
        invoked.append(kwargs)
        return "result"

    spy_tool = ToolDef(schema=reverse_string.schema, fn=spy_fn)
    mock_complete.return_value = _make_tool_response(
        "reverse_string", {"text": "hello"}
    )

    await backend.complete_step([Message(role="user", content="hi")], [spy_tool])

    assert invoked == []


@pytest.mark.asyncio
async def test_complete_step_assistant_message_has_tool_calls_json(
    backend: _MistralBackend, mock_complete: AsyncMock
) -> None:
    mock_complete.return_value = _make_tool_response(
        "reverse_string", {"text": "hi"}, call_id="call-7"
    )

    result = await backend.complete_step(
        [Message(role="user", content="hi")], [reverse_string]
    )

    assert isinstance(result, ToolUse)
    assert result.assistant_message.role == "assistant"
    parsed = json.loads(result.assistant_message.tool_calls_json or "[]")
    assert parsed[0]["id"] == "call-7"
    assert parsed[0]["function"]["name"] == "reverse_string"


@pytest.mark.asyncio
async def test_complete_step_passes_tool_schemas(
    backend: _MistralBackend, mock_complete: AsyncMock
) -> None:
    mock_complete.return_value = _make_text_response("ok")

    await backend.complete_step([Message(role="user", content="hi")], [reverse_string])

    _, kwargs = mock_complete.call_args
    assert kwargs["tools"] == [reverse_string.schema]
