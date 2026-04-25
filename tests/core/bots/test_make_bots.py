from codemoo.config import config
from codemoo.core.backend import TextResponse, ToolUse
from codemoo.core.bots import make_bots
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.echo_bot import EchoBot


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return ""

    async def complete_step(
        self, messages: object, tools: object
    ) -> TextResponse | ToolUse:
        return TextResponse(text="")


def _bots() -> list:
    return make_bots(
        _MockBackend(),
        human_name="You",
        cfg=config.bots,
        bot_order=config.scripts["default"],
    )


def test_make_bots_returns_eight_bots() -> None:
    assert len(_bots()) == 8


def test_make_bots_first_is_echo_bot() -> None:
    assert isinstance(_bots()[0], EchoBot)


def test_make_bots_last_is_shell_bot() -> None:
    assert isinstance(_bots()[-1], AgentBot)
