"""LLM bot that reads M365 data (SharePoint, email, calendar) via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot


@dataclasses.dataclass(eq=False)
class ScanBot(SingleTurnToolBot):
    """Chat participant that reads M365 data before replying.

    Demonstrates read-only M365 tool use: ask the LLM → detect a read request
    → fetch from Graph API → re-ask with the results. No writes occur.
    """
