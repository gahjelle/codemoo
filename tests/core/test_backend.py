from datetime import UTC, datetime

from codemoo.core.backend import Message, build_llm_context
from codemoo.core.message import ChatMessage

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


def test_current_message_is_final_user_turn() -> None:
    result = build_llm_context([], _msg("You", "hello"), "Bot", "You", 20)

    assert result == [Message(role="user", content="hello")]


def test_human_history_mapped_to_user_role() -> None:
    history = [_msg("You", "earlier")]
    result = build_llm_context(history, _msg("You", "now"), "Bot", "You", 20)

    assert result[0] == Message(role="user", content="earlier")


def test_bot_history_mapped_to_assistant_role() -> None:
    history = [_msg("Bot", "my reply")]
    result = build_llm_context(history, _msg("You", "ok"), "Bot", "You", 20)

    assert result[0] == Message(role="assistant", content="my reply")


def test_third_party_messages_excluded() -> None:
    history = [_msg("You", "a"), _msg("OtherBot", "noise"), _msg("Bot", "b")]
    result = build_llm_context(history, _msg("You", "c"), "Bot", "You", 20)

    contents = [m.content for m in result]
    assert "noise" not in contents
    assert contents == ["a", "b", "c"]


def test_clips_to_max_messages() -> None:
    history = [_msg("You", f"msg{i}") for i in range(5)]
    result = build_llm_context(history, _msg("You", "final"), "Bot", "You", 2)

    # 2 most recent history entries + current
    assert len(result) == 3
    assert result[0].content == "msg3"
    assert result[1].content == "msg4"
    assert result[2].content == "final"


def test_does_not_clip_when_within_limit() -> None:
    history = [_msg("You", "a"), _msg("Bot", "b")]
    result = build_llm_context(history, _msg("You", "c"), "Bot", "You", 10)

    assert len(result) == 3


def test_empty_history_returns_only_current() -> None:
    result = build_llm_context([], _msg("You", "hi"), "Bot", "You", 5)

    assert result == [Message(role="user", content="hi")]
