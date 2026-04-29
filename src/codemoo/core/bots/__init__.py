"""Bot participants for the Codemoo chat loop."""

from codemoo.config.schema import BotConfig, BotRef, BotType, ResolvedBotConfig, resolve
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
    "BotConfig",
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
    bot: ResolvedBotConfig,
    llm: ToolLLMBackend,
    commentator: CommentatorBot | None,
) -> ChatParticipant:
    """Construct a single bot by type, resolving tools from TOOL_REGISTRY."""
    tools = [TOOL_REGISTRY[name] for name in bot.tools]
    match bot.bot_type:
        case "EchoBot":
            return EchoBot(name=bot.name, emoji=bot.emoji)
        case "LlmBot":
            return LlmBot(name=bot.name, emoji=bot.emoji, llm=llm)
        case "ChatBot":
            return ChatBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
            )
        case "SystemBot":
            return SystemBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                instructions=bot.instructions,
            )
        case "ToolBot":
            return ToolBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )
        case "ReadBot":
            return ReadBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )
        case "ChangeBot":
            return ChangeBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )
        case "ScanBot":
            return ScanBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )
        case "SendBot":
            return SendBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )
        case "AgentBot":
            return AgentBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )
        case "GuardBot":
            return GuardBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                commentator=commentator,
            )


def make_bots(
    llm: ToolLLMBackend,
    *,
    cfg: dict[BotType, BotConfig],
    bot_refs: list[BotRef],
    commentator: CommentatorBot | None = None,
) -> tuple[list[ChatParticipant], list[ResolvedBotConfig]]:
    """Return bots and their resolved configs, in the order given by bot_refs."""
    resolved_list = [resolve(cfg, ref) for ref in bot_refs]
    bots = [_make_bot(bot, llm, commentator) for bot in resolved_list]
    return bots, resolved_list


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
