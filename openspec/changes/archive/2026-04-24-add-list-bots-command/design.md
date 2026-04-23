## Context

The `codemoo` TUI CLI (`tui.py`) uses `cyclopts` for command dispatch. The existing `chat` (default), `select`, and `demo` subcommands all call `_setup()` which instantiates the full LLM backend and all bot objects. A lightweight `list-bots` command should enumerate bots without launching the TUI or connecting to the LLM backend.

The `make_bots` function in `core/bots/__init__.py` requires a backend and human name to construct bots. Bot metadata (name, emoji, type) is per-instance, not per-class, so we need to call `make_bots`.

`rich` is already available via the project's dependencies and used in `cli.py`.

## Goals / Non-Goals

**Goals:**
- Print all bots as a rich table (columns: #, Type, Bot = emoji + name) to stdout and exit
- Reuse the existing `make_bots` + `resolve_bot` machinery to stay consistent with `--bot` / `--start` resolution
- Keep the command dependency-free at runtime (no LLM calls, no TUI launch)

**Non-Goals:**
- Filtering or sorting bots
- Machine-readable output (JSON, CSV)
- Showing tool details or bot configuration

## Decisions

### Use a minimal backend stub for bot construction

`make_bots` requires a `ToolLLMBackend`. Rather than refactoring `make_bots` to accept `None`, we call `create_mistral_backend()` as `_setup()` already does — the backend is never used for any LLM call, only stored in bot instances.

*Alternative considered*: Restructure `make_bots` to lazily initialize bots, or add a metadata-only factory. Rejected — over-engineering for a display-only command that calls no LLM endpoints.

### Use `rich.table.Table` for output

Consistent with the existing use of `rich` in `cli.py`. A plain `print` loop was considered but offers no alignment or style benefits.

### Place the command in `tui.py`, not `cli.py`

`list-bots` pertains to the TUI bot roster, not the LLM/tool exploration commands in `cli.py`. It lives alongside the other TUI-mode subcommands.

## Risks / Trade-offs

- [Backend construction at import time] `create_mistral_backend()` may read env vars or config at call time. → The backend object is created but no network call is made until `.complete()` is invoked, so this is safe.
- [Bot list diverges from `_setup` output] If `make_bots` signature changes, `list_bots` must be updated too. → Mitigated by sharing the same `_setup`-style call pattern.
