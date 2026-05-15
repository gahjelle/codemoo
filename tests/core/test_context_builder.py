"""Tests for build_context: mode handling, ToolUseContent unrolling, role mapping."""

import json

from codemoo.core.backend import Message
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    InjectedContent,
    ItemMode,
    SystemContent,
    ToolUseContent,
    UserMessageContent,
)


def _item(content: object, **kwargs: object) -> ContextItem:
    return ContextItem(content=content, **kwargs)


# ---------------------------------------------------------------------------
# Basic role mapping
# ---------------------------------------------------------------------------


def test_user_message_maps_to_user_role() -> None:
    ctx = [_item(UserMessageContent("hello"))]
    msgs = build_context(ctx)
    assert msgs == [Message(role="user", content="hello")]


def test_assistant_message_maps_to_assistant_role() -> None:
    ctx = [_item(AssistantMessageContent("reply"))]
    msgs = build_context(ctx)
    assert msgs == [Message(role="assistant", content="reply")]


def test_system_content_maps_to_system_role() -> None:
    ctx = [_item(SystemContent("you are a bot"))]
    msgs = build_context(ctx)
    assert msgs == [Message(role="system", content="you are a bot")]


def test_injected_content_uses_own_role() -> None:
    ctx = [_item(InjectedContent(label="f", text="file text", role="assistant"))]
    msgs = build_context(ctx)
    assert msgs == [Message(role="assistant", content="file text")]


def test_injected_content_defaults_to_user_role() -> None:
    ctx = [_item(InjectedContent(label="f", text="data"))]
    msgs = build_context(ctx)
    assert msgs[0].role == "user"


# ---------------------------------------------------------------------------
# DISABLED mode
# ---------------------------------------------------------------------------


def test_disabled_item_is_excluded() -> None:
    ctx = [
        _item(UserMessageContent("visible")),
        _item(UserMessageContent("hidden"), mode=ItemMode.DISABLED),
    ]
    msgs = build_context(ctx)
    assert len(msgs) == 1
    assert msgs[0].content == "visible"


def test_empty_context_returns_empty_list() -> None:
    assert build_context([]) == []


# ---------------------------------------------------------------------------
# EDITED mode
# ---------------------------------------------------------------------------


def test_edited_mode_uses_edited_field() -> None:
    ctx = [
        _item(
            AssistantMessageContent("original"),
            mode=ItemMode.EDITED,
            edited="rewritten",
        )
    ]
    msgs = build_context(ctx)
    assert msgs == [Message(role="assistant", content="rewritten")]


# ---------------------------------------------------------------------------
# SUMMARY mode
# ---------------------------------------------------------------------------


def test_summary_mode_uses_summary_field() -> None:
    ctx = [
        _item(
            AssistantMessageContent("long text"), mode=ItemMode.SUMMARY, summary="short"
        )
    ]
    msgs = build_context(ctx)
    assert msgs == [Message(role="assistant", content="short")]


# ---------------------------------------------------------------------------
# role_override
# ---------------------------------------------------------------------------


def test_role_override_replaces_natural_role() -> None:
    ctx = [_item(AssistantMessageContent("text"), role_override="user")]
    msgs = build_context(ctx)
    assert msgs[0].role == "user"


def test_role_override_ignored_for_tool_use_content() -> None:
    ctx = [_item(ToolUseContent("tool", "{}", "id1", "out"), role_override="user")]
    msgs = build_context(ctx)
    roles = [m.role for m in msgs]
    assert roles == ["assistant", "tool"]


# ---------------------------------------------------------------------------
# ToolUseContent unrolling
# ---------------------------------------------------------------------------


def test_tool_use_content_produces_two_messages() -> None:
    ctx = [
        _item(
            ToolUseContent(
                name="read_file",
                arguments_json='{"path":"a.py"}',
                call_id="c1",
                output="contents",
            )
        )
    ]
    msgs = build_context(ctx)
    assert len(msgs) == 2


def test_tool_use_assistant_message_has_tool_calls_json() -> None:
    ctx = [_item(ToolUseContent("read_file", '{"path":"a.py"}', "c1", "contents"))]
    msgs = build_context(ctx)
    assert msgs[0].role == "assistant"
    assert msgs[0].tool_calls_json is not None
    parsed = json.loads(msgs[0].tool_calls_json)
    assert parsed[0]["id"] == "c1"
    assert parsed[0]["function"]["name"] == "read_file"


def test_tool_use_result_message_has_call_id_and_output() -> None:
    ctx = [_item(ToolUseContent("read_file", "{}", "c1", "file contents"))]
    msgs = build_context(ctx)
    assert msgs[1].role == "tool"
    assert msgs[1].tool_call_id == "c1"
    assert msgs[1].content == "file contents"


def test_disabled_tool_use_produces_no_messages() -> None:
    ctx = [_item(ToolUseContent("tool", "{}", "c1", "out"), mode=ItemMode.DISABLED)]
    msgs = build_context(ctx)
    assert msgs == []


# ---------------------------------------------------------------------------
# Mixed context
# ---------------------------------------------------------------------------


def test_mixed_context_preserves_order() -> None:
    ctx = [
        _item(UserMessageContent("question")),
        _item(ToolUseContent("search", "{}", "c1", "results")),
        _item(AssistantMessageContent("answer")),
    ]
    msgs = build_context(ctx)
    assert len(msgs) == 4
    assert msgs[0].role == "user"
    assert msgs[1].role == "assistant"
    assert msgs[2].role == "tool"
    assert msgs[3].role == "assistant"
