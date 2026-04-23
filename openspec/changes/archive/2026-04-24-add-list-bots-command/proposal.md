## Why

Users need a quick way to discover available bots and their identifiers before invoking `codemoo` with `--bot` or `codemoo demo --start`. Currently there is no command to list bots without launching the full TUI.

## What Changes

- Add a `list-bots` subcommand to the `codemoo` TUI CLI (`tui.py`) that prints all available bots as a rich table to stdout and exits.
- The table includes three columns: **#** (1-based index), **Type** (class name), and **Bot** (emoji + name).
- The command requires no arguments and accepts no options.

## Capabilities

### New Capabilities

- `list-bots-command`: A CLI subcommand that enumerates available bots in a rich table. The number, type, and formatted name shown in the table are all valid values for `--bot` (chat) and `--start` (demo) arguments.

### Modified Capabilities

- `frontend-tui`: A new `list-bots` subcommand is added to the CLI surface.

## Impact

- `src/codemoo/frontends/tui.py` — add `list_bots` command function
- No new dependencies; `rich` is already used in `cli.py` and available in the environment
- No breaking changes to existing commands
