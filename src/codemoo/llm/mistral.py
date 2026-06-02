"""Mistral LLM backend implementation."""

import os

from mistralai.client import Mistral

from codemoo.core.backend import LLMBackend
from codemoo.core.exceptions import BackendUnavailableError
from codemoo.core.tracer import Tracer
from codemoo.llm.openai_like import OpenAILikeBackend

_MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"


class _MistralBackend(OpenAILikeBackend):
    """LLMBackend implementation backed by the Mistral API."""

    def __init__(
        self,
        client: Mistral,
        model: str,
        tracer: Tracer | None = None,
        url: str = _MISTRAL_CHAT_URL,
    ) -> None:
        super().__init__(model=model, tracer=tracer, url=url)
        self._client = client

    async def _call(
        self,
        serialized_messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]] | None,
    ) -> object:
        """Call Mistral chat completion API."""
        return await self._client.chat.complete_async(
            model=self._model,
            messages=serialized_messages,
            tools=tool_schemas,
        )


def create_mistral_backend(
    model: str,
    timeout_ms: int = 120_000,
    tracer: Tracer | None = None,
) -> LLMBackend:
    """Create a Mistral-backed LLMBackend.

    Reads MISTRAL_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        msg = (
            "MISTRAL_API_KEY environment variable is not set. "
            "Set it to your Mistral API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    return _MistralBackend(
        client=Mistral(api_key=api_key, timeout_ms=timeout_ms),
        model=model,
        tracer=tracer,
    )
