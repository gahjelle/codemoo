## ADDED Requirements

### Requirement: RetryBot is registered in codemoo.toml with name, emoji, sources, and three variants
`codemoo.toml` SHALL contain a `[bots.RetryBot]` block with `name = "Undo"`, `emoji = "BOOMERANG"`, and `sources = ["retry_bot.py"]`. Three variant blocks SHALL follow: `[bots.RetryBot.variants.code]`, `[bots.RetryBot.variants.m365]`, and `[bots.RetryBot.variants.workspace]`, each with an `instruction_file`, `prompts_file`, tool list, and context source matching MemoryBot's variant structure (but pointing to retry_bot instruction/prompt files).

#### Scenario: RetryBot config resolves to correct name and emoji
- **WHEN** `config.bots["RetryBot"]` is accessed
- **THEN** `config.bots["RetryBot"].name` SHALL equal `"Undo"`
- **AND** `config.bots["RetryBot"].emoji` SHALL equal `"BOOMERANG"`

### Requirement: BOTS.md emoji table includes 🪃 BOOMERANG for RetryBot
The RetryBot row in `BOTS.md`'s bot emoji table SHALL be updated from provisional (no emoji) to include `🪃` in the Emoji column and `BOOMERANG` in the Emoji name column. RetryBot SHALL be moved from the "Provisional" section to the "Implemented (final)" section of the Bot Character Reference credo table, with credo `"Failure is data — use it."`

#### Scenario: BOTS.md shows RetryBot as implemented with emoji
- **WHEN** `BOTS.md` is read
- **THEN** the RetryBot row SHALL show `🪃` and `BOOMERANG` in the emoji columns
- **AND** RetryBot SHALL appear in the "Implemented (final)" credo table with the correct credo
