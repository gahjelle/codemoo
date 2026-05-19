## REMOVED Requirements

### Requirement: BotRestartEvent carries the restarting bot's name
**Reason**: Replaced by `ContextEvent(kind="restart")`, which carries richer content (item count, message preview) enabling meaningful persona commentary.
**Migration**: Replace `BotRestartEvent(bot_name=name)` with `ContextEvent(kind="restart", bot_name=name, items_affected=n, preview=preview_text)`.

### Requirement: CommentatorBot generates persona commentary for BotRestartEvent
**Reason**: `_comment_on_restart` is replaced by `_comment_on_context`, which handles both `kind="restart"` and `kind="compact"` via template-file lookup.
**Migration**: No external callers. Internal to `CommentatorBot`.

## ADDED Requirements

### Requirement: ContextEvent is a unified frozen dataclass for context window operations
`ContextEvent` SHALL be a frozen dataclass defined in `commentator_bot.py` alongside the other event types, with fields: `kind: Literal["restart", "compact"]`, `bot_name: str`, `items_affected: int`, and `preview: str`. It SHALL be included in the `CommentatorBot.comment()` union type in place of `BotRestartEvent`.

#### Scenario: ContextEvent restart kind carries item count and message preview
- **WHEN** `ChatApp._restart_bot()` constructs a `ContextEvent`
- **THEN** `event.kind` SHALL be `"restart"`
- **AND** `event.bot_name` SHALL equal the name of the active participant
- **AND** `event.items_affected` SHALL equal the number of items in `_chat_context` before clearing
- **AND** `event.preview` SHALL be the concatenation of the last two user/assistant message texts, each truncated to 300 characters

#### Scenario: ContextEvent compact kind carries compacted item count and summary preview
- **WHEN** `CompactBot.compact()` constructs a `ContextEvent`
- **THEN** `event.kind` SHALL be `"compact"`
- **AND** `event.items_affected` SHALL equal the number of items that were disabled (not pinned, outside the recent window)
- **AND** `event.preview` SHALL be the first 300 characters of the LLM-generated summary text

### Requirement: CommentatorBot handles ContextEvent via template-file dispatch
`CommentatorBot.comment()` SHALL accept `ContextEvent` in its event union. It SHALL dispatch to `_comment_on_context(event)`, which looks up the prompt template using `self.templates[event.kind]`, interpolates it with the event's fields, and generates persona commentary. Both `"restart"` and `"compact"` template keys SHALL be present in `self.templates`.

#### Scenario: ContextEvent restart produces a commentary bubble with dim prefix
- **WHEN** `commentator.comment(ContextEvent(kind="restart", bot_name="Drop", items_affected=12, preview="..."))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the dimmed prefix SHALL read `"Restarted — 12 items dropped"`
- **AND** the bubble SHALL include an LLM-generated in-character sentence with a lamenting tone

#### Scenario: ContextEvent compact produces a commentary bubble with dim prefix
- **WHEN** `commentator.comment(ContextEvent(kind="compact", bot_name="Drop", items_affected=8, preview="..."))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the dimmed prefix SHALL read `"Compacted 8 items"`
- **AND** the bubble SHALL include an LLM-generated in-character sentence with a celebratory tone

#### Scenario: Commentary falls back to Streik on LLM failure for both kinds
- **WHEN** the LLM call inside `_comment_on_context` raises an exception
- **THEN** a fallback message SHALL be posted using the Streik persona
- **AND** no exception SHALL propagate out of `comment()`

### Requirement: All commentary events are template-file backed
Every event type handled by `CommentatorBot` SHALL use a template key from `self.templates`. No event handler SHALL use a hardcoded inline prompt string. The `[commentary_templates]` section in `codemoo.toml` SHALL include keys `restart` and `compact` pointing to `context_restart.txt` and `context_compact.txt` respectively.

#### Scenario: codemoo.toml contains restart and compact template keys
- **WHEN** the application loads `codemoo.toml`
- **THEN** `config.commentary_templates["restart"]` SHALL resolve to the content of `context_restart.txt`
- **AND** `config.commentary_templates["compact"]` SHALL resolve to the content of `context_compact.txt`
