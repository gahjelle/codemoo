"""Approval modal shown when GuardBot requires human sign-off on a tool call."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from codemoo.core.bots.guard_bot import (
    ApprovalRequest,
    Approved,
    Denied,
    GuardDecision,
)
from codemoo.core.tools.formatting import format_tool_call


class ApprovalModal(ModalScreen[GuardDecision]):
    """Modal that presents a tool-call for human approval before it executes."""

    DEFAULT_CSS = """
    ApprovalModal {
        align: center middle;
    }
    """

    def __init__(self, request: ApprovalRequest) -> None:
        """Initialise with the approval request carrying bot name and tool use."""
        super().__init__()
        self._request = request

    def compose(self) -> ComposeResult:
        """Yield the modal container with tool info, buttons, and reason input."""
        call_display = format_tool_call(
            self._request.tool_use.name,
            self._request.tool_use.arguments,
            max_value_len=80,
        )
        bot_name = self._request.bot_name
        with Vertical(id="approval-container"):
            yield Label(
                f"\N{LOCK} {bot_name} wants to call:",
                id="approval-title",
            )
            yield Label(call_display, id="approval-call")
            with Horizontal(id="approval-buttons"):
                yield Button("Approve", id="approve", variant="success")
                yield Button("Deny", id="deny", variant="error")
                yield Button(
                    "Deny with reason\N{HORIZONTAL ELLIPSIS}",
                    id="deny-reason",
                )
            yield Label(
                f"What should {bot_name} do instead?",
                id="reason-label",
                classes="hidden",
            )
            yield Input(id="reason-input", classes="hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the three approval choices."""
        if event.button.id == "approve":
            self.dismiss(Approved())
        elif event.button.id == "deny":
            self.dismiss(Denied())
        elif event.button.id == "deny-reason":
            self.query_one("#approval-buttons").add_class("hidden")
            self.query_one("#reason-label").remove_class("hidden")
            reason_input = self.query_one("#reason-input", Input)
            reason_input.remove_class("hidden")
            reason_input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Dismiss with a reason (or plain deny if empty)."""
        reason = event.value.strip()
        self.dismiss(Denied(reason=reason or None))
