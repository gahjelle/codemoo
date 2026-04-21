"""LLM-powered chat participant implementations."""

import dataclasses
from datetime import UTC, datetime

from codaroo.core.message import ChatMessage
from codaroo.llm.backend import LLMBackend
from codaroo.llm.message import LLMMessage


class LLMBot:
    """Chat participant that responds using only the current message.

    Intended for demonstration. The full conversation history is ignored;
    only the triggering message is sent to the LLM.
    """

    def __init__(self, name: str, emoji: str, backend: LLMBackend) -> None:
        """Initialise with display properties and an LLM backend."""
        self._name = name
        self._emoji = emoji
        self._backend = backend

    @property
    def name(self) -> str:
        """Return the bot's display name."""
        return self._name

    @property
    def emoji(self) -> str:
        """Return the bot's display emoji."""
        return self._emoji

    @property
    def is_human(self) -> bool:
        """Return False — this participant is a bot."""
        return False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Respond to message using only its text; ignore history."""
        if message.sender == self.name:
            return None
        response = await self._backend.complete(
            [LLMMessage(role="user", content=message.text)]
        )
        return dataclasses.replace(message, sender=self.name, text=response)


class ChatBot:
    """Chat participant that maintains conversation context.

    Filters history to human + self messages only and clips to max_messages
    before sending to the LLM. Stateless — history is injected by the shell.
    """

    def __init__(
        self,
        name: str,
        emoji: str,
        backend: LLMBackend,
        human_name: str,
        max_messages: int = 20,
    ) -> None:
        """Initialise with display properties, backend, human name, and clip limit."""
        self._name = name
        self._emoji = emoji
        self._backend = backend
        self._human_name = human_name
        self._max_messages = max_messages

    @property
    def name(self) -> str:
        """Return the bot's display name."""
        return self._name

    @property
    def emoji(self) -> str:
        """Return the bot's display emoji."""
        return self._emoji

    @property
    def is_human(self) -> bool:
        """Return False — this participant is a bot."""
        return False

    def _build_context(
        self, history: list[ChatMessage], current: ChatMessage
    ) -> list[LLMMessage]:
        """Build the LLM message list from filtered, clipped history plus current."""
        relevant = [m for m in history if m.sender in (self._human_name, self._name)]
        clipped = relevant[-self._max_messages :]
        llm_messages = [
            LLMMessage(
                role="assistant" if m.sender == self._name else "user",
                content=m.text,
            )
            for m in clipped
        ]
        llm_messages.append(LLMMessage(role="user", content=current.text))
        return llm_messages

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using filtered conversation history."""
        if message.sender == self.name:
            return None
        context = self._build_context(history, message)
        response = await self._backend.complete(context)
        return ChatMessage(
            sender=self.name,
            text=response,
            timestamp=datetime.now(tz=UTC),
        )
