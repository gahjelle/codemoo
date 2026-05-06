## Purpose

Allow bot variant entries in `codemoo.toml` to reference external files for instructions and example prompts instead of embedding them inline. The config loader resolves file references before Pydantic validation, keeping `BotVariantConfig` schema unchanged.

## Requirements

### Requirement: Bot variant TOML entries support instruction_file as an alternative to inline instructions
A bot variant entry in `codemoo.toml` MAY include `instruction_file: str` instead of (or in place of) `instructions: str`. When present, the config loader SHALL read the named file from `src/codemoo/config/instructions/` and substitute its content as the `instructions` string before Pydantic validation. Both keys SHALL NOT be present simultaneously in one variant entry.

#### Scenario: instruction_file is resolved to instructions string
- **WHEN** a variant entry contains `instruction_file = "system_bot-default.txt"`
- **THEN** `config.bots["SystemBot"].variants["default"].instructions` SHALL equal the full text content of `src/codemoo/config/instructions/system_bot-default.txt`

#### Scenario: Inline instructions are preserved when no instruction_file is present
- **WHEN** a variant entry contains `instructions = "You are a helpful bot."` and no `instruction_file` key
- **THEN** `config.bots[bot_type].variants[variant].instructions` SHALL equal `"You are a helpful bot."`

#### Scenario: Missing instruction_file raises FileNotFoundError at startup
- **WHEN** a variant entry contains `instruction_file = "nonexistent.txt"` and the file does not exist
- **THEN** the config loader SHALL raise `FileNotFoundError` at import time

#### Scenario: instruction_file content is read as UTF-8
- **WHEN** an instruction file contains non-ASCII characters (e.g. em-dash, emoji)
- **THEN** `BotVariantConfig.instructions` SHALL contain those characters correctly decoded

### Requirement: Bot variant TOML entries support prompts_file as an alternative to inline prompts
A bot variant entry in `codemoo.toml` MAY include `prompts_file: str` instead of (or in place of) `prompts: list[str]`. When present, the config loader SHALL read the named file from `src/codemoo/config/example_prompts/`, split on `---` lines, strip whitespace from each segment, discard empty segments, and substitute the result as the `prompts` list before Pydantic validation. Both keys SHALL NOT be present simultaneously in one variant entry.

#### Scenario: prompts_file is split on --- separators and resolved to prompts list
- **WHEN** a variant entry contains `prompts_file = "guard_bot-code.txt"` and the file contains three prompts separated by `---` lines
- **THEN** `config.bots["GuardBot"].variants["code"].prompts` SHALL be a list of three strings, one per prompt segment

#### Scenario: Leading and trailing whitespace is stripped from each prompt segment
- **WHEN** a prompts file has blank lines before and after each prompt segment
- **THEN** each string in the resolved `prompts` list SHALL have no leading or trailing whitespace

#### Scenario: Empty segments after splitting are discarded
- **WHEN** a prompts file ends with a trailing `---` line
- **THEN** the resolved `prompts` list SHALL NOT contain an empty string for the trailing segment

#### Scenario: A prompt segment containing a blank line is kept intact
- **WHEN** a prompt segment contains an internal blank line (not a `---` line)
- **THEN** that segment SHALL be parsed as a single prompt string, preserving the internal blank line

#### Scenario: Inline prompts list is preserved when no prompts_file is present
- **WHEN** a variant entry contains `prompts = ["Hello!", "How are you?"]` and no `prompts_file` key
- **THEN** `config.bots[bot_type].variants[variant].prompts` SHALL equal `["Hello!", "How are you?"]`

### Requirement: Resolution occurs before Pydantic validation; BotVariantConfig schema is unchanged
The config loader SHALL resolve `instruction_file` and `prompts_file` references by mutating the raw TOML dict before passing it to `Configuration.from_dict()` and subsequently to `convert_model(CodemooConfig)`. `BotVariantConfig` SHALL retain its existing fields (`description`, `tools`, `prompts`, `instructions`, `context_source`) without modification. `instruction_file` and `prompts_file` SHALL NOT appear as fields on `BotVariantConfig`.

#### Scenario: BotVariantConfig with instruction_file in raw TOML passes validation
- **WHEN** the loader resolves `instruction_file` to `instructions` before validation
- **THEN** `BotVariantConfig` SHALL parse without error and `.instructions` SHALL contain the file content

#### Scenario: instruction_file key does not appear on BotVariantConfig after loading
- **WHEN** `codemoo.toml` is loaded successfully
- **THEN** no `BotVariantConfig` instance SHALL have an `instruction_file` attribute
