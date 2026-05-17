# Spec: codemoo-variant

## Purpose

TBD — defines the `codemoo` variant of RetryBot: a production-oriented coding assistant with a comprehensive system prompt covering all capability layers, used as the default bot for code and business chat in the TUI.

## Requirements

### Requirement: RetryBot has a codemoo variant for production coding work
A `codemoo` variant of `RetryBot` SHALL be declared in `codemoo.toml`. It SHALL use the same tools, context source, memory file, and capabilities as the existing `code` variant, but with a dedicated instruction file (`retry_bot-codemoo.txt`) whose system prompt covers all capability layers comprehensively.

#### Scenario: codemoo variant loads and runs
- **WHEN** the TUI is started with the `codemoo` variant of RetryBot
- **THEN** the bot SHALL start up without error, loading project context and memory

#### Scenario: codemoo variant system prompt covers all capabilities
- **WHEN** the instruction file `retry_bot-codemoo.txt` is read
- **THEN** it SHALL mention: the available tools by name, planning (naming steps for multi-step tasks), approval gates, retry policy, project context, memory updates, and terse output style

### Requirement: codemoo variant is the TUI default for code and business chat
The `main_bot` section of `codemoo.toml` SHALL declare `code = { type = "RetryBot", variant = "codemoo" }` as the default for the code chat mode. The `code_chat` and `business_chat` entry points in `tui.py` SHALL use this variant.

#### Scenario: TUI code chat uses the codemoo variant by default
- **WHEN** `uv run codemoo` is launched without arguments
- **THEN** the active bot SHALL be the `codemoo` variant of RetryBot
