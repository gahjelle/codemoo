## ADDED Requirements

### Requirement: BotRestartEvent carries the restarting bot's name
A `BotRestartEvent` SHALL be a frozen dataclass with one field: `bot_name: str` (the name of the bot being restarted). It SHALL be defined in `commentator_bot.py` alongside the other event types and included in the `CommentatorBot.comment()` union type.

#### Scenario: BotRestartEvent fields match the bot being restarted
- **WHEN** `ChatApp._restart_bot()` constructs a `BotRestartEvent`
- **THEN** `event.bot_name` SHALL equal the name of the active (non-human) participant

### Requirement: CommentatorBot generates persona commentary for BotRestartEvent
`CommentatorBot.comment()` SHALL accept `BotRestartEvent` in its event union. It SHALL handle the event by calling `_comment_on_restart()`, which generates LLM persona commentary about the bot's memory being cleared and a fresh start beginning.

#### Scenario: BotRestartEvent produces a commentary bubble
- **WHEN** `commentator.comment(BotRestartEvent(bot_name="Lore"))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the bubble SHALL include a dimmed prefix line (e.g. `↺ Restarted`)
- **AND** the bubble SHALL include an LLM-generated in-character sentence about the fresh start

#### Scenario: Commentary falls back to Streik on LLM failure
- **WHEN** the LLM call inside `_comment_on_restart` raises an exception
- **THEN** a fallback message SHALL be posted using the Streik persona
- **AND** the fallback SHALL reference the bot name and restart action
