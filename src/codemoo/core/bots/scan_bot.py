"""LLM bot that reads M365 data (SharePoint, email, calendar) via tool calls."""

import dataclasses

from codemoo.core.bots.general_tool_bot import GeneralToolBot

_INSTRUCTIONS = """
You can read Microsoft 365 data using your tools. When the user asks about documents,
emails, or calendar events, call the appropriate tool to retrieve that information
before answering. You are in read-only mode — you observe and report, but do not send
or modify anything.
""".strip()


@dataclasses.dataclass(eq=False)
class ScanBot(GeneralToolBot):
    """Chat participant that reads M365 data before replying.

    Demonstrates read-only M365 tool use: ask the LLM → detect a read request
    → fetch from Graph API → re-ask with the results. No writes occur.
    """

    instructions: str = _INSTRUCTIONS
