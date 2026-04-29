"""Tests for SelectionApp's pure helper functions."""

from codemoo.chat.selection import _bot_label
from codemoo.core.backend import LLMBackend
from codemoo.core.bots import ChatBot, EchoBot, LlmBot


class _StubBackend:
    async def complete(self, messages: object) -> str:
        return ""


_BACKEND: LLMBackend = _StubBackend()


def test_label_includes_name_and_type() -> None:
    bot = LlmBot(name="Llm", emoji="\N{SPARKLES}", backend=_BACKEND)
    assert _bot_label(bot) == "\N{SPARKLES} Llm (LlmBot)"


def test_label_echo_bot() -> None:
    assert _bot_label(EchoBot(name="Echo", emoji="O")) == "O Echo (EchoBot)"


def test_label_chat_bot() -> None:
    bot = ChatBot(name="Chat", emoji="O", backend=_BACKEND)
    assert _bot_label(bot) == "O Chat (ChatBot)"
