## Why

The bots from Telo onwards have minimal, inconsistent system prompts — no shared structure, no personality, and scattered inconsistencies ("helpful coding assistant" vs "coding assistant", Lore calling itself a "business assistant"). Adding subtle per-bot credos and a consistent prompt form makes the demo richer without making persona the point (that role belongs to Sona).

## What Changes

- Each bot from Telo onwards gains a **credo** — a short phrase at the end of its system prompt expressing its operating principle. Identical wording across all variants of a bot; domain vocabulary (email/Gmail, SharePoint/Drive) adapts per variant.
- All 17 instruction files are rewritten to a consistent four-part form: identity → capability → behavior trigger → credo.
- Role naming is standardised: `coding assistant` for code variants, `productivity assistant` for platform variants. No adjective prefix. Sona's "ruthlessly practical" is the explicit exception.
- `reverse_string` is removed from all named tool lists in `codemoo.toml`. It remains assigned directly to Telo's variant, where it is the point. All other bots lose the toy tool silently.
- `AGENTS.md` gains a "Bot System Prompt Style" subsection documenting the form, role naming rules, credo concept, the full credo reference table, and the `reverse_string` convention. The stale `code_write` example in the existing tool_lists description is updated.
- `BOTS.md` gains a Bot Character Reference table listing every bot's credo. Credos for implemented bots are final. Credos for planned-but-unimplemented bots are provisional and marked for revisiting when those bots are built.

## Capabilities

### New Capabilities

- `bot-system-prompt-style`: The conventions governing how bot system prompts are written — four-part form, role naming, credo structure, and the `reverse_string` rule. Captured in AGENTS.md as guidance for future bot authoring.

### Modified Capabilities

- `tool-bot`: Telo's system prompt updated with consistent form and credo.
- `read-bot`: Rune's system prompt updated; `reverse_string` removed from `code_read` tool list.
- `named-tool-lists`: `reverse_string` removed from all named lists (`code_read`, `code_write`, `m365_read`, `m365_write`, `workspace_read`, `workspace_write`).

## Non-goals

- No new bot types or variants are introduced.
- Sona's system prompt is not touched — her extreme persona is intentional.
- EchoBot, LlmBot, and ChatBot have no system prompts and are not affected.
- No changes to bot behavior, tool implementations, or the TUI.

## Impact

- `src/codemoo/config/codemoo.toml` — named tool list changes
- `src/codemoo/config/instructions/*.txt` — all 17 instruction files rewritten
- `AGENTS.md` — new subsection added, stale example updated
- `BOTS.md` — Bot Character Reference table added with credos for all bots (implemented and provisional)
