"""OpenRouter LLM backend implementation (OpenAI-compatible API)."""

import os

import openai

from codemoo.core.backend import LLMBackend
from codemoo.core.exceptions import BackendUnavailableError
from codemoo.core.tracer import Tracer
from codemoo.llm.openai_like import OpenAILikeBackend


class _OpenRouterBackend(OpenAILikeBackend):
    """LLMBackend implementation backed by OpenRouter (OpenAI-compatible)."""

    def __init__(
        self,
        client: openai.AsyncOpenAI,
        model: str,
        tracer: Tracer | None = None,
        url: str = "",
    ) -> None:
        super().__init__(model=model, tracer=tracer, url=url)
        self._client = client

    async def _call(
        self,
        serialized_messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]] | None,
    ) -> object:
        """Call OpenRouter chat completion API."""
        return await self._client.chat.completions.create(
            model=self._model,
            messages=serialized_messages,  # ty: ignore[invalid-argument-type]
            tools=(  # ty: ignore[invalid-argument-type]
                tool_schemas if tool_schemas is not None else openai.NOT_GIVEN
            ),
        )


def create_openrouter_backend(
    model: str,
    base_url: str,
    tracer: Tracer | None = None,
) -> LLMBackend:
    """Create an OpenRouter-backed LLMBackend.

    Reads OPENROUTER_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent. base_url must be provided via BackendConfig in codemoo.toml.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        msg = (
            "OPENROUTER_API_KEY environment variable is not set. "
            "Set it to your OpenRouter API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
    url = str(client.base_url).rstrip("/") + "/chat/completions"
    return _OpenRouterBackend(client=client, model=model, tracer=tracer, url=url)
