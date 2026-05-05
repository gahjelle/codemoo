"""LLM bot that performs M365 or Google Workspace actions via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot


@dataclasses.dataclass(eq=False)
class SendBot(SingleTurnToolBot):
    """Chat participant that performs M365 or Google Workspace actions before replying.

    Demonstrates consequential tool use: ask the LLM → detect an action request
    → execute via API → re-ask with the result. State changes here.
    """
