"""LLM bot that performs M365 actions (email, calendar, Teams) via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot


@dataclasses.dataclass(eq=False)
class SendBot(SingleTurnToolBot):
    """Chat participant that performs M365 actions before replying.

    Demonstrates consequential M365 tool use: ask the LLM → detect an action request
    → execute via Graph API → re-ask with the result. State changes here.
    """
