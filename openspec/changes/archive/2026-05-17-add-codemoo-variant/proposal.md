## Why

The demo-oriented `code` variant of RetryBot keeps its system prompt minimal by design, which means it never fully communicates its capabilities (memory, approval gates, project context, retry behavior) to the LLM. For real coding work this makes the bot underperform. A production-quality variant is needed that's comprehensive in its instructions but sharp in its output.

A separate issue: `save_memory` is silently injected by the bot factory for MemoryBot and RetryBot regardless of what the config declares — making it invisible in configuration and tightly coupled to bot type rather than bot capability.

## What Changes

- **New `RetryBot.codemoo` variant**: a production-quality coding assistant with a comprehensive system prompt covering all capabilities — tools available, planning approach, approval-gate behavior, retry policy, memory usage, project context, and output style. Same tools as the `code` variant.
- **`save_memory` as an explicit config-level tool**: variants declare `"save_memory"` in their `tools` list like any other tool. The factory detects it, builds the path-parameterized tool, and injects it. The hardcoded factory injection is removed.
- **Update all MemoryBot and RetryBot variants** (6 total) to explicitly list `"save_memory"` in their tools config.
- **Update TUI default** to use the `codemoo` variant.

## Non-goals

- No new bot type or class — `codemoo` is a variant of the existing `RetryBot`.
- No changes to the behavior or capabilities of existing demo variants; only their config becomes explicit.
- No changes to how `save_memory` functions at runtime (the tool itself is unchanged).

## Capabilities

### New Capabilities

- `codemoo-variant`: A production-quality RetryBot variant with a comprehensive system prompt, named `codemoo`, suitable as the default coding assistant for real work.

### Modified Capabilities

- `bot-tool-registry`: The factory must recognise `"save_memory"` as a special declarable tool name, build it from the variant's `memory_file` path, and inject it — replacing the hardcoded MemoryBot/RetryBot injection logic.
- `bot-variant-config`: Variants can now declare `"save_memory"` in their `tools` list. This needs to be handled without a registry lookup (since `save_memory` is not in `TOOL_REGISTRY`).

## Impact

- `src/codemoo/config/codemoo.toml` — 6 variant edits + 1 new variant
- `src/codemoo/core/bots/__init__.py` — factory refactor
- `src/codemoo/config/instructions/retry_bot-codemoo.txt` — new file
- `src/codemoo/frontends/tui.py` — default bot update
