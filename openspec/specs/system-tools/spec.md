# Spec: system-tools

## Purpose

TBD — defines system-level tools in `src/codemoo/core/tools/system.py`, such as querying the current date and time, that are useful across bot variants.

## Requirements

### Requirement: System tools module provides current date and time
The system SHALL provide a `get_datetime` tool in `src/codemoo/core/tools/system.py` that returns the current date, time, and timezone as a human-readable string.

#### Scenario: get_datetime returns current date and time
- **WHEN** `get_datetime` tool is called with no arguments
- **THEN** system returns a string containing today's date, current time, and UTC offset
- **AND** the string is formatted as `YYYY-MM-DD HH:MM:SS+HH:MM (Timezone)`

#### Scenario: get_datetime is registered in TOOL_REGISTRY
- **WHEN** the core tools module is imported
- **THEN** `TOOL_REGISTRY["get_datetime"]` resolves to the `get_datetime` ToolDef

#### Scenario: get_datetime is available to all bots
- **WHEN** a bot variant lists `get_datetime` in its tools list in TOML
- **THEN** the bot can invoke `get_datetime` during a tool call round-trip

#### Scenario: get_datetime enables accurate calendar queries
- **WHEN** a workspace bot has `get_datetime` in its tool list
- **AND** the user asks a date-relative question (e.g., "what's on my calendar next Tuesday?")
- **THEN** the LLM calls `get_datetime` first to determine today's date
- **AND** uses the result to compute the correct target date range
