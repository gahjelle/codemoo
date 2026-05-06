## 1. Config Loader

- [x] 1.1 Add `import re` to `src/codemoo/config/__init__.py`
- [x] 1.2 Define `_instructions_dir` and `_prompts_dir` module-level constants derived from `config_path.parent`
- [x] 1.3 Implement `_resolve_file_refs(data: dict) -> None`: walk `data["bots"]` → each bot's variants → resolve `instruction_file` (pop key, read UTF-8, set `instructions`) and `prompts_file` (pop key, read UTF-8, split on `---`, strip, discard empties, set `prompts`)
- [x] 1.4 Implement `_load_config(path: Path) -> Configuration`: extract `.data` from `Configuration.from_file(path)`, call `_resolve_file_refs`, return `Configuration.from_dict(data)`
- [x] 1.5 Replace `Configuration.from_file(config_path)` with `_load_config(config_path)` in the `config` chain

## 2. Instruction Files

- [x] 2.1 Create `src/codemoo/config/instructions/` directory
- [x] 2.2 Create `system_bot-default.txt` — Sona's full system prompt (currently in `[bots.SystemBot.variants.default]`)
- [x] 2.3 Create `tool_bot-default.txt` — Telo's instructions
- [x] 2.4 Create `read_bot-code.txt` — Rune's instructions
- [x] 2.5 Create `change_bot-code.txt` — Axel's instructions
- [x] 2.6 Create `agent_bot-code.txt`, `agent_bot-m365.txt`, `agent_bot-workspace.txt` — Loom's three variant instructions
- [x] 2.7 Create `guard_bot-code.txt`, `guard_bot-m365.txt`, `guard_bot-workspace.txt` — Cato's three variant instructions
- [x] 2.8 Create `scan_bot-m365.txt`, `scan_bot-workspace.txt` — Roam's two variant instructions
- [x] 2.9 Create `send_bot-m365.txt`, `send_bot-workspace.txt` — Aero's two variant instructions
- [x] 2.10 Create `project_bot-code.txt`, `project_bot-m365.txt`, `project_bot-workspace.txt` — Lore's three variant instructions

## 3. Example Prompt Files

- [x] 3.1 Create `src/codemoo/config/example_prompts/` directory
- [x] 3.2 Create `echo_bot-default.txt` — EchoBot prompts separated by `---`
- [x] 3.3 Create `llm_bot-default.txt` — LlmBot prompts
- [x] 3.4 Create `chat_bot-default.txt` — ChatBot prompts
- [x] 3.5 Create `system_bot-default.txt` — SystemBot prompts
- [x] 3.6 Create `tool_bot-default.txt` — ToolBot prompts
- [x] 3.7 Create `read_bot-code.txt` — ReadBot prompts
- [x] 3.8 Create `change_bot-code.txt` — ChangeBot prompts
- [x] 3.9 Create `agent_bot-code.txt`, `agent_bot-m365.txt`, `agent_bot-workspace.txt` — AgentBot prompts for each variant
- [x] 3.10 Create `guard_bot-code.txt`, `guard_bot-m365.txt`, `guard_bot-workspace.txt` — GuardBot prompts for each variant
- [x] 3.11 Create `scan_bot-m365.txt`, `scan_bot-workspace.txt` — ScanBot prompts
- [x] 3.12 Create `send_bot-m365.txt`, `send_bot-workspace.txt` — SendBot prompts
- [x] 3.13 Create `project_bot-code.txt`, `project_bot-m365.txt`, `project_bot-workspace.txt` — ProjectBot prompts

## 4. Update codemoo.toml

- [x] 4.1 Replace `instructions = """..."""` blocks with `instruction_file = "<bot>-<variant>.txt"` for all non-empty instruction variants (SystemBot, ToolBot, ReadBot, ChangeBot, AgentBot ×3, GuardBot ×3, ScanBot ×2, SendBot ×2, ProjectBot ×3)
- [x] 4.2 Replace all `prompts = [...]` lists with `prompts_file = "<bot>-<variant>.txt"` for all bot variants
- [x] 4.3 Verify `codemoo.toml` line count has dropped significantly (395 lines, down from 467; tool lists grew with new workspace tools)

## 5. Verification

- [x] 5.1 Run `uv run codemoo --help` to confirm config loads without error
- [x] 5.2 Run `uv run demoo llm "Hello"` to confirm a bot resolves correctly end-to-end
- [x] 5.3 Run `uv run pytest` — all tests pass
- [x] 5.4 Run `uv run ruff check src/ tests/` — no lint errors
- [x] 5.5 Run `uv run ruff format src/ tests/` — no formatting changes
- [x] 5.6 Run `uv run ty check src/ tests/` — no type errors

## 6. Documentation

- [x] 6.1 Read `AGENTS.md` and update the config section to document `instruction_file` / `prompts_file` and the `---` separator convention
- [x] 6.2 Read `README.md` and update if it references `codemoo.toml` structure in a way that needs updating
