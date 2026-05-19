"""Tests for CompactBot — compact() logic, startup state reset, and registry."""

import dataclasses
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from codemoo.core.backend import Message
from codemoo.core.bots.commentator_bot import ContextEvent
from codemoo.core.bots.compact_bot import CompactBot
from codemoo.core.context_items import (
    ContextItem,
    InjectedContent,
    ItemMode,
    UserMessageContent,
)
from codemoo.core.tools import ToolDef

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class _FakeLLM:
    responses: list[str | object]

    async def complete(
        self, messages: list[Message], tools: list[ToolDef] | None = None
    ) -> str | object:
        return self.responses.pop(0)


def _make_bot(threshold: int, llm_responses: list[str]) -> CompactBot:
    return CompactBot(
        name="Drop",
        emoji="\N{BROOM}",
        llm=_FakeLLM(llm_responses),  # type: ignore[arg-type]
        tools=[],
        instructions="You are Drop.",
        context_source=None,
        memory_file=None,
        session_folder=Path(),
        compact_threshold=threshold,
    )


def _ctx(texts: list[str], pinned: list[bool] | None = None) -> list[ContextItem]:
    """Build a list of UserMessageContent context items."""
    pin_flags = pinned or [False] * len(texts)
    return [
        ContextItem(content=UserMessageContent(t), turn_id=i, pinned=p)
        for i, (t, p) in enumerate(zip(texts, pin_flags, strict=False))
    ]


# ---------------------------------------------------------------------------
# compact() — below threshold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_compact_returns_unchanged_below_threshold() -> None:
    bot = _make_bot(threshold=100_000, llm_responses=[])
    ctx = _ctx(["hello", "world"])

    result = await bot.compact(ctx)

    assert result is ctx


@pytest.mark.asyncio
async def test_compact_returns_same_object_when_empty_context() -> None:
    bot = _make_bot(threshold=1, llm_responses=[])
    result = await bot.compact([])
    assert result == []


# ---------------------------------------------------------------------------
# compact() — at or above threshold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_compact_disables_old_items_and_injects_summary() -> None:
    # Use a very low threshold so short messages trigger compaction.
    # "word " * 20 = 20 words ≈ 20 tokens per item; 3 items ≈ 60 tokens > threshold 5.
    long_text = "word " * 20
    ctx = _ctx([long_text, long_text, long_text])
    bot = _make_bot(threshold=5, llm_responses=["Summary of old turns."])

    result = await bot.compact(ctx)

    disabled = [i for i in result if i.mode == ItemMode.DISABLED]
    summaries = [i for i in result if isinstance(i.content, InjectedContent)]

    assert len(disabled) >= 1, "At least one item should be disabled"
    assert len(summaries) == 1
    summary_content = summaries[0].content
    assert isinstance(summary_content, InjectedContent)
    assert summary_content.text == "Summary of old turns."
    assert summary_content.label == "Conversation summary"
    assert summary_content.role == "user"


@pytest.mark.asyncio
async def test_compact_summary_appears_before_recent_window() -> None:
    # Use threshold=80 with 5 items of ~20 tokens each (~100 total).
    # recent_budget = 24 tokens → the last item (20 tokens) fits in the recent window.
    long_text = "word " * 20
    ctx = _ctx([long_text, long_text, long_text, long_text, long_text])
    bot = _make_bot(threshold=80, llm_responses=["Summary."])

    result = await bot.compact(ctx)

    summary_idx = next(
        i for i, item in enumerate(result) if isinstance(item.content, InjectedContent)
    )
    recent_idx = next(
        i
        for i, item in enumerate(result)
        if item.mode == ItemMode.ORIGINAL
        and isinstance(item.content, UserMessageContent)
    )
    assert summary_idx < recent_idx, "Summary must appear before the recent window"


@pytest.mark.asyncio
async def test_compact_sets_compacted_flag() -> None:
    long_text = "word " * 20
    bot = _make_bot(threshold=5, llm_responses=["Summary."])

    assert bot._compacted is False
    await bot.compact(_ctx([long_text, long_text, long_text]))
    assert bot._compacted is True


# ---------------------------------------------------------------------------
# compact() — pinned items are never disabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pinned_items_are_never_disabled() -> None:
    long_text = "word " * 20
    # First item is pinned, the others are not.
    ctx = _ctx([long_text, long_text, long_text], pinned=[True, False, False])
    bot = _make_bot(threshold=5, llm_responses=["Summary."])

    result = await bot.compact(ctx)

    pinned_in_result = [
        i for i in result if i.pinned and not isinstance(i.content, InjectedContent)
    ]
    for item in pinned_in_result:
        assert item.mode != ItemMode.DISABLED, "Pinned items must never be DISABLED"


# ---------------------------------------------------------------------------
# startup() resets compaction state
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_startup_resets_compacted_flag() -> None:
    long_text = "word " * 20
    bot = _make_bot(threshold=5, llm_responses=["Summary.", "Ignored."])

    await bot.compact(_ctx([long_text, long_text, long_text]))
    assert bot._compacted is True

    await bot.startup()
    assert bot._compacted is False


# ---------------------------------------------------------------------------
# compact() — ContextEvent emission
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_compact_emits_context_event_when_commentator_set() -> None:
    long_text = "word " * 20
    ctx = _ctx([long_text, long_text, long_text])
    bot = _make_bot(threshold=5, llm_responses=["The summary text."])

    received_events: list[object] = []
    mock_commentator = AsyncMock()
    mock_commentator.comment = AsyncMock(side_effect=received_events.append)
    bot.commentator = mock_commentator

    await bot.compact(ctx)

    assert len(received_events) == 1
    event = received_events[0]
    assert isinstance(event, ContextEvent)
    assert event.kind == "compact"
    assert event.bot_name == "Drop"
    assert event.items_affected >= 1
    assert event.preview == "The summary text."[:300]


@pytest.mark.asyncio
async def test_compact_emits_no_event_when_commentator_is_none() -> None:
    long_text = "word " * 20
    ctx = _ctx([long_text, long_text, long_text])
    bot = _make_bot(threshold=5, llm_responses=["Summary."])

    assert bot.commentator is None
    result = await bot.compact(ctx)

    disabled = [i for i in result if i.mode == ItemMode.DISABLED]
    assert len(disabled) >= 1


@pytest.mark.asyncio
async def test_compact_emits_no_event_below_threshold() -> None:
    ctx = _ctx(["short"])
    bot = _make_bot(threshold=100_000, llm_responses=[])

    received_events: list[object] = []
    mock_commentator = AsyncMock()
    mock_commentator.comment = AsyncMock(side_effect=received_events.append)
    bot.commentator = mock_commentator

    await bot.compact(ctx)

    assert len(received_events) == 0
