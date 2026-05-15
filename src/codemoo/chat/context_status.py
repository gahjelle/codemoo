"""ContextStatus widget showing conversation statistics for capability-aware bots."""

from textual.widgets import Label


class ContextStatus(Label):
    """A status bar that shows context statistics when context_management is active.

    Hidden until the first message is exchanged.
    Structural layout (height) is defined here; visual styling lives in chat.tcss.
    """

    DEFAULT_CSS = """
    ContextStatus {
        height: 1;
    }
    """

    def on_mount(self) -> None:  # noqa: D102
        self.display = False

    def update_message_count(self, count: int) -> None:
        """Update the displayed message count and make the widget visible."""
        self.update(f"Num messages: {count}")
        self.display = True
