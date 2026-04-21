"""Tests for SelectionApp's pure helper functions."""

from codemoo.chat.selection import _bot_label, _bot_sort_key
from codemoo.core.echo_bot import EchoBot
from codemoo.llm.backend import LLMBackend
from codemoo.llm.bots import ChatBot, LLMBot


class _StubBackend:
    async def complete(self, messages: object) -> str:
        return ""


_BACKEND: LLMBackend = _StubBackend()  # type: ignore[assignment]


def test_echo_bot_sorts_first() -> None:
    echo = EchoBot()
    llm = LLMBot(name="X", emoji="", backend=_BACKEND)
    chat = ChatBot(name="Y", emoji="", backend=_BACKEND, human_name="You")
    assert _bot_sort_key(echo) < _bot_sort_key(llm) < _bot_sort_key(chat)


def test_unknown_type_sorts_last() -> None:
    class _OtherBot:
        name = "Other"
        emoji = ""
        is_human = False

        async def on_message(self, message: object, history: object) -> None:
            return None

    assert _bot_sort_key(_OtherBot()) == 999  # type: ignore[arg-type]


def test_label_includes_name_and_type() -> None:
    bot = LLMBot(name="Mistral", emoji="\N{SPARKLES}", backend=_BACKEND)
    assert _bot_label(bot) == "Mistral (LLMBot)"


def test_label_echo_bot() -> None:
    assert _bot_label(EchoBot()) == "EchoBot (EchoBot)"


def test_label_chat_bot() -> None:
    bot = ChatBot(name="Mistral Chat", emoji="", backend=_BACKEND, human_name="You")
    assert _bot_label(bot) == "Mistral Chat (ChatBot)"
