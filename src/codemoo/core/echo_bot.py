"""Simple bot that echoes every message back to the chat."""

import dataclasses

from codemoo.core.message import ChatMessage


class EchoBot:
    """A bot participant that mirrors each human message verbatim."""

    @property
    def name(self) -> str:
        """Return the bot's display name."""
        return "EchoBot"

    @property
    def emoji(self) -> str:
        """Return the bot's display emoji."""
        return "\N{ROBOT FACE}"

    @property
    def is_human(self) -> bool:
        """Return False — this participant is a bot."""
        return False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        """Echo the message, or return None if the sender is this bot."""
        # Skip own messages to prevent infinite echo loops
        if message.sender == self.name:
            return None
        # Timestamp is intentionally inherited from the incoming message;
        # the dispatch shell is responsible for assigning a fresh timestamp.
        return dataclasses.replace(message, sender=self.name)
