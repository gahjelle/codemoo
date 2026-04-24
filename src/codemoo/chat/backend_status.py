"""BackendStatus widget showing the active LLM backend and model."""

from textual.widgets import Label

from codemoo.llm.factory import BackendInfo


class BackendStatus(Label):
    """Footer bar showing the active backend name and model.

    Always visible, regardless of demo mode.
    Structural layout (height) is defined here; visual styling lives in chat.tcss.
    """

    DEFAULT_CSS = """
    BackendStatus {
        height: 1;
        width: 1fr;
    }
    """

    def __init__(self, backend_info: BackendInfo) -> None:
        """Initialise with the active backend info."""
        text = f"{backend_info.name}  \N{BULLET}  {backend_info.model}"
        super().__init__(text)
