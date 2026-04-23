"""TUI entry point for the codemoo command."""

import cyclopts

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.core import bots as bot_module
from codemoo.core.bots import make_bots, resolve_bot
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.backend import create_mistral_backend

_SetupResult = tuple[HumanParticipant, list[ChatParticipant], ErrorBot, CommentatorBot]

app = cyclopts.App(help="Codemoo — demo coding agents step by step.")


def _setup() -> _SetupResult:
    backend = create_mistral_backend()
    human = HumanParticipant()
    error_bot = bot_module.ErrorBot(backend=backend)
    commentator_bot = bot_module.CommentatorBot(backend=backend)
    available = make_bots(backend, human.name, commentator=commentator_bot)
    return human, available, error_bot, commentator_bot


@app.default
def chat(*, bot: str | None = None) -> None:
    """Launch the chat with the most capable bot, or a specific one via --bot."""
    human, available, error_bot, commentator_bot = _setup()
    chosen = resolve_bot(bot, available) if bot is not None else available[-1]
    ChatApp(
        participants=[human, chosen],
        error_bot=error_bot,
        commentator_bot=commentator_bot,
    ).run()


@app.command
def select() -> None:
    """Choose bots interactively before starting the chat."""
    human, available, error_bot, commentator_bot = _setup()
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
    human, available, error_bot, commentator_bot = _setup()
    index = available.index(resolve_bot(start, available)) if start is not None else 0
    while index < len(available):
        result = ChatApp(
            participants=[human, available[index]],
            error_bot=error_bot,
            commentator_bot=commentator_bot,
            demo_position=(index + 1, len(available)),
        ).run()
        if result != "next":
            break
        index += 1
