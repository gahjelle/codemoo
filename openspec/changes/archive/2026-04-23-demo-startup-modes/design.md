## Context

`codemoo` is a live demo tool for walking through a bot progression (EchoBot → ShellBot). The current `main()` in `codemoo/__init__.py` runs `SelectionApp` then `ChatApp`. The presenter must quit and restart between bots. The `demoo` CLI lives in `codemoo/cli.py` alongside the TUI code, and creates its LLM backend at module level — a side effect that runs at import time.

## Goals / Non-Goals

**Goals:**
- Three new `codemoo` startup modes: bare (last bot), `--bot <spec>` (named bot), `demo` (progression loop)
- Preserve the interactive picker as `codemoo select`
- Ctrl-N advances to the next bot in demo mode without quitting
- A demo header widget shows bot identity and position in the progression
- Clear frontend separation: TUI and plain CLI are distinct cyclopts Apps
- Fix import-time backend instantiation in the CLI

**Non-Goals:**
- Changing how `ChatApp` handles messages or participants during a session
- Adding new bots (out of scope for this change)
- Persisting chat history across Ctrl-N transitions

## Decisions

### D1: Outer loop for Ctrl-N (Option B over Option A)

Demo progression runs an outer `while` loop in `frontends/tui.py`. Each bot gets its own `ChatApp` instance. Ctrl-N calls `self.exit("next")`; the loop checks the return value and creates the next app.

**Alternatives considered:**
- Option A: `ChatApp` grows mutation methods (`_set_bot()`, `_clear_chat()`). Rejected because it adds stateful mutation surface to a component that doesn't need it outside demo mode and makes the lifecycle harder to reason about.

**Why Option B:** Each `ChatApp` starts fresh — clean history, clean widget tree. The existing `SelectionApp` already uses `app.exit(value)` as a result-passing pattern, so this is idiomatic. Brief Textual re-init between bots is acceptable for a demo tool.

### D2: `codemoo.frontends` subpackage

Two entry point modules: `frontends/tui.py` (TUI, `codemoo` command) and `frontends/cli.py` (plain CLI, `demoo` command). Both expose a module-level `app = cyclopts.App()` that `pyproject.toml` wires to directly — no wrapper `main()` needed since cyclopts `App` is directly callable.

**Why:** Separates concerns at the module level rather than just at the function level. The TUI and CLI have different dependencies (Textual vs. Rich), different startup costs, and different audiences. Keeping them in separate modules prevents accidental coupling.

### D3: `make_bots(backend, human_name)` factory in `core.bots`

The ordered bot list moves from `__init__.py:main()` into `core/bots/__init__.py` as a factory function. Both `frontends/tui.py` commands that need bots call it.

**Why:** The bot list is domain knowledge (ordering, names, tools) that belongs in `core`, not in a frontend module. The factory also gives a single place to extend when new bots are added.

### D4: `demo_position: tuple[int, int] | None` on `ChatApp`

`ChatApp` gets one new optional parameter. When set, `compose()` prepends a `DemoHeader` widget and `on_key()` handles Ctrl-N. When `None` (default), behaviour is identical to today.

**Why:** Avoids a `DemoChatApp` subclass for a small feature. A single boolean-ish parameter keeps the class hierarchy flat. The parameter is typed and defaults to `None` so existing call sites are unaffected.

### D5: Case-insensitive matching for both name and type in `resolve_bot`

`resolve_bot(spec, bots)` tries: 1-based int, then `name.casefold()`, then `type.__name__.casefold()`. An unmatched spec raises a `cyclopts.ValidationError` listing valid options.

**Why:** Demo presenters should not need to recall exact casing. Consistent case-folding for both name and type avoids surprising asymmetry.

## Risks / Trade-offs

- **Brief blank screen on Ctrl-N**: Textual re-inits between bots (Option B). On a fast machine this is imperceptible; on a slow machine it may be a visible flash. → Mitigation: acceptable for a demo tool; can revisit with Option A if it becomes a problem.
- **Module-level `app = cyclopts.App()` runs at import**: The cyclopts App object is created when the frontend module is imported, but no backend is instantiated and no I/O happens. Commands instantiate the backend lazily. → No mitigation needed.
- **`demoo` entry point changes module path**: `codemoo.cli:main` → `codemoo.frontends.cli:app`. Anyone who hard-codes the old import path breaks. → Acceptable: this is an internal entry point, not a public API.

## Migration Plan

1. Add `codemoo/frontends/` package with `tui.py` and `cli.py`
2. Add `make_bots()` factory; update `core/bots/__init__.py`
3. Add `DemoHeader` widget and `demo_position` param to `ChatApp`
4. Update `pyproject.toml` entry points
5. Remove `codemoo/cli.py` and strip `codemoo/__init__.py`
6. Run `uv sync` to refresh the installed entry points

Rollback: revert the five files changed in steps 1–5 and re-run `uv sync`.
