"""DemoHeader widget shown at the top of ChatApp in demo mode."""

from textual.widgets import Label

from codemoo.core.participant import ChatParticipant


class DemoHeader(Label):
    """One-line header showing the active bot's identity and position."""

    DEFAULT_CSS = """
    DemoHeader {
        height: 1;
        width: 1fr;
    }
    """

    def __init__(self, bot: ChatParticipant, position: tuple[int, int]) -> None:
        """Initialise with the active bot and its (current, total) position."""
        current, total = position
        bot_type = type(bot).__name__
        text = (
            f"{bot.emoji} {bot.name} ({bot_type})"
            f"  \N{BULLET}  {current} of {total}"
            f"  \N{BULLET}  Ctrl-N: next bot"
        )
        super().__init__(text)
