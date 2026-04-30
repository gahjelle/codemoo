"""OpenRouter LLM backend implementation (OpenAI-compatible API)."""

import os

import openai

from codemoo.core.backend import ToolLLMBackend
from codemoo.llm.exceptions import BackendUnavailableError
from codemoo.llm.openai_like import OpenAILikeBackend

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class _OpenRouterBackend(OpenAILikeBackend):
    """LLMBackend implementation backed by OpenRouter (OpenAI-compatible)."""

    def __init__(self, client: openai.AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

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


def create_openrouter_backend(model: str) -> ToolLLMBackend:
    """Create an OpenRouter-backed ToolLLMBackend.

    Reads OPENROUTER_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        msg = (
            "OPENROUTER_API_KEY environment variable is not set. "
            "Set it to your OpenRouter API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    return _OpenRouterBackend(
        client=openai.AsyncOpenAI(api_key=api_key, base_url=_OPENROUTER_BASE_URL),
        model=model,
    )
