"""Startup bot selection screen for choosing participants before the chat."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Label, SelectionList

from codaroo.core.participant import ChatParticipant

_BOT_TYPE_ORDER: dict[str, int] = {"EchoBot": 0, "LLMBot": 1, "ChatBot": 2}


def _bot_sort_key(bot: ChatParticipant) -> int:
    """Return the position of a bot in the fixed display order."""
    return _BOT_TYPE_ORDER.get(type(bot).__name__, 999)


def _bot_label(bot: ChatParticipant) -> str:
    """Format a bot's selection list label as 'Name (TypeName)'."""
    return f"{bot.name} ({type(bot).__name__})"


class SelectionApp(App[list[ChatParticipant]]):
    """Startup screen that lets the user pick which bots join the session."""

    CSS_PATH = Path(__file__).parent / "chat.tcss"

    def __init__(self, available_bots: list[ChatParticipant]) -> None:
        """Initialise with the full candidate bot list."""
        super().__init__()
        self._available_bots = sorted(available_bots, key=_bot_sort_key)

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
        # Preserve the fixed type order within the selection
        selected: list[ChatParticipant] = sorted(
            selection_list.selected, key=_bot_sort_key
        )
        self.exit(selected)
