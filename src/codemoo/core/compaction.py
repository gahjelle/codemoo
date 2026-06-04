"""Context compaction: summarise old context items when the token budget is exceeded."""

import dataclasses
from typing import TYPE_CHECKING

from codemoo.core.backend import LLMBackend, Message
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    ContextItem,
    InjectedContent,
    ItemMode,
)
from codemoo.core.token_counter import estimate_tokens

if TYPE_CHECKING:
    from codemoo.core.commentator import CommentatorBot

_RECENT_WINDOW_FRACTION = 0.3

_SUMMARISE_PROMPT = """\
Summarise the conversation history below. Preserve:
- Decisions made and their rationale
- Files created, read, or modified (include paths)
- Explicit user instructions or constraints
- Open questions or next steps

Omit tool call traces and raw command output — those can be re-derived if needed.
Be concise. The summary will be injected as context for the next LLM turn.

--- CONVERSATION HISTORY ---
{history}
--- END ---"""


async def _summarise(items: list[ContextItem], llm: LLMBackend) -> str:
    """Call the LLM to produce a focused summary of the given context items."""
    messages = build_context(items)
    history_lines: list[str] = []
    for msg in messages:
        role = msg.role.upper()
        history_lines.append(f"[{role}] {msg.content or ''}")
    history = "\n".join(history_lines)
    prompt = _SUMMARISE_PROMPT.format(history=history)
    summary_messages = [Message(role="user", content=prompt)]
    response = await llm.complete(summary_messages, [])
    return "(Summary unavailable)" if isinstance(response, list) else response


async def compact_context(
    context: list[ContextItem],
    llm: LLMBackend,
    threshold: int,
    commentator: "CommentatorBot | None" = None,
    bot_name: str = "",
) -> list[ContextItem]:
    """Summarise old context items when the token budget is exceeded.

    Returns context unchanged if below threshold. When at or above threshold,
    disables old non-pinned items and injects a single summary InjectedContent
    item before the recent window.
    """
    if estimate_tokens(build_context(context)) < threshold:
        return context

    recent_budget = int(threshold * _RECENT_WINDOW_FRACTION)
    recent_start = len(context)
    recent_tokens = 0
    for i in range(len(context) - 1, -1, -1):
        item_tokens = estimate_tokens(build_context([context[i]]))
        if recent_tokens + item_tokens <= recent_budget:
            recent_tokens += item_tokens
            recent_start = i
        else:
            break

    items_to_summarise = [item for item in context[:recent_start] if not item.pinned]
    summary_text = await _summarise(items_to_summarise, llm)

    new_context: list[ContextItem] = []
    for item in context[:recent_start]:
        if item.pinned:
            new_context.append(item)
        else:
            new_context.append(dataclasses.replace(item, mode=ItemMode.DISABLED))

    summary_turn = context[recent_start].turn_id if recent_start < len(context) else 0
    new_context.append(
        ContextItem(
            content=InjectedContent(
                label="Conversation summary",
                text=summary_text,
                role="user",
            ),
            turn_id=summary_turn,
            pinned=True,
        )
    )
    new_context.extend(context[recent_start:])

    if commentator is not None:
        from codemoo.core.commentator import ContextEvent  # noqa: PLC0415

        await commentator.comment(
            ContextEvent(
                kind="compact",
                bot_name=bot_name,
                items_affected=len(items_to_summarise),
                preview=summary_text[:300],
            )
        )

    return new_context
