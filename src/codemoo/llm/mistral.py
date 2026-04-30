"""Mistral LLM backend implementation."""

import os

from mistralai.client import Mistral

from codemoo.core.backend import ToolLLMBackend
from codemoo.llm.exceptions import BackendUnavailableError
from codemoo.llm.openai_like import OpenAILikeBackend


class _MistralBackend(OpenAILikeBackend):
    """LLMBackend implementation backed by the Mistral API."""

    def __init__(self, client: Mistral, model: str) -> None:
        self._client = client
        self._model = model

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
) -> ToolLLMBackend:
    """Create a Mistral-backed ToolLLMBackend.

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
        client=Mistral(api_key=api_key, timeout_ms=timeout_ms), model=model
    )
