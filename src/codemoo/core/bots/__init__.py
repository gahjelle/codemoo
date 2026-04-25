"""Bot participants for the Codemoo chat loop."""

from codemoo.config.schema import BotConfig, BotType
from codemoo.core.backend import ToolLLMBackend
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.bots.file_bot import FileBot
from codemoo.core.bots.llm_bot import LlmBot
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
    "LlmBot",
    "ShellBot",
    "SystemBot",
    "ToolBot",
    "make_bots",
    "resolve_bot",
]


def _make_bot(  # noqa: PLR0911
    bot_type: BotType,
    cfg: BotConfig,
    backend: ToolLLMBackend,
    human_name: str,
    commentator: CommentatorBot | None,
) -> ChatParticipant:
    """Construct a single bot by type."""
    match bot_type:
        case "EchoBot":
            return EchoBot(name=cfg.name, emoji=cfg.emoji)
        case "LlmBot":
            return LlmBot(name=cfg.name, emoji=cfg.emoji, backend=backend)
        case "ChatBot":
            return ChatBot(
                name=cfg.name, emoji=cfg.emoji, backend=backend, human_name=human_name
            )
        case "SystemBot":
            return SystemBot(
                name=cfg.name, emoji=cfg.emoji, backend=backend, human_name=human_name
            )
        case "ToolBot":
            return ToolBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=[reverse_string],
                commentator=commentator,
            )
        case "FileBot":
            return FileBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=[read_file, write_file, reverse_string],
                commentator=commentator,
            )
        case "ShellBot":
            return ShellBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=[run_shell, read_file, write_file, reverse_string],
                commentator=commentator,
            )
        case "AgentBot":
            return AgentBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=[run_shell, read_file, write_file, reverse_string],
                commentator=commentator,
            )


def make_bots(
    backend: ToolLLMBackend,
    *,
    human_name: str,
    cfg: dict[BotType, BotConfig],
    bot_order: list[BotType],
    commentator: CommentatorBot | None = None,
) -> list[ChatParticipant]:
    """Return bots instantiated in the order given by bot_order."""
    return [_make_bot(t, cfg[t], backend, human_name, commentator) for t in bot_order]


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
