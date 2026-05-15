"""Tests for ContextItem types, ItemMode, and pure list operations."""

import dataclasses

import pytest

from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    InjectedContent,
    ItemMode,
    SystemContent,
    ToolUseContent,
    UserMessageContent,
    add_item,
    inject_at,
    next_turn_id,
    replace_item,
    set_edited,
    set_mode,
    set_summary,
)

# ---------------------------------------------------------------------------
# ContextItem construction and defaults
# ---------------------------------------------------------------------------


def test_context_item_default_mode_is_original() -> None:
    item = ContextItem(content=UserMessageContent("hi"))
    assert item.mode == ItemMode.ORIGINAL


def test_context_item_id_is_unique() -> None:
    a = ContextItem(content=UserMessageContent("hi"))
    b = ContextItem(content=UserMessageContent("hi"))
    assert a.id != b.id


def test_context_item_default_turn_id_is_zero() -> None:
    item = ContextItem(content=UserMessageContent("hi"))
    assert item.turn_id == 0


def test_context_item_is_immutable() -> None:
    item = ContextItem(content=UserMessageContent("hi"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        item.mode = ItemMode.DISABLED


def test_all_content_types_are_frozen() -> None:
    for content in [
        UserMessageContent("x"),
        AssistantMessageContent("x"),
        ToolUseContent("tool", "{}", "id1", "out"),
        InjectedContent("label", "text"),
        SystemContent("sys"),
    ]:
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            content.text = "mutated"


def test_injected_content_default_role_is_user() -> None:
    item = InjectedContent(label="file", text="content")
    assert item.role == "user"


# ---------------------------------------------------------------------------
# next_turn_id
# ---------------------------------------------------------------------------


def test_next_turn_id_empty_context_returns_zero() -> None:
    assert next_turn_id([]) == 0


def test_next_turn_id_increments_max() -> None:
    ctx = [
        ContextItem(content=UserMessageContent("a"), turn_id=0),
        ContextItem(content=AssistantMessageContent("b"), turn_id=0),
        ContextItem(content=UserMessageContent("c"), turn_id=1),
    ]
    assert next_turn_id(ctx) == 2


# ---------------------------------------------------------------------------
# Pure list operations
# ---------------------------------------------------------------------------


def test_add_item_appends_without_mutating_original() -> None:
    ctx: list[ContextItem] = []
    item = ContextItem(content=UserMessageContent("hi"))
    new_ctx = add_item(ctx, item)
    assert new_ctx == [item]
    assert ctx == []


def test_replace_item_replaces_matching_id() -> None:
    item_a = ContextItem(content=UserMessageContent("a"))
    item_b = ContextItem(content=UserMessageContent("b"))
    ctx = [item_a, item_b]
    replacement = ContextItem(content=UserMessageContent("replaced"), id=item_a.id)
    new_ctx = replace_item(ctx, item_a.id, replacement)
    assert new_ctx[0] is replacement
    assert new_ctx[1] is item_b
    assert ctx[0] is item_a


def test_set_mode_changes_targeted_item() -> None:
    item = ContextItem(content=UserMessageContent("hi"))
    ctx = [item]
    new_ctx = set_mode(ctx, item.id, ItemMode.DISABLED)
    assert new_ctx[0].mode == ItemMode.DISABLED
    assert ctx[0].mode == ItemMode.ORIGINAL


def test_set_edited_sets_edited_field() -> None:
    item = ContextItem(content=AssistantMessageContent("original"))
    ctx = [item]
    new_ctx = set_edited(ctx, item.id, "edited text")
    assert new_ctx[0].edited == "edited text"
    assert ctx[0].edited is None


def test_set_summary_sets_summary_field() -> None:
    item = ContextItem(content=AssistantMessageContent("long reply"))
    ctx = [item]
    new_ctx = set_summary(ctx, item.id, "short")
    assert new_ctx[0].summary == "short"
    assert ctx[0].summary is None


def test_inject_at_inserts_at_correct_index() -> None:
    a = ContextItem(content=UserMessageContent("a"))
    b = ContextItem(content=UserMessageContent("b"))
    injected = ContextItem(content=InjectedContent("f", "file contents"))
    ctx = [a, b]
    new_ctx = inject_at(ctx, 1, injected)
    assert new_ctx == [a, injected, b]
    assert ctx == [a, b]
