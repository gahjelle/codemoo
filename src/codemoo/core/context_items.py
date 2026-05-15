"""ContextItem model: intermediate layer between chat log and LLM wire format."""

import dataclasses
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

type Role = Literal["user", "assistant", "system", "tool"]


class ItemMode(Enum):
    """Controls which content layer is active for a ContextItem."""

    ORIGINAL = "original"
    EDITED = "edited"
    SUMMARY = "summary"
    DISABLED = "disabled"


@dataclass(frozen=True)
class UserMessageContent:
    """Text sent by the human participant."""

    text: str


@dataclass(frozen=True)
class AssistantMessageContent:
    """Final text reply produced by a bot."""

    text: str


@dataclass(frozen=True)
class ToolUseContent:
    """Atomic pair of a tool call and its result."""

    name: str
    arguments_json: str
    call_id: str
    output: str


@dataclass(frozen=True)
class InjectedContent:
    """Manually added content with an explicit role."""

    label: str
    text: str
    role: Role = "user"


@dataclass(frozen=True)
class SystemContent:
    """System prompt text."""

    text: str


type ContextContent = (
    UserMessageContent
    | AssistantMessageContent
    | ToolUseContent
    | InjectedContent
    | SystemContent
)


@dataclass(frozen=True)
class ContextItem:
    """Immutable record of one item in the shapeable context layer.

    mode selects which content layer the context builder uses:
      ORIGINAL  → content's natural text
      EDITED    → edited field (content preserved as record)
      SUMMARY   → summary field (applies to whichever layer is active below it)
      DISABLED  → item is excluded from LLM context entirely

    Invariants: mode==EDITED requires edited is not None;
                mode==SUMMARY requires summary is not None.
    """

    content: ContextContent
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_id: int = 0
    mode: ItemMode = ItemMode.ORIGINAL
    edited: str | None = None
    summary: str | None = None
    role_override: Role | None = None
    pinned: bool = False


# ---------------------------------------------------------------------------
# Pure operations on list[ContextItem]
# ---------------------------------------------------------------------------


def next_turn_id(context: list[ContextItem]) -> int:
    """Return the next turn_id: max existing + 1, or 0 for an empty context."""
    if not context:
        return 0
    return max(item.turn_id for item in context) + 1


def add_item(context: list[ContextItem], item: ContextItem) -> list[ContextItem]:
    """Return a new list with item appended."""
    return [*context, item]


def replace_item(
    context: list[ContextItem], item_id: str, new_item: ContextItem
) -> list[ContextItem]:
    """Return a new list with the item matching item_id replaced by new_item."""
    return [new_item if it.id == item_id else it for it in context]


def set_mode(
    context: list[ContextItem], item_id: str, mode: ItemMode
) -> list[ContextItem]:
    """Return a new list with the targeted item's mode changed."""
    item = next(it for it in context if it.id == item_id)
    return replace_item(context, item_id, dataclasses.replace(item, mode=mode))


def set_edited(
    context: list[ContextItem], item_id: str, text: str
) -> list[ContextItem]:
    """Return a new list with the targeted item's edited field set."""
    item = next(it for it in context if it.id == item_id)
    return replace_item(context, item_id, dataclasses.replace(item, edited=text))


def set_summary(
    context: list[ContextItem], item_id: str, text: str
) -> list[ContextItem]:
    """Return a new list with the targeted item's summary field set."""
    item = next(it for it in context if it.id == item_id)
    return replace_item(context, item_id, dataclasses.replace(item, summary=text))


def inject_at(
    context: list[ContextItem], index: int, item: ContextItem
) -> list[ContextItem]:
    """Return a new list with item inserted at the given index."""
    return [*context[:index], item, *context[index:]]
