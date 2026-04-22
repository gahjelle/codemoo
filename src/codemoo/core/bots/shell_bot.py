"""LLM bot that can execute shell commands via a single tool call."""

import dataclasses

from codemoo.core.bots.general_tool_bot import GeneralToolBot

_INSTRUCTIONS = """
You can run shell commands using the run_shell tool. When the user asks you to execute
a command, inspect runtime state, or perform a system operation, call run_shell with
the appropriate command before answering.
""".strip()


@dataclasses.dataclass(eq=False)
class ShellBot(GeneralToolBot):
    """Chat participant that runs shell commands on demand before delivering a reply.

    Demonstrates tool use applied to the shell: ask the LLM → detect a run_shell
    request → execute the command → re-ask with the output.
    """

    instructions: str = _INSTRUCTIONS
