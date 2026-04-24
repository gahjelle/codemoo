## Why

During live demos, having to type example prompts from scratch wastes time and breaks flow. Pre-set prompts per bot, inserted with a single keystroke, let the presenter focus on explaining rather than typing.

## What Changes

- `BotConfig` gains an optional `prompts` list field (TOML: `prompts = ["...", "..."]`)
- A new `Ctrl+Space` key binding in demo-mode `ChatApp` inserts the next preset prompt into the input field (insert-and-edit, not auto-send)
- `DemoContext` gains a `prompts` field carrying the current bot's prompts
- `DemoHeader` becomes reactive, showing remaining prompt count and the `Ctrl+Space` hint; when prompts are exhausted, `Ctrl+Space` does nothing and the header indicates this
- If `config.language` is not English, prompts are translated eagerly during the slide screen (while the LLM explanation is being generated), mutating `DemoContext.prompts` in place

## Non-goals

- No auto-send — the presenter always reviews and can edit before hitting Enter
- No prompt cycling or wrapping — once all prompts are used, the feature is done for that session
- No prompt support outside demo mode — `Ctrl+Space` and the prompt count display are demo-only
- No per-prompt language override — translation applies to all prompts at once

## Capabilities

### New Capabilities

- `demo-preset-prompts`: Pre-configured prompt list per bot, Ctrl+Space insertion, prompt count display in DemoHeader, and optional eager LLM translation during the slide screen

### Modified Capabilities

- `demo-mode`: DemoHeader gains reactive prompt-count state and the Ctrl+Space hint; `ChatApp.on_key` handles the new binding
- `toml-bot-registry`: `BotConfig` gains an optional `prompts: list[str]` field

## Impact

- `src/codemoo/config/schema.py` — `BotConfig` gains `prompts: list[str] = []`
- `configs/codemoo.toml` — example `prompts` arrays added to each bot entry
- `src/codemoo/chat/slides.py` — `DemoContext` gains `prompts` field; `SlideScreen` gains translation worker
- `src/codemoo/chat/demo_header.py` — stores bot/position/prompt-count data, overrides `render()`, adds `update_prompt_state(remaining)`
- `src/codemoo/chat/app.py` — `_prompt_index`, `Ctrl+Space` handler, `_insert_next_prompt()` method
- `src/codemoo/frontends/tui.py` — extracts prompts from config and passes to `DemoContext`
- Tests updated or added for all touched modules
