"""Ollama LLM backend implementation (OpenAI-compatible local server)."""

import os

import httpx
import openai

from codemoo.core.backend import LLMBackend
from codemoo.llm.exceptions import BackendUnavailableError
from codemoo.llm.openai_like import OpenAILikeBackend


class _OllamaBackend(OpenAILikeBackend):
    """LLMBackend implementation backed by a local Ollama server."""

    def __init__(self, client: openai.AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    async def _call(
        self,
        serialized_messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]] | None,
    ) -> object:
        """Call Ollama chat completion API."""
        return await self._client.chat.completions.create(
            model=self._model,
            messages=serialized_messages,  # ty: ignore[invalid-argument-type]
            tools=(  # ty: ignore[invalid-argument-type]
                tool_schemas if tool_schemas is not None else openai.NOT_GIVEN
            ),
        )


def create_ollama_backend(model: str, base_url: str) -> LLMBackend:
    """Create an Ollama-backed LLMBackend.

    Availability is determined by pinging GET {base_url}/models with a 2-second
    timeout rather than checking for an API key, since Ollama does not require one
    for local use. Raises BackendUnavailableError if the server is unreachable.

    OLLAMA_API_KEY is read from the environment; if absent it silently defaults to
    "ollama" (the Ollama convention), which supports authenticated remote deployments
    without breaking unauthenticated local ones.
    """
    try:
        with httpx.Client(timeout=2.0) as client:
            client.get(f"{base_url}/models")
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        msg = f"Ollama server not reachable at {base_url}: {exc}"
        raise BackendUnavailableError(msg) from exc

    api_key = os.environ.get("OLLAMA_API_KEY", "ollama")
    return _OllamaBackend(
        client=openai.AsyncOpenAI(api_key=api_key, base_url=base_url),
        model=model,
    )
