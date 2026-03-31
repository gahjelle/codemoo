from datetime import datetime, timezone

from gaia.chat.message import ChatMessage


class EchoBot:
    @property
    def name(self) -> str:
        return "EchoBot"

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:
        # Skip own messages to prevent infinite echo loops
        if message.sender == self.name:
            return None
        return ChatMessage(
            sender=self.name,
            text=message.text,
            timestamp=datetime.now(tz=timezone.utc),
        )
