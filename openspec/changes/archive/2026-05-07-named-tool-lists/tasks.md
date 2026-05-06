## 1. Config Loader

- [x] 1.1 In `_resolve_file_refs` (`src/codemoo/config/__init__.py`), pop `tool_lists` from `data` at the start of the function
- [x] 1.2 After the existing file-ref resolution loop, add expansion logic: iterate each variant's `tools` list and replace any `@name` entry with the contents of `tool_lists[name]`, raising `KeyError` with a clear message if the name is not found

## 2. TOML Config

- [x] 2.1 Add a `[tool_lists]` section to `codemoo.toml` defining: `code_read`, `code_write`, `m365_read`, `m365_write`, `workspace_read`, `workspace_write`
- [x] 2.2 Replace repeated inline tool lists in all bot variants with the appropriate `@`-reference (ReadBot, ChangeBot, AgentBot, GuardBot, ProjectBot for code; ScanBot, SendBot, AgentBot, GuardBot, ProjectBot for m365 and workspace)

## 3. Tests

- [x] 3.1 Add a unit test verifying that a `@name` reference expands correctly after `_resolve_file_refs`
- [x] 3.2 Add a unit test verifying that a `@name` reference mixed with plain tool names expands correctly in-place
- [x] 3.3 Add a unit test verifying that an unknown `@name` reference raises `KeyError` with a message containing the reference name and available list names

## 4. Verification

- [x] 4.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 4.2 Run `uv run ty check src/ tests/`
- [x] 4.3 Run `uv run pytest`
- [x] 4.4 Run `uv run codemoo show-config bots.ProjectBot.variants` and confirm that each variant's `tools` list shows the fully expanded tool names (no `@`-prefixed entries remain)

## 5. Documentation

- [x] 5.1 Review `AGENTS.md` "Bot Configuration" section and add a note about `[tool_lists]` and `@name` syntax
- [x] 5.2 Review `PLANS.md` and `BOTS.md` for any related items to close or update
