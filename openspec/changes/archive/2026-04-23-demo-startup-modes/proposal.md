## Why

Codemoo is a live demo tool for walking through a progression of bots, but the current startup flow (SelectionApp → ChatApp) requires manual restart between each bot, breaking demo flow. Adding structured startup modes lets presenters drive the whole progression without leaving the app.

## What Changes

- Replace the flat `codemoo:main()` entry point with a `cyclopts` App in a new `codemoo.frontends.tui` module
- Move the `demoo` CLI from `codemoo.cli` to `codemoo.frontends.cli`, fixing an import-time backend side effect
- Add three startup modes to `codemoo`: default (last bot), `--bot <spec>` (named bot), `select` (interactive picker), and `demo` (progression loop)
- Extract the hardcoded bot list into a `make_bots(backend, human_name)` factory in `core.bots`
- Add a `demo_position` parameter to `ChatApp` that enables a `DemoHeader` widget and Ctrl-N key binding
- Add a new `DemoHeader` widget showing bot identity, position in progression, and keyboard hint
- Add a `resolve_bot(spec, bots)` helper supporting 1-based index, case-insensitive name, and case-insensitive type name

## Capabilities

### New Capabilities

- `frontend-tui`: The `codemoo` TUI command with default, `--bot`, `select`, and `demo` subcommand modes
- `demo-mode`: Demo progression loop with Ctrl-N bot-advancing and a header widget
- `bot-spec-resolver`: Shared helper resolving a bot by 1-based index, name, or type name

### Modified Capabilities

- `bot-selection-screen`: Moves from being the default startup flow to an explicit `codemoo select` subcommand

## Impact

- `pyproject.toml`: Both entry points updated to point at `codemoo.frontends.*:app`
- `codemoo/__init__.py`: `main()` removed; module stripped down
- `codemoo/cli.py`: Replaced by `codemoo/frontends/cli.py`
- `codemoo/chat/app.py`: New `demo_position` parameter, `on_key` handler
- `codemoo/core/bots/__init__.py`: New `make_bots()` factory
- New files: `codemoo/frontends/__init__.py`, `codemoo/frontends/tui.py`, `codemoo/frontends/cli.py`, `codemoo/chat/demo_header.py`
