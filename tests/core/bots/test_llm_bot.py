import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.llm_bot import LlmBot

from .conftest import user_ctx


class _MockBackend:
    """Captures calls and returns a fixed response."""

    def __init__(self, response: str = "mock response") -> None:
        self.response = response
        self.calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        self.calls.append(list(messages))
        return self.response


@pytest.fixture
def mock_backend() -> _MockBackend:
    return _MockBackend()


@pytest.fixture
def llm_bot(mock_backend: _MockBackend) -> LlmBot:
    return LlmBot(name="LLMBot", emoji="\N{ROBOT FACE}", llm=mock_backend)


@pytest.mark.asyncio
async def test_llm_bot_sends_only_current_message(
    llm_bot: LlmBot, mock_backend: _MockBackend
) -> None:
    await llm_bot.on_message(user_ctx("latest"))

    assert len(mock_backend.calls) == 1
    assert mock_backend.calls[0] == [Message(role="user", content="latest")]


@pytest.mark.asyncio
async def test_llm_bot_returns_response_as_context_item(
    llm_bot: LlmBot, mock_backend: _MockBackend
) -> None:
    from codemoo.core.context_items import AssistantMessageContent

    mock_backend.response = "I am a bot"
    [item] = await llm_bot.on_message(user_ctx("hi"))

    assert isinstance(item.content, AssistantMessageContent)
    assert item.content.text == "I am a bot"
