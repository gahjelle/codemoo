"""Shared approval gate data model and helpers for gated bots."""

import dataclasses

from codemoo.core.backend import ToolUse


@dataclasses.dataclass(frozen=True)
class Approved:
    """The user approved the tool call — execute as planned."""


@dataclasses.dataclass(frozen=True)
class Denied:
    """The user denied the tool call, with an optional instruction."""

    reason: str | None = None


type GuardDecision = Approved | Denied


@dataclasses.dataclass(frozen=True)
class ApprovalRequest:
    """Carries the context needed to display an approval modal."""

    bot_name: str
    tool_use: ToolUse


def _denial_message(decision: Denied) -> str:
    if decision.reason:
        return f"Tool call denied: {decision.reason}"
    return (
        "The user denied this tool call."
        " Do not attempt it again — move on to the next step."
    )


async def _async_approved(_: ApprovalRequest) -> GuardDecision:
    return Approved()
