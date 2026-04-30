"""BackendStatus widget showing the active bot(s) and LLM backend."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from codemoo import __version__
from codemoo.config.schema import ResolvedBotConfig
from codemoo.llm.factory import BackendInfo


class BackendStatus(Widget):
    """Footer bar showing the active bot(s), backend name, and model.

    Always visible, regardless of demo mode.
    Structural layout lives in DEFAULT_CSS; visual styling in chat.tcss.
    """

    DEFAULT_CSS = """
    BackendStatus {
        height: 1;
        layout: horizontal;
    }
    """

    def __init__(
        self, backend_info: BackendInfo, resolved_bots: list[ResolvedBotConfig]
    ) -> None:
        """Initialise with the active backend info and participant bot configs."""
        super().__init__()
        bot_parts = "  \N{BULLET}  ".join(
            f"{r.bot_type} ({r.variant})" for r in resolved_bots
        )
        self._left_text = f"{bot_parts}  \N{BULLET}  {__version__}"
        self._backend_text = f"{backend_info.name}  \N{BULLET}  {backend_info.model}"

    def compose(self) -> ComposeResult:
        """Yield bot label on the left and backend/model label on the right."""
        yield Label(self._left_text, id="mode-label")
        yield Label(self._backend_text, id="backend-label")
