"""LLMBackend protocol and provider-specific factory functions."""

import os
from typing import Protocol

from mistralai.client import Mistral

from codaroo.llm.message import LLMMessage


class LLMBackend(Protocol):
    """Structural protocol for LLM completion backends."""

    async def complete(self, messages: list[LLMMessage]) -> str:
        """Send messages to the LLM and return the response text."""
        ...


class _MistralBackend:
    """LLMBackend implementation backed by the Mistral API."""

    def __init__(self, client: Mistral, model: str) -> None:
        self._client = client
        self._model = model

    async def complete(self, messages: list[LLMMessage]) -> str:
        """Call Mistral chat completion and return the response text."""
        response = await self._client.chat.complete_async(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        content = response.choices[0].message.content
        return content if isinstance(content, str) else str(content)


def create_mistral_backend(model: str = "mistral-small-latest") -> LLMBackend:
    """Create a Mistral-backed LLMBackend.

    Reads MISTRAL_API_KEY from the environment.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        msg = (
            "MISTRAL_API_KEY environment variable is not set. "
            "Set it to your Mistral API key before using this backend."
        )
        raise ValueError(msg)
    return _MistralBackend(client=Mistral(api_key=api_key), model=model)
