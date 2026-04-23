from codemoo.core.backend import TextResponse, ToolUse
from codemoo.core.bots import make_bots
from codemoo.core.bots.chat_bot import ChatBot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.file_bot import FileBot
from codemoo.core.bots.llm_bot import LLMBot
from codemoo.core.bots.shell_bot import ShellBot
from codemoo.core.bots.system_bot import SystemBot
from codemoo.core.bots.tool_bot import ToolBot


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return ""

    async def complete_step(
        self, messages: object, tools: object
    ) -> TextResponse | ToolUse:
        return TextResponse(text="")


def _bots() -> list:
    return make_bots(_MockBackend(), "You")  # type: ignore[arg-type]


def test_make_bots_returns_seven_bots() -> None:
    assert len(_bots()) == 7


def test_make_bots_order() -> None:
    types = [type(b) for b in _bots()]
    assert types == [EchoBot, LLMBot, ChatBot, SystemBot, ToolBot, FileBot, ShellBot]


def test_make_bots_names() -> None:
    names = [b.name for b in _bots()]
    assert names == ["Coco", "Mono", "Iris", "Sona", "Telo", "Rune", "Ash"]


def test_make_bots_first_is_echo_bot() -> None:
    assert isinstance(_bots()[0], EchoBot)


def test_make_bots_last_is_shell_bot() -> None:
    assert isinstance(_bots()[-1], ShellBot)
