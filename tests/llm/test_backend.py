from dataclasses import FrozenInstanceError

import pytest

from codaroo.llm.backend import create_mistral_backend
from codaroo.llm.message import LLMMessage


def test_llm_message_is_immutable() -> None:
    msg = LLMMessage(role="user", content="hello")
    with pytest.raises(FrozenInstanceError):
        msg.__setattr__("content", "changed")


def test_llm_message_fields_accessible() -> None:
    msg = LLMMessage(role="assistant", content="hi there")
    assert msg.role == "assistant"
    assert msg.content == "hi there"


def test_create_mistral_backend_raises_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
        create_mistral_backend()


def test_create_mistral_backend_returns_llm_backend_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    backend = create_mistral_backend()
    # Duck-type check: must have a complete method
    assert callable(getattr(backend, "complete", None))


def test_create_mistral_backend_accepts_custom_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    # No error raised — model name is stored, validated by the API at call time
    backend = create_mistral_backend(model="mistral-large-latest")
    assert backend is not None
