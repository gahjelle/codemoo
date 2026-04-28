# Spec: demo-bot-descriptions

## Purpose

TBD — defines how bot-type descriptions and source file mappings are stored for use in the demo slide screen, sourced from `configs/codemoo.toml` via `config.bots`.

## Requirements

### Requirement: slides.py reads descriptions and source lists from config
`slides.py` SHALL look up bot descriptions and source file lists via `config.bots.get(type(bot).__name__)`. When a bot type is not registered in config (e.g. `ErrorBot`), description SHALL fall back to `""` and source list SHALL fall back to `[f"{classname.lower()}.py"]`.

#### Scenario: Description for registered bot comes from config
- **WHEN** the slide screen renders for `EchoBot`
- **THEN** the description label SHALL display the value from `config.bots["EchoBot"].description`

#### Scenario: Source files for ToolBot include base class file
- **WHEN** the LLM prompt is built for a `ToolBot` instance
- **THEN** the prompt SHALL include the contents of both `tool_bot.py` and `single_turn_tool_bot.py` as specified in `config.bots["ToolBot"].sources`

#### Scenario: Unregistered bot type falls back gracefully
- **WHEN** a bot whose class name is not in `config.bots` is passed to `_bot_source_block`
- **THEN** it SHALL fall back to reading `[f"{classname.lower()}.py"]` without raising

### Requirement: slides.py uses config.paths.bots_dir for source file reading
`slides.py` SHALL read source files from `config.paths.bots_dir`, not from a hardcoded path derived from `__file__`.

#### Scenario: Source files are read from the configured directory
- **WHEN** `_read_source("echo_bot.py")` is called
- **THEN** it SHALL read from `config.paths.bots_dir / "echo_bot.py"`
