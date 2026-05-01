"""OpenAI LLM backend implementation."""

import os

import openai as openai_sdk

from codemoo.core.backend import LLMBackend
from codemoo.llm.exceptions import BackendUnavailableError
from codemoo.llm.openai_like import OpenAILikeBackend


class _OpenAIBackend(OpenAILikeBackend):
    """LLMBackend implementation backed by the OpenAI API."""

    def __init__(self, client: openai_sdk.AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    async def _call(
        self,
        serialized_messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]] | None,
    ) -> object:
        """Call OpenAI chat completion API."""
        return await self._client.chat.completions.create(
            model=self._model,
            messages=serialized_messages,  # ty: ignore[invalid-argument-type]
            tools=(  # ty: ignore[invalid-argument-type]
                tool_schemas if tool_schemas is not None else openai_sdk.NOT_GIVEN
            ),
        )


def create_openai_backend(model: str, base_url: str | None = None) -> LLMBackend:
    """Create an OpenAI-backed LLMBackend.

    Reads OPENAI_API_KEY from the environment. Raises BackendUnavailableError
    if the key is absent. When base_url is provided it overrides the SDK default,
    enabling Azure AI Foundry and other OpenAI-compatible endpoints.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        msg = (
            "OPENAI_API_KEY environment variable is not set. "
            "Set it to your OpenAI API key before using this backend."
        )
        raise BackendUnavailableError(msg)
    kwargs: dict[str, object] = {"api_key": api_key}
    if base_url is not None:
        kwargs["base_url"] = base_url
    return _OpenAIBackend(
        client=openai_sdk.AsyncOpenAI(**kwargs),  # ty: ignore[invalid-argument-type]
        model=model,
    )
