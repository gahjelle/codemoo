"""Bot participants for the Codemoo chat loop."""

from codemoo.core.backend import ToolLLMBackend
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.bots.file_bot import FileBot
from codemoo.core.bots.llm_bot import LLMBot
from codemoo.core.bots.shell_bot import ShellBot
from codemoo.core.bots.system_bot import SystemBot
from codemoo.core.bots.tool_bot import ToolBot
from codemoo.core.participant import ChatParticipant
from codemoo.core.tools import read_file, reverse_string, run_shell, write_file

__all__ = [
    "AgentBot",
    "ChatBot",
    "CommentatorBot",
    "EchoBot",
    "ErrorBot",
    "FileBot",
    "LLMBot",
    "ShellBot",
    "SystemBot",
    "ToolBot",
    "make_bots",
    "resolve_bot",
]


def make_bots(
    backend: ToolLLMBackend,
    human_name: str,
    commentator: CommentatorBot | None = None,
) -> list[ChatParticipant]:
    """Return the full ordered bot progression."""
    return [
        EchoBot(name="Coco", emoji="\N{PARROT}"),
        LLMBot(name="Mono", emoji="\N{SPARKLES}", backend=backend),
        ChatBot(
            name="Iris",
            emoji="\N{EYE}\N{VARIATION SELECTOR-16}",
            backend=backend,
            human_name=human_name,
        ),
        SystemBot(
            name="Sona",
            emoji="\N{PERFORMING ARTS}",
            backend=backend,
            human_name=human_name,
        ),
        ToolBot(
            name="Telo",
            emoji="\N{WRENCH}",
            backend=backend,
            human_name=human_name,
            tools=[reverse_string],
            commentator=commentator,
        ),
        FileBot(
            name="Rune",
            emoji="\N{FILE FOLDER}",
            backend=backend,
            human_name=human_name,
            tools=[read_file, write_file, reverse_string],
            commentator=commentator,
        ),
        ShellBot(
            name="Ash",
            emoji="\N{SPIRAL SHELL}",
            backend=backend,
            human_name=human_name,
            tools=(all_tools := [run_shell, read_file, write_file, reverse_string]),
            commentator=commentator,
        ),
        AgentBot(
            name="Loom",
            emoji="\N{CYCLONE}",
            backend=backend,
            human_name=human_name,
            tools=all_tools,
            commentator=commentator,
        ),
    ]


def resolve_bot(spec: str, bots: list[ChatParticipant]) -> ChatParticipant:
    """Resolve a bot by 1-based index, case-insensitive name, or type name."""
    # Try 1-based integer index first
    try:
        index = int(spec)
    except ValueError:
        pass
    else:
        if 1 <= index <= len(bots):
            return bots[index - 1]
        msg = f"Index {index!r} out of range - valid range is 1-{len(bots)}"
        raise ValueError(msg)

    folded = spec.casefold()

    for bot in bots:
        if bot.name.casefold() == folded:
            return bot

    for bot in bots:
        if type(bot).__name__.casefold() == folded:
            return bot

    valid = ", ".join(
        f"{i + 1}={b.name}({type(b).__name__})" for i, b in enumerate(bots)
    )
    msg = f"Unknown bot spec {spec!r} — valid options: {valid}"
    raise ValueError(msg)
