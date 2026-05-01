"""TUI entry point for the codemoo command."""

import asyncio
from dataclasses import dataclass
from typing import NoReturn

import configaroo
import cyclopts
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.chat.slides import DemoContext
from codemoo.config import config
from codemoo.config.schema import (
    BotRef,
    BotType,
    ResolvedBotConfig,
    ScriptName,
    resolve,
)
from codemoo.core import bots as bot_module
from codemoo.core.backend import LLMBackend
from codemoo.core.bots import make_bots, resolve_bot, run_init_hooks
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.factory import BackendInfo, resolve_backend
from codemoo.m365.tools import M365_TOOL_REGISTRY


@dataclass
class SetupResult:
    """Basic set up of the coding assistant."""

    llm: LLMBackend
    backend_info: BackendInfo
    human: HumanParticipant
    available: list[ChatParticipant]
    resolved_bots: list[ResolvedBotConfig]
    error_bot: ErrorBot
    commentator_bot: CommentatorBot


# One app defaults to code bots/scripts, while the other to business bots/scripts
code_app = cyclopts.App(help="Codemoo — demo coding agents step by step.")
business_app = cyclopts.App(help="Collebra - demo enterprise agents step by step.")


def _setup(script: ScriptName = "default") -> SetupResult:
    llm_backend, backend_info = resolve_backend(config)
    human = HumanParticipant()
    language = config.language
    error_bot = bot_module.ErrorBot(llm=llm_backend, language=language)
    commentator_bot = bot_module.CommentatorBot(llm=llm_backend, language=language)

    available, resolved_bots = make_bots(
        llm_backend,
        cfg=config.bots,
        bot_refs=config.scripts[script].bots,
        commentator=commentator_bot,
    )
    return SetupResult(
        llm=llm_backend,
        backend_info=backend_info,
        human=human,
        available=available,
        resolved_bots=resolved_bots,
        error_bot=error_bot,
        commentator_bot=commentator_bot,
    )


@code_app.default
def code_chat(*, bot: BotType = "GuardBot", variant: str = "code") -> None:
    """Launch the code chat with the main bot, or a specific one via --bot/--variant."""
    try:
        return _chat(bot=bot, variant=variant)
    except ValueError as err:
        _raise_error(str(err))


@business_app.default
def business_chat(*, bot: BotType = "GuardBot", variant: str = "business") -> None:
    """Launch the business chat with the main bot, or a specific one via --bot/--variant."""  # noqa: E501
    try:
        return _chat(bot=bot, variant=variant)
    except ValueError as err:
        _raise_error(str(err))


def _chat(*, bot: BotType, variant: str) -> None:
    """Instantiate a single bot and launch the chat."""
    bot_ref = BotRef(type=bot, variant=variant)
    llm_backend, backend_info = resolve_backend(config)
    human = HumanParticipant()
    language = config.language
    error_bot = bot_module.ErrorBot(llm=llm_backend, language=language)
    commentator_bot = bot_module.CommentatorBot(llm=llm_backend, language=language)

    available, resolved_bots = make_bots(
        llm_backend,
        cfg=config.bots,
        bot_refs=[bot_ref],
        commentator=commentator_bot,
    )
    _run_init_hooks_for_resolved(resolved_bots)
    ChatApp(
        participants=[human, *available],
        error_bot=error_bot,
        commentator_bot=commentator_bot,
        backend_info=backend_info,
        resolved_bots=resolved_bots,
    ).run()


@code_app.command
@business_app.command
def show_config(section: str | None = None) -> None:
    """Show the Codemoo configuration."""
    configaroo.print_configuration(config, section=section)


@code_app.command
@business_app.command
def list_bots(*, script: ScriptName = "default") -> None:
    """List all available bots with their index, type, and name."""
    setup = _setup(script)
    table = Table(show_header=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Type")
    table.add_column("Bot")
    table.add_column("Variant")
    for i, bot in enumerate(setup.resolved_bots, start=1):
        table.add_row(str(i), bot.bot_type, f"{bot.emoji} {bot.name}", bot.variant)
    Console().print(table)


@code_app.command
@business_app.command
def list_scripts() -> None:
    """List all configured scripts with their ordered bot types."""
    table = Table(show_header=True)
    table.add_column("Script")
    table.add_column("Bots")
    for name, script_cfg in config.scripts.items():
        bots_str = ", ".join(f"{r.type}:{r.variant}" for r in script_cfg.bots)
        table.add_row(name, bots_str)
    Console().print(table)


@code_app.command(name="select")
@business_app.command(name="select")
def select() -> None:
    """Show the full bot catalog and start chat with the chosen bot(s)."""
    all_resolved = [
        resolve(config.bots, BotRef(type=bot_type, variant=variant_name))
        for bot_type, bot_cfg in config.bots.items()
        for variant_name in bot_cfg.variants
    ]

    selected: list[ResolvedBotConfig] | None = SelectionApp(all_resolved).run()
    if not selected:
        return

    llm_backend, backend_info = resolve_backend(config)
    human = HumanParticipant()
    language = config.language
    error_bot = bot_module.ErrorBot(llm=llm_backend, language=language)
    commentator_bot = bot_module.CommentatorBot(llm=llm_backend, language=language)

    _run_init_hooks_for_resolved(selected)

    bot_refs = [BotRef(type=r.bot_type, variant=r.variant) for r in selected]
    available, resolved_bots = make_bots(
        llm_backend,
        cfg=config.bots,
        bot_refs=bot_refs,
        commentator=commentator_bot,
    )
    participants: list[ChatParticipant] = [human, *available]
    ChatApp(
        participants=participants,
        error_bot=error_bot,
        commentator_bot=commentator_bot,
        backend_info=backend_info,
        resolved_bots=resolved_bots,
    ).run()


@code_app.command(name="demo")
def code_demo(
    *, script: ScriptName = "default", start: str | None = None, end: str | None = None
) -> None:
    """Run the bot progression demo. Use Ctrl-N to advance to the next bot."""
    try:
        asyncio.run(_run_demo(script, start, end))
    except ValueError as err:
        _raise_error(str(err))


@business_app.command(name="demo")
def business_demo(
    *, script: ScriptName = "m365", start: str | None = None, end: str | None = None
) -> None:
    """Run the bot progression demo. Use Ctrl-N to advance to the next bot."""
    try:
        asyncio.run(_run_demo(script, start, end))
    except ValueError as err:
        _raise_error(str(err))


async def _run_demo(script: ScriptName, start: str | None, end: str | None) -> None:
    """Run the demo loop in a single event loop so shared async resources stay valid."""
    setup = _setup(script)
    start_index = (
        setup.available.index(resolve_bot(start, setup.available))
        if start is not None
        else 0
    )
    end_index = (
        setup.available.index(resolve_bot(end, setup.available))
        if end is not None
        else len(setup.available) - 1
    )
    demo_bots = setup.available[start_index : end_index + 1]
    demo_resolved = setup.resolved_bots[start_index : end_index + 1]

    # Run all init hooks upfront so auth fires before the first slide
    _run_init_hooks_for_resolved(setup.resolved_bots[start_index : end_index + 1])

    for i, bot in enumerate(demo_bots):
        prev_bot = demo_bots[i - 1] if i > 0 else None
        context = DemoContext(
            all_bots=demo_bots,
            resolved_configs=demo_resolved,
            prev_bot=prev_bot,
            llm=setup.llm,
            position=(i + 1, len(demo_bots)),
            prompts=list(demo_resolved[i].prompts),
        )
        result = await ChatApp(
            participants=[setup.human, bot],
            error_bot=setup.error_bot,
            commentator_bot=setup.commentator_bot,
            demo_context=context,
            backend_info=setup.backend_info,
            resolved_bots=[demo_resolved[i]],
        ).run_async()
        if result != "next":
            break


def _run_init_hooks_for_resolved(resolved_bots: list[ResolvedBotConfig]) -> None:
    """Collect all tools across the resolved bots and run unique init hooks."""
    all_tools = [
        M365_TOOL_REGISTRY[name]
        for r in resolved_bots
        for name in r.tools
        if name in M365_TOOL_REGISTRY
    ]
    run_init_hooks(all_tools)


def _raise_error(text: str) -> NoReturn:
    """Raise an error, mimicking how Cyclopts show errors."""
    Console(stderr=True).print(
        Panel(text, title="Error", border_style="red", title_align="left")
    )
    raise SystemExit(1) from None
