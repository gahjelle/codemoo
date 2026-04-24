"""TUI entry point for the codemoo command."""

import asyncio

import configaroo
import cyclopts
from rich.console import Console
from rich.table import Table

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.chat.slides import DemoContext
from codemoo.config import config
from codemoo.core import bots as bot_module
from codemoo.core.backend import ToolLLMBackend
from codemoo.core.bots import make_bots, resolve_bot
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.backend import create_mistral_backend

_SetupResult = tuple[
    ToolLLMBackend, HumanParticipant, list[ChatParticipant], ErrorBot, CommentatorBot
]

app = cyclopts.App(help="Codemoo — demo coding agents step by step.")


def _setup() -> _SetupResult:
    backend = create_mistral_backend()
    human = HumanParticipant()
    error_bot = bot_module.ErrorBot(backend=backend)
    commentator_bot = bot_module.CommentatorBot(backend=backend)
    available = make_bots(backend, human.name, commentator=commentator_bot)
    return backend, human, available, error_bot, commentator_bot


@app.default
def chat(*, bot: str | None = None) -> None:
    """Launch the chat with the most capable bot, or a specific one via --bot."""
    _, human, available, error_bot, commentator_bot = _setup()
    chosen = resolve_bot(bot, available) if bot is not None else available[-1]
    ChatApp(
        participants=[human, chosen],
        error_bot=error_bot,
        commentator_bot=commentator_bot,
    ).run()


@app.command
def show_config(section: str | None = None) -> None:
    """Show the Codemoo configuration."""
    configaroo.print_configuration(config, section=section)


@app.command
def list_bots() -> None:
    """List all available bots with their index, type, and name."""
    backend = create_mistral_backend()
    bots = make_bots(backend, "")
    table = Table(show_header=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Type")
    table.add_column("Bot")
    for i, bot in enumerate(bots, start=1):
        table.add_row(str(i), type(bot).__name__, f"{bot.emoji} {bot.name}")
    Console().print(table)


@app.command
def select() -> None:
    """Choose bots interactively before starting the chat."""
    _, human, available, error_bot, commentator_bot = _setup()
    selected = SelectionApp(available).run()
    participants: list[ChatParticipant] = [human, *(selected or [])]
    ChatApp(
        participants=participants,
        error_bot=error_bot,
        commentator_bot=commentator_bot,
    ).run()


@app.command
def demo(*, start: str | None = None) -> None:
    """Run the bot progression demo. Use Ctrl-N to advance to the next bot."""
    asyncio.run(_run_demo(start))


async def _run_demo(start: str | None) -> None:
    """Run the demo loop in a single event loop so shared async resources stay valid."""
    backend, human, available, error_bot, commentator_bot = _setup()
    index = available.index(resolve_bot(start, available)) if start is not None else 0
    demo_bots = available[index:]
    for i, bot in enumerate(demo_bots):
        prev_bot = demo_bots[i - 1] if i > 0 else None
        context = DemoContext(
            all_bots=demo_bots,
            prev_bot=prev_bot,
            backend=backend,
            position=(i + 1, len(demo_bots)),
        )
        result = await ChatApp(
            participants=[human, bot],
            error_bot=error_bot,
            commentator_bot=commentator_bot,
            demo_context=context,
        ).run_async()
        if result != "next":
            break
