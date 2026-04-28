"""LLM bot that can read files and list directories via tool calls."""

import dataclasses

from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot

_INSTRUCTIONS = """
You can read files and list directory contents using your tools. When the user asks
about a file, its contents, or what files exist in a folder, call the appropriate
tool to retrieve that information before answering.
""".strip()


@dataclasses.dataclass(eq=False)
class ReadBot(SingleTurnToolBot):
    """Chat participant that reads files and lists directories before replying.

    Demonstrates read-only tool use: ask the LLM → detect a read or list request
    → fetch the data → re-ask with the results. No writes occur.
    """

    instructions: str = _INSTRUCTIONS
