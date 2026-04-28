"""LLM bot that performs M365 actions (email, calendar, Teams) via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot

_INSTRUCTIONS = """
You can perform Microsoft 365 actions using your tools: send emails, create calendar
events, post Teams messages, and write SharePoint documents. When the user asks you to
perform such an action, call the appropriate tool before answering. These actions have
real consequences — confirm intent when uncertain.
""".strip()


@dataclasses.dataclass(eq=False)
class SendBot(SingleTurnToolBot):
    """Chat participant that performs M365 actions before replying.

    Demonstrates consequential M365 tool use: ask the LLM → detect an action request
    → execute via Graph API → re-ask with the result. State changes here.
    """

    instructions: str = _INSTRUCTIONS
