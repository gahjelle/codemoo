"""TUI entry point for the codemoo command."""

import asyncio
from typing import TYPE_CHECKING, cast

import configaroo
import cyclopts
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.chat.slides import DemoContext
from codemoo.config import config
from codemoo.config.schema import ScriptName
from codemoo.core import bots as bot_module
from codemoo.core.backend import ToolLLMBackend
from codemoo.core.bots import make_bots, resolve_bot
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.factory import BackendInfo, resolve_backend

if TYPE_CHECKING:
    from codemoo.config.schema import BotType

_SetupResult = tuple[
    ToolLLMBackend,
    BackendInfo,
    HumanParticipant,
    list[ChatParticipant],
    ErrorBot,
    CommentatorBot,
]

app = cyclopts.App(help="Codemoo — demo coding agents step by step.")


def _setup(script: ScriptName = "default") -> _SetupResult:
    backend, backend_info = resolve_backend(config)
    human = HumanParticipant()
    language = config.language
    error_bot = bot_module.ErrorBot(backend=backend, language=language)
    commentator_bot = bot_module.CommentatorBot(backend=backend, language=language)
    available = make_bots(
        backend,
        human_name=human.name,
        cfg=config.bots,
        bot_order=config.scripts[script],
        commentator=commentator_bot,
    )
    return backend, backend_info, human, available, error_bot, commentator_bot


@app.default
def chat(*, bot: str = config.main_bot) -> None:
    """Launch the chat with the most capable bot, or a specific one via --bot."""
    _, backend_info, human, available, error_bot, commentator_bot = _setup()
    chosen = resolve_bot(bot, available)
    ChatApp(
        participants=[human, chosen],
        error_bot=error_bot,
        commentator_bot=commentator_bot,
        backend_info=backend_info,
    ).run()


@app.command
def show_config(section: str | None = None) -> None:
    """Show the Codemoo configuration."""
    configaroo.print_configuration(config, section=section)


@app.command
def list_bots() -> None:
    """List all available bots with their index, type, and name."""
    backend, _, _, _, _, _ = _setup()
    bots = make_bots(
        backend, human_name="", cfg=config.bots, bot_order=config.scripts["default"]
    )
    table = Table(show_header=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Type")
    table.add_column("Bot")
    for i, bot in enumerate(bots, start=1):
        table.add_row(str(i), type(bot).__name__, f"{bot.emoji} {bot.name}")
    Console().print(table)


@app.command
def list_scripts() -> None:
    """List all configured scripts with their ordered bot types."""
    table = Table(show_header=True)
    table.add_column("Script")
    table.add_column("Bots")
    for name, bot_order in config.scripts.items():
        table.add_row(name, ", ".join(bot_order))
    Console().print(table)


@app.command
def select() -> None:
    """Choose bots interactively before starting the chat."""
    _, backend_info, human, available, error_bot, commentator_bot = _setup()
    selected = SelectionApp(available).run()
    participants: list[ChatParticipant] = [human, *(selected or [])]
    ChatApp(
        participants=participants,
        error_bot=error_bot,
        commentator_bot=commentator_bot,
        backend_info=backend_info,
    ).run()


@app.command
def demo(
    *, script: ScriptName = "default", start: str | None = None, end: str | None = None
) -> None:
    """Run the bot progression demo. Use Ctrl-N to advance to the next bot."""
    try:
        asyncio.run(_run_demo(script, start, end))
    except ValueError as e:
        Console(stderr=True).print(Panel(str(e), title="Error", border_style="red"))
        raise SystemExit(1) from None


async def _run_demo(script: ScriptName, start: str | None, end: str | None) -> None:
    """Run the demo loop in a single event loop so shared async resources stay valid."""
    backend, backend_info, human, available, error_bot, commentator_bot = _setup(script)
    start_index = (
        available.index(resolve_bot(start, available)) if start is not None else 0
    )
    end_index = (
        available.index(resolve_bot(end, available))
        if end is not None
        else len(available) - 1
    )
    demo_bots = available[start_index : end_index + 1]
    for i, bot in enumerate(demo_bots):
        prev_bot = demo_bots[i - 1] if i > 0 else None
        bot_cfg = config.bots.get(cast("BotType", type(bot).__name__))
        prompts = list(bot_cfg.prompts) if bot_cfg else []
        context = DemoContext(
            all_bots=demo_bots,
            prev_bot=prev_bot,
            backend=backend,
            position=(i + 1, len(demo_bots)),
            prompts=prompts,
        )
        result = await ChatApp(
            participants=[human, bot],
            error_bot=error_bot,
            commentator_bot=commentator_bot,
            demo_context=context,
            backend_info=backend_info,
        ).run_async()
        if result != "next":
            break
