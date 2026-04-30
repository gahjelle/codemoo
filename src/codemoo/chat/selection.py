"""Startup bot selection screen for choosing participants before the chat."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Label, SelectionList

from codemoo.config.schema import ResolvedBotConfig


def _bot_label(bot: ResolvedBotConfig) -> str:
    """Format a resolved bot's selection label as 'Emoji Name (Type) • variant'."""
    return f"{bot.emoji} {bot.name} ({bot.bot_type}) \N{BULLET} {bot.variant}"


class SelectionApp(App[list[ResolvedBotConfig]]):
    """Startup screen that lets the user pick which bots join the session."""

    CSS_PATH = Path(__file__).parent / "chat.tcss"

    def __init__(self, available_bots: list[ResolvedBotConfig]) -> None:
        """Initialise with the full catalog of resolved bot configs."""
        super().__init__()
        self._available_bots = available_bots

    def compose(self) -> ComposeResult:
        """Yield the title, selection list, and confirm button."""
        with Vertical(id="selection-container"):
            yield Label("Choose bots to join the conversation", id="selection-title")
            yield SelectionList(
                *[(_bot_label(bot), bot) for bot in self._available_bots],
                id="bot-list",
            )
            yield Button("Start Chat", id="start-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Confirm selection and exit with the ordered list of chosen bots."""
        if event.button.id != "start-btn":
            return
        selection_list = self.query_one("#bot-list", SelectionList)
        self.exit(selection_list.selected)
