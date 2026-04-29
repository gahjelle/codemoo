"""LLM bot that can read files and list directories via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot


@dataclasses.dataclass(eq=False)
class ReadBot(SingleTurnToolBot):
    """Chat participant that reads files and lists directories before replying.

    Demonstrates read-only tool use: ask the LLM → detect a read or list request
    → fetch the data → re-ask with the results. No writes occur.
    """
