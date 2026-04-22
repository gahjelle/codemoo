"""LLM bot that can read files from disk via a single tool call."""

import dataclasses

from codemoo.core.bots.general_tool_bot import GeneralToolBot

_INSTRUCTIONS = """
You can read files using the read_file tool. When the user asks about a file or its
contents, call read_file with the file path to retrieve it before answering.
""".strip()


@dataclasses.dataclass(eq=False)
class FileBot(GeneralToolBot):
    """Chat participant that reads files on demand before delivering a reply.

    Demonstrates tool use applied to the filesystem: ask the LLM → detect a
    read_file request → load the file → re-ask with the contents.
    """

    instructions: str = _INSTRUCTIONS
