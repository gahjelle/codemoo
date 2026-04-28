"""BackendStatus widget showing the active LLM backend and model."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from codemoo.config.schema import ModeName
from codemoo.llm.factory import BackendInfo


class BackendStatus(Widget):
    """Footer bar showing the active mode, backend name, and model.

    Always visible, regardless of demo mode.
    Structural layout lives in DEFAULT_CSS; visual styling in chat.tcss.
    """

    DEFAULT_CSS = """
    BackendStatus {
        height: 1;
        layout: horizontal;
    }
    """

    def __init__(self, backend_info: BackendInfo, mode: ModeName = "code") -> None:
        """Initialise with the active backend info and current mode."""
        super().__init__()
        self._mode = mode
        self._backend_text = f"{backend_info.name}  \N{BULLET}  {backend_info.model}"

    def compose(self) -> ComposeResult:
        """Yield mode label on the left and backend/model label on the right."""
        yield Label(self._mode.title(), id="mode-label")
        yield Label(self._backend_text, id="backend-label")
