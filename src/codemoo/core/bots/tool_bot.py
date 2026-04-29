"""LLM bot that can invoke tools in a single explicit round-trip."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot


@dataclasses.dataclass(eq=False)
class ToolBot(SingleTurnToolBot):
    """Chat participant that can call tools before delivering a final reply.

    Demonstrates the tool-call round-trip explicitly:
    ask the LLM → detect a tool request → invoke the tool → re-ask with the result.
    """
