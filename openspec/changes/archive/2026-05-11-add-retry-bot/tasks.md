## 1. Commentator infrastructure (ToolErrorEvent)

- [x] 1.1 Add `ToolErrorEvent` frozen dataclass to `commentator_bot.py` with fields `bot_name`, `tool_name`, `arguments`, `result`
- [x] 1.2 Add `ToolErrorEvent` to the union type in `CommentatorBot.comment()` and add `_comment_on_tool_error` handler
- [x] 1.3 Implement `_comment_on_tool_error`: dim prefix showing tool signature + truncated error, LLM persona prompt reacting to the failure, Streik fallback
- [x] 1.4 Emit `ToolErrorEvent` from `dispatch_tool` in `core/tools/__init__.py` when `result.startswith("Error ")`

## 2. RetryBot implementation

- [x] 2.1 Create `src/codemoo/core/bots/retry_bot.py` as a standalone dataclass copying MemoryBot's full structure
- [x] 2.2 Add per-turn retry counter `dict[tuple[str, str], int]` reset at the top of `on_message`; key is `(tool_name, json.dumps(args, sort_keys=True))`
- [x] 2.3 Add partial-progress log `list[str]` tracking successful tool call summaries within the turn
- [x] 2.4 Increment counter and log successful calls around each `dispatch_tool` call; check budget (3) before each dispatch — escalate if reached
- [x] 2.5 Implement escalation: return `ChatMessage` summarising the failing tool, error, and partial progress
- [x] 2.6 Re-request approval via `_ask_fn` for any `requires_approval` tool being retried after failure

## 3. Register RetryBot

- [x] 3.1 Import `RetryBot` in `src/codemoo/core/bots/__init__.py`, add to `__all__`, add `"RetryBot"` case to `_make_bot`
- [x] 3.2 Add `BotType` literal `"RetryBot"` to the config schema (wherever `BotType` is defined)

## 4. Config and scripts

- [x] 4.1 Add `[bots.RetryBot]` block to `codemoo.toml` with `name = "Undo"`, `emoji = "BOOMERANG"`, `sources = ["retry_bot.py"]`
- [x] 4.2 Add `[bots.RetryBot.variants.code]` with `instruction_file`, `context_source`, `memory_file`, `tools = ["@code_write"]`, `prompts_file`
- [x] 4.3 Add `[bots.RetryBot.variants.m365]` with `instruction_file`, `context_source`, `memory_file`, `tools = ["@m365_read", "@m365_write"]`, `prompts_file`
- [x] 4.4 Add `[bots.RetryBot.variants.workspace]` with `instruction_file`, `context_source`, `memory_file`, `tools = ["@workspace_read", "@workspace_write"]`, `prompts_file`
- [x] 4.5 Append `{ type = "RetryBot", variant = "code" }` after MemoryBot in `[scripts.default]`
- [x] 4.6 Append `{ type = "RetryBot", variant = "m365" }` after MemoryBot in `[scripts.m365]`
- [x] 4.7 Append `{ type = "RetryBot", variant = "workspace" }` after MemoryBot in `[scripts.workspace]`

## 5. Instruction and prompt files

- [x] 5.1 Write `src/codemoo/config/instructions/retry_bot-code.txt` (four-part structure: identity, capability, behaviour, credo "Failure is data — use it.")
- [x] 5.2 Write `src/codemoo/config/instructions/retry_bot-m365.txt` (same structure, productivity assistant, M365 domain vocabulary)
- [x] 5.3 Write `src/codemoo/config/instructions/retry_bot-workspace.txt` (same structure, productivity assistant, Workspace domain vocabulary)
- [x] 5.4 Write `src/codemoo/config/example_prompts/retry_bot-code.txt` (3 prompts: numpy check; run whoami.py; fix typo and run again)
- [x] 5.5 Write `src/codemoo/config/example_prompts/retry_bot-m365.txt` (2–3 prompts: read missing Q3 Board Report email; read missing Strategy2030.docx from SharePoint)
- [x] 5.6 Write `src/codemoo/config/example_prompts/retry_bot-workspace.txt` (2–3 prompts: find missing Q3 Board Report email in Gmail; read missing Strategy2030.docx from Drive)

## 6. Default bot

- [x] 6.1 Change `bot: BotType = "MemoryBot"` to `bot: BotType = "RetryBot"` in `code_chat` in `tui.py`
- [x] 6.2 Change `bot: BotType = "MemoryBot"` to `bot: BotType = "RetryBot"` in `business_chat` in `tui.py`

## 7. Demo game

- [x] 7.1 Write `demo/whoami.py` with: hardcoded famous-people list (≥15), date-seeded random selection, `os.environ["MISTAKE_API_KEY"]` (deliberate typo), OpenAI client pointed at Mistral, no `input()` loop
- [x] 7.2 Implement three CLI modes: no-arg intro; one-arg question passed to LLM; one-arg code-side reveal when any word ≥4 chars from `sys.argv[1]` appears in the person's name (case-insensitive)
- [x] 7.3 Add soft LLM trigger to system prompt: instruct the persona to confirm enthusiastically if the user's guess is very close to the name, including minor spelling errors or first/last name only

## 8. Documentation

- [x] 8.1 Add "Adding a New Bot" subsection to `AGENTS.md` (emoji rules, additive-only, no inheritance, default bot update, example prompt principles)
- [x] 8.2 Add `| Undo (RetryBot) | Failure is data — use it. |` to the credo table in `AGENTS.md`
- [x] 8.3 Add `demo/whoami.py` deliberate-bug note to `AGENTS.md` alongside the greeter.py note
- [x] 8.4 Update `BOTS.md`: fill in `🪃` / `BOOMERANG` in the emoji table; move RetryBot to "Implemented (final)" credo section
- [x] 8.5 Review `PLANS.md` and update if RetryBot affects any planned items

## 9. Verification

- [x] 9.1 `uv run ruff format src/ tests/`
- [x] 9.2 `uv run ruff check src/ tests/`
- [x] 9.3 `uv run ty check src/ tests/`
- [x] 9.4 `uv run pytest`
- [x] 9.5 Run `uv run codemoo` and confirm RetryBot (Undo 🪃) starts as the default bot
- [ ] ~~9.6 Run the first preset prompt (numpy check) and confirm 3 retries then escalation~~
- [x] 9.7 Run the second preset prompt (whoami) and confirm 3 retries then escalation with MISTAKE_API_KEY diagnosis
- [x] 9.8 Run the third preset prompt (fix and run) and confirm whoami.py is patched and the mystery guest introduces themselves
