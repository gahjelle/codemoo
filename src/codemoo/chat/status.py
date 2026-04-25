"""ThinkingStatus widget that shows which bot is currently processing a request."""

import time

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

    def __init__(self) -> None:
        """Initialize timer tracking fields."""
        super().__init__()
        self._start_time = None
        self._update_task = None
        self._current_bot = None

    def on_mount(self) -> None:  # noqa: D102
        self.display = False

    def set_bot(self, emoji: str, name: str) -> None:
        """Start timer and begin periodic updates."""
        self._start_time = time.perf_counter()
        self._current_bot = (emoji, name)
        self._update_status_display()
        # Update every second
        self._update_task = self.set_interval(1.0, self._update_status_display)
        self.display = True

    def _update_status_display(self) -> None:
        """Update display with current thinking time."""
        if self._start_time and self._current_bot:
            elapsed = time.perf_counter() - self._start_time
            seconds = round(elapsed)
            emoji, name = self._current_bot
            self.update(
                f"{emoji} {name} is thinking\N{HORIZONTAL ELLIPSIS} ({seconds}s)"
            )

    def clear(self) -> int | None:
        """Stop timer and return duration in seconds."""
        if self._update_task:
            self._update_task.stop()
            self._update_task = None

        duration = None
        if self._start_time:
            elapsed = time.perf_counter() - self._start_time
            duration = round(elapsed)
            self._start_time = None
            self._current_bot = None

        self.update("")
        self.display = False
        return duration
