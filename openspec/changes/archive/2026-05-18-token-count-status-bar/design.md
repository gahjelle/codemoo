## Context

`ContextStatus` is a Textual widget mounted by `ChatApp` when the `context_management` capability is active. It currently receives only a message count (`len(_chat_context)`) via `update_message_count()` and renders it as plain text. Token count is the more useful signal — it's what actually approaches model limits — but computing it requires a tokenizer.

`ChatApp` already calls `build_context(_chat_context)` indirectly through bots; the result is a `list[Message]` that represents exactly what would be sent to the LLM. Token estimation operates on that same representation.

## Goals / Non-Goals

**Goals:**
- Estimate tokens from `list[Message]` without network calls.
- Display message count and estimated token count together in `ContextStatus`.
- Keep `estimate_tokens` reusable by CompactBot (the planned next change).

**Non-Goals:**
- Exact Claude-specific token counts (would require a paid API call per turn).
- Per-message or per-role breakdown in the UI.
- Any compaction behaviour.

## Decisions

### Use `cl100k_base` tiktoken encoder, not chars ÷ 4

`cl100k_base` is GPT-4's encoder and a close approximation for Claude (within ~5–10%). It runs locally after first download and is fast enough for per-message calls.

Alternatives considered:
- **`chars // 4`**: Zero dependencies, but visibly wrong for code-heavy or non-Latin content. We decided the inaccuracy isn't acceptable for a number users will anchor on.
- **Anthropic `count_tokens()` endpoint**: Exact, but requires a network round-trip on every turn — unacceptable latency in the TUI hot path.
- **`o200k_base`** (GPT-4o): Marginally newer but negligible difference for this use case.

### Single module-level encoder instance

`tiktoken.get_encoding()` triggers a local file read (~1 MB, cached after first download). Instantiating once at module import time pays this cost once per process.

### Token estimation runs in `ChatApp`, not inside `ContextStatus`

`ContextStatus` is a display widget; it should receive data, not compute it. `ChatApp` already owns `_chat_context` and calls `build_context` conceptually — it's the right place to call `estimate_tokens(build_context(self._chat_context))` and pass the result to the widget.

This also positions the function correctly for CompactBot: the app will call the same `estimate_tokens` to decide when to compact.

### Display format: `"12 messages · ~3.2k tokens"`

Compact, readable, and clearly approximate (the `~` prefix). Values ≥ 1000 tokens are formatted as `Xk` with one decimal place; values < 1000 are shown as integers.

## Risks / Trade-offs

- **tiktoken first run**: Downloads the encoder file (~1 MB) on first import. Subsequent runs use a local cache (`~/.tiktoken`). Risk is a one-time pause on first use. Mitigation: acceptable for a dev/demo tool; document in setup notes if it becomes a complaint.
- **Approximation drift**: If a model with a very different tokenizer is used, the estimate could be off by 15–20%. Mitigation: the `~` prefix sets expectations; this is "is the context large?" not "exactly how many tokens?".

## Open Questions

*(none — decisions above are final for this change)*
