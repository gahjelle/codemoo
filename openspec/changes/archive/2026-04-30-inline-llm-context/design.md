## Context

Context for LLM bots is currently built by `build_llm_context` in `core/backend.py`. All context-using bots import it and pass five or six arguments. For demo purposes, this hides the conceptual difference between `LlmBot` (single message) and `ChatBot` (history + message): the viewer sees a helper function call rather than the list construction directly.

The change inlines context construction into each bot. No new behaviour is introduced; `build_llm_context` is deleted.

## Goals / Non-Goals

**Goals:**
- Make the `LlmBot` → `ChatBot` progression visible in source without unfolding a helper
- Remove `human_name` and `max_messages` as fields bots must carry
- Delete `build_llm_context` from the public surface of `core/backend.py`

**Non-Goals:**
- Context window management (clipping, summarisation) — future work
- Filtering history by sender — removed without replacement for now

## Decisions

### Inline pattern: list unpacking, not append

Use `[*[...comprehension...], Message(role="user", content=message.text)]` rather than building a list and calling `.append()`. This keeps construction as a single expression and avoids mutation.

_Alternative_: append-after-construction. Rejected because the mutation step after the list literal is visually disconnected from the construction.

### Drop `human_name` filtering entirely

Rather than mapping `human_name` to a role and everything else to "user", map `self.name → "assistant"` and all other senders → `"user"`. Third-party messages are included rather than filtered.

_Alternative_: retain filtering but inline it. Rejected: filtering is context-management logic that should be introduced deliberately when needed, not carried silently.

### Drop `max_messages` clipping

Remove with no replacement. A demo conversation will never approach any model's context window. Clipping belongs in a future context-management layer, not in the base bot.

_Alternative_: keep clipping inline. Rejected: it adds noise to the bot bodies without serving the demo, and the current default (20) is arbitrary.

### `build_llm_context` deleted, not deprecated

No callers remain after the change. Leaving it would imply it is still the preferred API. Delete it and the associated tests.

## Risks / Trade-offs

- **Third-party messages now reach the LLM as "user" turns** → In multi-bot scenarios other bots' output is included with "user" role. Acceptable for current demos (always single-bot). If multi-bot context accuracy matters in future, reintroduce filtering explicitly.
- **No context-length guard** → A very long session could eventually hit a model's token limit, surfacing as a 400 error. Acceptable for demo use; document that clipping is deferred.
- **Behaviour change in existing tests** → Tests asserting third-party message exclusion and clipping must be updated to reflect new behaviour. No functional regression in production paths.

## Migration Plan

1. Inline construction in all five bots, drop `human_name`/`max_messages` fields
2. Remove `human_name` from `_make_bot`/`make_bots` and their callers
3. Delete `build_llm_context` from `backend.py`
4. Delete `tests/core/test_backend.py`
5. Update bot tests: remove filtering/clipping assertions, remove `human_name` from constructors
6. Run `uv run pytest` and `uv run ruff check .`
