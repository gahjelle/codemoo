"""Tests for OpenAI, Google, and Ollama backend factories."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest

from codemoo.config.schema import BackendConfig
from codemoo.core.exceptions import BackendUnavailableError
from codemoo.llm.factory import BackendInfo, _create, resolve_backend
from codemoo.llm.google import _GoogleBackend, create_google_backend
from codemoo.llm.ollama import _OllamaBackend, create_ollama_backend
from codemoo.llm.openai import _OpenAIBackend, create_openai_backend
from codemoo.llm.openai_like import OpenAILikeBackend


def _make_resolve_config(
    backend: str | None,
    fallbacks: list[str],
    backends: dict[str, str],
) -> SimpleNamespace:
    """Minimal config-like object for resolve_backend tests."""
    backend_cfgs = {
        name: BackendConfig(model_name=model) for name, model in backends.items()
    }
    return SimpleNamespace(
        models=SimpleNamespace(
            backend=backend,
            fallbacks=fallbacks,
            backends=backend_cfgs,
        )
    )


# ---------------------------------------------------------------------------
# BackendConfig.base_url
# ---------------------------------------------------------------------------


def test_backend_config_base_url_defaults_to_none() -> None:
    cfg = BackendConfig(model_name="gpt-4o-mini")
    assert cfg.base_url is None


def test_backend_config_base_url_accepts_string() -> None:
    cfg = BackendConfig(model_name="gpt-4o-mini", base_url="https://example.com/v1")
    assert cfg.base_url == "https://example.com/v1"


# ---------------------------------------------------------------------------
# OpenAI backend
# ---------------------------------------------------------------------------


def test_create_openai_backend_raises_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(BackendUnavailableError, match="OPENAI_API_KEY"):
        create_openai_backend(model="gpt-4o-mini")


def test_create_openai_backend_returns_backend_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    backend = create_openai_backend(model="gpt-4o-mini")
    assert isinstance(backend, _OpenAIBackend)
    assert isinstance(backend, OpenAILikeBackend)


def test_create_openai_backend_uses_correct_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    backend = create_openai_backend(model="gpt-4o")
    assert isinstance(backend, _OpenAIBackend)
    assert backend._model == "gpt-4o"


def test_create_openai_backend_with_custom_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    backend = create_openai_backend(
        model="Phi-4",
        base_url="https://my-project.inference.ai.azure.com/v1",
    )
    assert isinstance(backend, _OpenAIBackend)
    assert backend._model == "Phi-4"


def test_create_openai_backend_without_base_url_uses_sdk_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    backend = create_openai_backend(model="gpt-4o-mini", base_url=None)
    assert isinstance(backend, _OpenAIBackend)


# ---------------------------------------------------------------------------
# Google backend
# ---------------------------------------------------------------------------


def test_create_google_backend_raises_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(BackendUnavailableError, match="GOOGLE_API_KEY"):
        create_google_backend(
            model="gemini-2.0-flash",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )


def test_create_google_backend_returns_backend_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    backend = create_google_backend(
        model="gemini-2.0-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    assert isinstance(backend, _GoogleBackend)
    assert isinstance(backend, OpenAILikeBackend)


def test_create_google_backend_uses_correct_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    backend = create_google_backend(
        model="gemini-1.5-pro",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    assert isinstance(backend, _GoogleBackend)
    assert backend._model == "gemini-1.5-pro"


# ---------------------------------------------------------------------------
# Ollama backend
# ---------------------------------------------------------------------------


def _mock_httpx_success() -> MagicMock:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get = MagicMock(return_value=mock_response)
    return mock_client


def test_create_ollama_backend_returns_backend_when_server_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    with patch("codemoo.llm.ollama.httpx.Client", return_value=_mock_httpx_success()):
        backend = create_ollama_backend(
            model="llama3.2", base_url="http://localhost:11434/v1"
        )
    assert isinstance(backend, _OllamaBackend)
    assert isinstance(backend, OpenAILikeBackend)


def test_create_ollama_backend_raises_when_server_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get = MagicMock(side_effect=httpx.ConnectError("refused"))

    with (
        patch("codemoo.llm.ollama.httpx.Client", return_value=mock_client),
        pytest.raises(BackendUnavailableError, match="not reachable"),
    ):
        create_ollama_backend(model="llama3.2", base_url="http://localhost:11434/v1")


def test_create_ollama_backend_raises_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get = MagicMock(side_effect=httpx.TimeoutException("timeout"))

    with (
        patch("codemoo.llm.ollama.httpx.Client", return_value=mock_client),
        pytest.raises(BackendUnavailableError, match="not reachable"),
    ):
        create_ollama_backend(model="llama3.2", base_url="http://localhost:11434/v1")


def test_create_ollama_backend_defaults_key_to_ollama(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    with patch("codemoo.llm.ollama.httpx.Client", return_value=_mock_httpx_success()):
        backend = create_ollama_backend(
            model="llama3.2", base_url="http://localhost:11434/v1"
        )
    assert isinstance(backend, _OllamaBackend)


def test_create_ollama_backend_uses_explicit_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "secret")
    with patch("codemoo.llm.ollama.httpx.Client", return_value=_mock_httpx_success()):
        backend = create_ollama_backend(
            model="llama3.2", base_url="http://localhost:11434/v1"
        )
    assert isinstance(backend, _OllamaBackend)


# ---------------------------------------------------------------------------
# Factory dispatch
# ---------------------------------------------------------------------------


def test_create_dispatches_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    backend = _create("openai", "gpt-4o-mini", None)
    assert isinstance(backend, _OpenAIBackend)


def test_create_dispatches_google(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    backend = _create(
        "google",
        "gemini-2.0-flash",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    assert isinstance(backend, _GoogleBackend)


def test_create_dispatches_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    with patch("codemoo.llm.ollama.httpx.Client", return_value=_mock_httpx_success()):
        backend = _create("ollama", "llama3.2", "http://localhost:11434/v1")
    assert isinstance(backend, _OllamaBackend)


# ---------------------------------------------------------------------------
# resolve_backend — strict vs fallback mode
# ---------------------------------------------------------------------------

_BACKENDS = {"mistral": "mistral-small-latest", "openai": "gpt-4o-mini"}


def test_resolve_backend_strict_mode_returns_explicit_backend() -> None:
    config = _make_resolve_config("mistral", ["openai"], _BACKENDS)
    mock_backend = MagicMock()
    with patch("codemoo.llm.factory._create", return_value=mock_backend) as mock_create:
        _, info = resolve_backend(config)  # type: ignore[arg-type]
    assert info == BackendInfo(name="mistral", model="mistral-small-latest")
    mock_create.assert_called_once()


def test_resolve_backend_strict_mode_raises_without_trying_fallback() -> None:
    config = _make_resolve_config("mistral", ["openai"], _BACKENDS)
    err = BackendUnavailableError("no key")
    with (
        patch("codemoo.llm.factory._create", side_effect=err) as mock_create,
        pytest.raises(ValueError, match="No LLM backend available"),
    ):
        resolve_backend(config)  # type: ignore[arg-type]
    mock_create.assert_called_once()


def test_resolve_backend_fallback_mode_returns_first_available() -> None:
    config = _make_resolve_config(None, ["mistral", "openai"], _BACKENDS)
    mock_backend = MagicMock()
    with patch("codemoo.llm.factory._create", return_value=mock_backend) as mock_create:
        _, info = resolve_backend(config)  # type: ignore[arg-type]
    assert info.name == "mistral"
    mock_create.assert_called_once()


def test_resolve_backend_fallback_mode_skips_unavailable_backend() -> None:
    config = _make_resolve_config(None, ["mistral", "openai"], _BACKENDS)
    mock_backend = MagicMock()

    unavailable = BackendUnavailableError("no key")

    def _fail_mistral(name: str, *args: object, **kwargs: object) -> MagicMock:
        if name == "mistral":
            raise unavailable
        return mock_backend

    with patch("codemoo.llm.factory._create", side_effect=_fail_mistral):
        _, info = resolve_backend(config)  # type: ignore[arg-type]
    assert info.name == "openai"
