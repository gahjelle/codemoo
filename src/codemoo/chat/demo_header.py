"""DemoHeader widget shown at the top of ChatApp in demo mode."""

from rich.text import Text
from textual.widgets import Label

from codemoo.core.participant import ChatParticipant


class DemoHeader(Label):
    """One-line header showing the active bot's identity, position, and prompt state."""

    DEFAULT_CSS = """
    DemoHeader {
        height: 1;
        width: 1fr;
    }
    """

    def __init__(
        self, bot: ChatParticipant, position: tuple[int, int], prompt_count: int = 0
    ) -> None:
        """Initialise with the bot, its (current, total) position, and prompt count."""
        self._bot = bot
        self._position = position
        self._total = prompt_count
        self._remaining = prompt_count
        super().__init__(self._build_text())

    def _build_text(self) -> Text:
        current, total = self._position
        bot_type = type(self._bot).__name__
        parts = [
            f"{self._bot.emoji} {self._bot.name} ({bot_type})",
            f"{current} of {total}",
            "Ctrl-N: next bot",
        ]
        if self._total > 0:
            if self._remaining == 0:
                parts.append("(no more examples)")
            elif self._remaining == 1:
                parts.append("Ctrl-E: last example")
            else:
                parts.append(f"Ctrl-E: example ({self._remaining} left)")
        return Text("  \N{BULLET}  ".join(parts))

    def render(self) -> Text:
        """Build header text from current state."""
        return self._build_text()

    def update_prompt_state(self, remaining: int) -> None:
        """Update the remaining prompt count and refresh the display."""
        self._remaining = remaining
        self.refresh()
