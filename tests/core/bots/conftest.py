"""Shared test helpers for bot tests."""

from codemoo.core.context_items import ContextItem, UserMessageContent


def user_ctx(text: str) -> list[ContextItem]:
    """Return a single-item context satisfying the on_message precondition."""
    return [ContextItem(content=UserMessageContent(text), turn_id=0)]
