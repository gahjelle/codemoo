# Spec: demo-preset-prompts

## Purpose

Defines the pre-set prompt feature for demo mode: configuration, keyboard insertion, prompt-count display, exhaustion behaviour, and optional LLM translation.

## Requirements

### Requirement: BotConfig carries an optional list of preset prompts
Each bot entry in TOML MAY include a `prompts` field containing an ordered list of strings. When absent, the list defaults to empty and the feature is inactive for that bot.

#### Scenario: Prompts field is parsed from TOML
- **WHEN** a bot entry contains `prompts = ["What is X?", "Explain Y"]`
- **THEN** `config.bots[bot_type].prompts` SHALL equal `["What is X?", "Explain Y"]`

#### Scenario: Missing prompts field defaults to empty list
- **WHEN** a bot entry does not include a `prompts` key
- **THEN** `config.bots[bot_type].prompts` SHALL equal `[]`

### Requirement: DemoContext carries the current bot's prompts
When `ChatApp` is launched in demo mode, `DemoContext` SHALL include a `prompts` field initialised from `config.bots[bot_type].prompts` for the current bot.

#### Scenario: Prompts are populated for a bot with configured prompts
- **WHEN** `DemoContext` is constructed for a bot whose config includes prompts
- **THEN** `demo_context.prompts` SHALL equal the list from config

#### Scenario: Prompts are empty for a bot with no configured prompts
- **WHEN** `DemoContext` is constructed for a bot with no `prompts` in config
- **THEN** `demo_context.prompts` SHALL be an empty list

### Requirement: Ctrl-E inserts the next preset prompt in demo mode
While in a demo-mode `ChatApp` session with remaining prompts, pressing `Ctrl-E` SHALL insert the next prompt text into the `Input` widget without submitting it, and advance the internal prompt index.

#### Scenario: First Ctrl-E inserts the first prompt
- **WHEN** the user presses `Ctrl-E` and no prompts have been used yet
- **THEN** the `Input` widget value SHALL be set to the first prompt string

#### Scenario: Second Ctrl-E inserts the second prompt
- **WHEN** the user presses `Ctrl-E` a second time
- **THEN** the `Input` widget value SHALL be set to the second prompt string

#### Scenario: Ctrl-E does nothing when prompts are exhausted
- **WHEN** all configured prompts have been used and the user presses `Ctrl-E`
- **THEN** the `Input` widget value SHALL NOT change

#### Scenario: Ctrl-E is inactive outside demo mode
- **WHEN** `ChatApp` is launched without a `demo_context`
- **THEN** pressing `Ctrl-E` SHALL have no effect on the input

### Requirement: DemoHeader shows the prompt count and Ctrl-E hint
When the current bot has configured prompts, the `DemoHeader` SHALL include a Ctrl-E hint and the number of remaining prompts. The hint SHALL update each time a prompt is consumed and SHALL indicate exhaustion when the count reaches zero.

#### Scenario: Header shows prompt count when prompts remain
- **WHEN** a bot has 3 prompts and none have been used
- **THEN** the header SHALL contain text indicating 3 prompts remain and the Ctrl-E hint

#### Scenario: Header shows "last example" when one prompt remains
- **WHEN** exactly one prompt remains
- **THEN** the header SHALL contain text indicating this is the last example

#### Scenario: Header shows exhaustion state when all prompts are used
- **WHEN** all prompts have been consumed
- **THEN** the header SHALL NOT show the Ctrl-E hint as active, and SHALL indicate no more examples remain

#### Scenario: Header shows no prompt section when no prompts are configured
- **WHEN** the current bot has an empty prompts list
- **THEN** the header SHALL NOT contain any prompt-count or Ctrl-E hint text

### Requirement: Prompts are translated eagerly during the slide screen when a non-English language is configured
If `config.language` is not `"English"` and the current bot has prompts, `SlideScreen` SHALL translate all prompts to the configured language using the LLM backend during the slide display window, and SHALL replace `DemoContext.prompts` with the translated list before the slide is dismissed.

#### Scenario: Prompts are translated when language is non-English
- **WHEN** `config.language` is `"Norwegian"` and the bot has prompts configured in English
- **THEN** after the slide worker completes, `demo_context.prompts` SHALL contain the Norwegian translations

#### Scenario: Translation failure falls back to original prompts
- **WHEN** translation produces a different number of items than the original list
- **THEN** `demo_context.prompts` SHALL remain as the original (untranslated) list

#### Scenario: No translation is attempted when language is English
- **WHEN** `config.language` is `"English"`
- **THEN** no translation LLM call SHALL be made and `demo_context.prompts` SHALL remain unchanged

#### Scenario: No translation is attempted when prompts list is empty
- **WHEN** the current bot has no configured prompts
- **THEN** no translation LLM call SHALL be made

### Requirement: Demo prompts for Acts 3–4 assume demo/ as the working directory
The preset prompts configured for FileBot, ShellBot, AgentBot, and GuardBot SHALL reference files by name only (e.g. `greeter.py`, `README.md`) without path prefixes. These prompts SHALL only work correctly when `demo/` is the process working directory. The project `README.md` and `BOTS.md` SHALL document this assumption.

#### Scenario: File paths in prompts have no directory prefix
- **WHEN** the prompts for FileBot, ShellBot, AgentBot, and GuardBot are read from config
- **THEN** no prompt SHALL contain the string `demo/` as a path prefix before a filename

#### Scenario: README documents the working directory requirement
- **WHEN** the project `README.md` Demo Mode section is read
- **THEN** it SHALL instruct the user to run the demo from the `demo/` directory
