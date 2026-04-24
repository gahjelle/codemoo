from dataclasses import FrozenInstanceError

import pytest

from codemoo.core.backend import Message
from codemoo.llm.backend import _MistralBackend, create_mistral_backend


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
    with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
        create_mistral_backend()


def test_create_mistral_backend_returns_llm_backend_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    backend = create_mistral_backend()
    assert callable(getattr(backend, "complete", None))


def test_create_mistral_backend_accepts_custom_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    backend = create_mistral_backend(model="mistral-large-latest")
    assert backend is not None


def test_create_mistral_backend_uses_env_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    monkeypatch.setenv("CODEMOO_MISTRAL_MODEL", "mistral-large-latest")
    backend = create_mistral_backend()
    assert isinstance(backend, _MistralBackend)
    assert backend._model == "mistral-large-latest"


def test_create_mistral_backend_default_model_when_env_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    monkeypatch.delenv("CODEMOO_MISTRAL_MODEL", raising=False)
    backend = create_mistral_backend()
    assert isinstance(backend, _MistralBackend)
    assert backend._model == "mistral-small-latest"


def test_create_mistral_backend_explicit_model_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    monkeypatch.setenv("CODEMOO_MISTRAL_MODEL", "mistral-large-latest")
    backend = create_mistral_backend(model="mistral-small-latest")
    assert isinstance(backend, _MistralBackend)
    assert backend._model == "mistral-small-latest"
