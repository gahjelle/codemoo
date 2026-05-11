## 1. Rename existing memory files

- [x] 1.1 Rename `.codemoo/memory.md` → `.codemoo/memory-code.md` in the repo root
- [x] 1.2 Rename `demo/.codemoo/memory.md` → `demo/.codemoo/memory-code.md`

## 2. Update configuration

- [x] 2.1 Update `.gitignore`: change `.codemoo/memory.md` to `.codemoo/memory-code.md`
- [x] 2.2 Update `src/codemoo/config/codemoo.toml` `code` variant: `memory_file = "{project_settings_path}/memory-code.md"`
- [x] 2.3 Update `src/codemoo/config/codemoo.toml` `m365` variant: `memory_file = "{user_settings_path}/memory-m365.md"`
- [x] 2.4 Update `src/codemoo/config/codemoo.toml` `workspace` variant: `memory_file = "{user_settings_path}/memory-workspace.md"`

## 3. Verification

- [x] 3.1 Run `uv run ruff format src/ tests/`
- [x] 3.2 Run `uv run ruff check src/ tests/`
- [x] 3.3 Run `uv run ty check src/ tests/`
- [x] 3.4 Run `uv run pytest`

## 4. Documentation review

- [x] 4.1 Read `AGENTS.md` and update the memory-bot variant table if it references `memory.md`
- [x] 4.2 Read `BOTS.md` and update any references to the memory file path
- [x] 4.3 Read `PLANS.md` and update if relevant
- [x] 4.4 Read `README.md` and update if relevant
