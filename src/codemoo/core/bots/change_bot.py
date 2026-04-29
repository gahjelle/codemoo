"""LLM bot that can execute shell commands and write files via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot


@dataclasses.dataclass(eq=False)
class ChangeBot(SingleTurnToolBot):
    """Chat participant that executes shell commands and writes files before replying.

    Demonstrates consequential tool use: ask the LLM → detect a shell or write
    request → execute it → re-ask with the output. State changes here.
    """
