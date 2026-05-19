import json
from dataclasses import FrozenInstanceError

import pytest

from codemoo.core.backend import Message, ToolUse, merge_tool_uses
from codemoo.llm.exceptions import BackendUnavailableError
from codemoo.llm.mistral import _MistralBackend, create_mistral_backend


def _make_tool_use(call_id: str, name: str = "f") -> ToolUse:
    return ToolUse(
        name=name,
        arguments={"x": "v"},
        call_id=call_id,
        assistant_message=Message(
            role="assistant",
            content="",
            tool_calls_json=json.dumps(
                [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": name, "arguments": "{}"},
                    }
                ]
            ),
        ),
    )


def test_merge_tool_uses_single_call() -> None:
    use = _make_tool_use("c1")
    result = merge_tool_uses([use])

    assert result.role == "assistant"
    calls = json.loads(result.tool_calls_json or "[]")
    assert len(calls) == 1
    assert calls[0]["id"] == "c1"


def test_merge_tool_uses_multiple_calls() -> None:
    uses = [_make_tool_use("c1", "tool_a"), _make_tool_use("c2", "tool_b")]
    result = merge_tool_uses(uses)

    calls = json.loads(result.tool_calls_json or "[]")
    assert len(calls) == 2
    assert calls[0]["id"] == "c1"
    assert calls[1]["id"] == "c2"
    assert calls[0]["function"]["name"] == "tool_a"
    assert calls[1]["function"]["name"] == "tool_b"


def test_message_is_immutable() -> None:
    msg = Message(role="user", content="hello")
    with pytest.raises(FrozenInstanceError):
        msg.__setattr__("content", "changed")


def test_message_fields_accessible() -> None:
    msg = Message(role="assistant", content="hi there")
    assert msg.role == "assistant"
    assert msg.content == "hi there"


def test_create_mistral_backend_raises_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    with pytest.raises(BackendUnavailableError, match="MISTRAL_API_KEY"):
        create_mistral_backend(model="mistral-small-latest")


def test_create_mistral_backend_returns_llm_backend_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    backend = create_mistral_backend(model="mistral-small-latest")
    assert callable(getattr(backend, "complete", None))


def test_create_mistral_backend_accepts_custom_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    backend = create_mistral_backend(model="mistral-large-latest")
    assert backend is not None


def test_create_mistral_backend_default_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    backend = create_mistral_backend(model="mistral-small-latest")
    assert isinstance(backend, _MistralBackend)
    assert backend._model == "mistral-small-latest"
