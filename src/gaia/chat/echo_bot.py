"""Simple bot that echoes every message back to the chat."""

from datetime import UTC, datetime

from gaia.chat.message import ChatMessage


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

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:
        """Echo the message, or return None if the sender is this bot."""
        # Skip own messages to prevent infinite echo loops
        if message.sender == self.name:
            return None
        return ChatMessage(
            sender=self.name,
            text=message.text,
            timestamp=datetime.now(tz=UTC),
        )
