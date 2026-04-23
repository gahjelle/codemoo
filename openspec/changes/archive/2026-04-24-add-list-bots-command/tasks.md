## 1. Implement list-bots command

- [x] 1.1 Add `list_bots` function to `src/codemoo/frontends/tui.py` decorated with `@app.command`, using `rich.table.Table` to print a three-column table (`#`, `Type`, `Bot`) for each bot returned by `make_bots`

## 2. Validation

- [x] 2.1 Run `codemoo list-bots` and confirm it exits cleanly with a table showing all bots
- [x] 2.2 Check table columns match the spec: `#` (1-based index), `Type` (class name), `Bot` (emoji + name)
- [x] 2.3 Run `codemoo --help` and confirm `list-bots` appears in the subcommand list
- [x] 2.4 Pick the `#`, type name, and bot name from the table output; confirm each is accepted by `codemoo --bot <value>` and `codemoo demo --start <value>` without error
- [x] 2.5 Run `uv run ruff check src/codemoo/frontends/tui.py` and `uv run ty check` — no new errors
