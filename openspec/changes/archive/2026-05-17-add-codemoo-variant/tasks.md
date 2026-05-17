## 1. Refactor factory to handle `save_memory` as a special token

- [x] 1.1 In `src/codemoo/core/bots/__init__.py`, replace the single tools comprehension with a two-step process: extract `"save_memory"` from the names list, resolve remaining names through `_ALL_TOOLS`, then append the memory tool if `"save_memory"` was declared
- [x] 1.2 Remove the hardcoded `make_memory_tool` injection from the `MemoryBot` match arm (path building and `tools=[*tools, memory_tool]`)
- [x] 1.3 Remove the hardcoded `make_memory_tool` injection from the `RetryBot` match arm (same)
- [x] 1.4 Verify that the `memory_file` field on `ResolvedBotConfig` is still threaded correctly through to the path logic in the factory

## 2. Update existing variants in config

- [x] 2.1 Add `"save_memory"` to `tools` for `MemoryBot.variants.code` in `codemoo.toml`
- [x] 2.2 Add `"save_memory"` to `tools` for `MemoryBot.variants.m365` in `codemoo.toml`
- [x] 2.3 Add `"save_memory"` to `tools` for `MemoryBot.variants.workspace` in `codemoo.toml`
- [x] 2.4 Add `"save_memory"` to `tools` for `RetryBot.variants.code` in `codemoo.toml`
- [x] 2.5 Add `"save_memory"` to `tools` for `RetryBot.variants.m365` in `codemoo.toml`
- [x] 2.6 Add `"save_memory"` to `tools` for `RetryBot.variants.workspace` in `codemoo.toml`

## 3. Add the `codemoo` variant

- [x] 3.1 Create `src/codemoo/config/instructions/retry_bot-codemoo.txt` with the comprehensive system prompt
- [x] 3.2 Add `[bots.RetryBot.variants.codemoo]` to `codemoo.toml` with `instruction_file`, `context_source`, `memory_file`, `tools = ["@code_write", "save_memory"]`, `capabilities`, and `description`

## 4. Update TUI default

- [x] 4.1 Update `src/codemoo/frontends/tui.py` to use `("RetryBot", "codemoo")` as the default bot in `code_chat` and `business_chat`

## 5. Verify and document

- [x] 5.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 5.2 Run `uv run ty check src/ tests/`
- [x] 5.3 Run `uv run pytest` and confirm all tests pass
- [x] 5.4 Review `AGENTS.md` and update the Bot Configuration section if the new variant or the `save_memory` config pattern warrants documentation
