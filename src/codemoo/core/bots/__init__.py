"""Bot participants for the Codemoo chat loop."""

import dataclasses
from collections.abc import Iterable
from pathlib import Path

from codemoo.config.schema import BotConfig, BotRef, BotType, ResolvedBotConfig, resolve
from codemoo.core.backend import LLMBackend
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.change_bot import ChangeBot
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.bots.compact_bot import CompactBot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.guard_bot import GuardBot
from codemoo.core.bots.llm_bot import LlmBot
from codemoo.core.bots.memory_bot import MemoryBot
from codemoo.core.bots.project_bot import ProjectBot
from codemoo.core.bots.read_bot import ReadBot
from codemoo.core.bots.retry_bot import RetryBot
from codemoo.core.bots.scan_bot import ScanBot
from codemoo.core.bots.send_bot import SendBot
from codemoo.core.bots.system_bot import SystemBot
from codemoo.core.bots.tool_bot import ToolBot
from codemoo.core.commentator import CommentatorBot
from codemoo.core.error import ErrorBot
from codemoo.core.participant import ChatParticipant
from codemoo.core.tools import TOOL_REGISTRY, ToolDef
from codemoo.core.tools.files import make_file_validator
from codemoo.core.tools.memory import make_memory_tool
from codemoo.core.tools.shell import make_shell_validator
from codemoo.m365.tools import M365_TOOL_REGISTRY
from codemoo.workspace.tools import WORKSPACE_TOOL_REGISTRY

_ALL_TOOLS: dict[str, ToolDef] = {
    **TOOL_REGISTRY,
    **M365_TOOL_REGISTRY,
    **WORKSPACE_TOOL_REGISTRY,
}

__all__ = [
    "AgentBot",
    "BotConfig",
    "ChangeBot",
    "ChatBot",
    "CommentatorBot",
    "CompactBot",
    "EchoBot",
    "ErrorBot",
    "GuardBot",
    "LlmBot",
    "MemoryBot",
    "ProjectBot",
    "ReadBot",
    "RetryBot",
    "ScanBot",
    "SendBot",
    "SystemBot",
    "ToolBot",
    "make_bots",
    "resolve_bot",
    "run_init_hooks",
]


def run_init_hooks(tools: Iterable[ToolDef]) -> None:
    """Call each unique init hook once, deduplicated by function identity."""
    seen: set[object] = set()
    for tool in tools:
        if tool.init is not None and tool.init not in seen:
            seen.add(tool.init)
            tool.init()


def _make_bot(  # noqa: C901, PLR0911, PLR0912
    bot: ResolvedBotConfig,
    llm: LLMBackend,
    commentator: CommentatorBot | None,
    session_folder: Path,
) -> ChatParticipant:
    """Construct a single bot by type, resolving tools from the combined registry."""
    _file_validator = make_file_validator(session_folder)
    _shell_validator = make_shell_validator(session_folder)
    _file_tool_names = {"read_file", "write_file", "list_files"}
    _shell_tool_names = {"run_shell"}

    def _sandbox(tool: ToolDef) -> ToolDef:
        if tool.name in _file_tool_names:
            return dataclasses.replace(tool, validate=_file_validator)
        if tool.name in _shell_tool_names:
            return dataclasses.replace(tool, validate=_shell_validator)
        return tool

    registry_names = [n for n in bot.tools if n != "save_memory"]
    tools = [_sandbox(_ALL_TOOLS[name]) for name in registry_names]
    if "save_memory" in bot.tools:
        memory_path = Path(bot.memory_file) if bot.memory_file else None
        effective_path = memory_path or session_folder / ".codemoo" / "memory.md"
        tools.append(make_memory_tool(effective_path))
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
        case "RetryBot":
            return RetryBot(
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
        case "ProjectBot":
            return ProjectBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                context_source=bot.context_source,
                session_folder=session_folder,
                commentator=commentator,
            )
        case "MemoryBot":
            return MemoryBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                context_source=bot.context_source,
                memory_file=Path(bot.memory_file) if bot.memory_file else None,
                session_folder=session_folder,
                commentator=commentator,
            )
        case "CompactBot":
            return CompactBot(
                name=bot.name,
                emoji=bot.emoji,
                llm=llm,
                tools=tools,
                instructions=bot.instructions,
                context_source=bot.context_source,
                memory_file=Path(bot.memory_file) if bot.memory_file else None,
                session_folder=session_folder,
                compact_threshold=bot.compact_threshold,
                commentator=commentator,
            )


async def make_bots(
    llm: LLMBackend,
    *,
    cfg: dict[BotType, BotConfig],
    bot_refs: list[BotRef],
    commentator: CommentatorBot | None = None,
    session_folder: Path,
) -> tuple[list[ChatParticipant], list[ResolvedBotConfig]]:
    """Return bots and their resolved configs, in the order given by bot_refs."""
    resolved_list = [resolve(cfg, ref) for ref in bot_refs]
    bots = [_make_bot(bot, llm, commentator, session_folder) for bot in resolved_list]
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
