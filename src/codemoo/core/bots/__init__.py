"""Bot participants for the Codemoo chat loop."""

from codemoo.config.schema import BotConfig, ModeName
from codemoo.core.backend import ToolLLMBackend
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.change_bot import ChangeBot
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.bots.guard_bot import GuardBot
from codemoo.core.bots.llm_bot import LlmBot
from codemoo.core.bots.read_bot import ReadBot
from codemoo.core.bots.scan_bot import ScanBot
from codemoo.core.bots.send_bot import SendBot
from codemoo.core.bots.system_bot import SystemBot
from codemoo.core.bots.tool_bot import ToolBot
from codemoo.core.participant import ChatParticipant
from codemoo.core.tools import TOOL_REGISTRY

__all__ = [
    "AgentBot",
    "ChangeBot",
    "ChatBot",
    "CommentatorBot",
    "EchoBot",
    "ErrorBot",
    "GuardBot",
    "LlmBot",
    "ReadBot",
    "ScanBot",
    "SendBot",
    "SystemBot",
    "ToolBot",
    "make_bots",
    "resolve_bot",
]


def _make_bot(  # noqa: C901, PLR0911
    cfg: BotConfig,
    backend: ToolLLMBackend,
    human_name: str,
    commentator: CommentatorBot | None,
) -> ChatParticipant:
    """Construct a single bot by type, resolving tools from TOOL_REGISTRY."""
    tools = [TOOL_REGISTRY[name] for name in cfg.tools]
    match cfg.type:
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
                tools=tools,
                commentator=commentator,
            )
        case "ReadBot":
            return ReadBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=tools,
                commentator=commentator,
            )
        case "ChangeBot":
            return ChangeBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=tools,
                commentator=commentator,
            )
        case "ScanBot":
            return ScanBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=tools,
                commentator=commentator,
            )
        case "SendBot":
            return SendBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=tools,
                commentator=commentator,
            )
        case "AgentBot":
            return AgentBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=tools,
                commentator=commentator,
            )
        case "GuardBot":
            return GuardBot(
                name=cfg.name,
                emoji=cfg.emoji,
                backend=backend,
                human_name=human_name,
                tools=tools,
                commentator=commentator,
            )


def make_bots(  # noqa: PLR0913
    backend: ToolLLMBackend,
    *,
    human_name: str,
    cfg: dict[str, BotConfig],
    bot_order: list[str],
    mode: ModeName = "code",
    commentator: CommentatorBot | None = None,
) -> list[ChatParticipant]:
    """Return bots instantiated in the order given by bot_order."""
    _ = mode  # mode is available for future use by callers; tools are wired via config
    return [_make_bot(cfg[t], backend, human_name, commentator) for t in bot_order]


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
