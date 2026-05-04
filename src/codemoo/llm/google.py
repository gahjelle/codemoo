"""Google Gemini LLM backend implementation (OpenAI-compatible endpoint)."""

import os

import openai

from codemoo.core.backend import LLMBackend
from codemoo.core.tracer import Tracer
from codemoo.llm.exceptions import BackendUnavailableError
from codemoo.llm.openai_like import OpenAILikeBackend


class _GoogleBackend(OpenAILikeBackend):
    """LLMBackend backed by Google Gemini via its OpenAI-compatible API."""

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
        """Call Google Gemini chat completion API."""
        return await self._client.chat.completions.create(
            model=self._model,
            messages=serialized_messages,  # ty: ignore[invalid-argument-type]
            tools=(  # ty: ignore[invalid-argument-type]
                tool_schemas if tool_schemas is not None else openai.NOT_GIVEN
            ),
        )


def create_google_backend(
    model: str,
    base_url: str,
    tracer: Tracer | None = None,
) -> LLMBackend:
    """Create a Google Gemini-backed LLMBackend.

    Reads GOOGLE_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent. base_url must point to Google's OpenAI-compatible endpoint
    (configured via BackendConfig.base_url in codemoo.toml).
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        msg = (
            "GOOGLE_API_KEY environment variable is not set. "
            "Set it to your Google AI API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
    url = str(client.base_url).rstrip("/") + "/chat/completions"
    return _GoogleBackend(client=client, model=model, tracer=tracer, url=url)
