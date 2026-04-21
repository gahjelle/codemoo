"""ThinkingStatus widget that shows which bot is currently processing a request."""

from textual.widgets import Label


class ThinkingStatus(Label):
    """A status bar that shows which participant is currently awaiting an LLM response.

    Hidden when idle; visible while a bot is thinking.
    Structural layout (height) is defined here; visual styling lives in chat.tcss.
    """

    DEFAULT_CSS = """
    ThinkingStatus {
        height: 1;
    }
    """

    def on_mount(self) -> None:  # noqa: D102
        self.display = False

    def set_bot(self, emoji: str, name: str) -> None:
        """Show the status bar with the active bot's identity."""
        self.update(f"{emoji} {name} is thinking\N{HORIZONTAL ELLIPSIS}")
        self.display = True

    def clear(self) -> None:
        """Hide the status bar."""
        self.update("")
        self.display = False
