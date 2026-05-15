## ADDED Requirements

### Requirement: ContextContent is a closed discriminated union of content types
The system SHALL define `ContextContent` as a type alias for the union of five frozen dataclasses: `UserMessageContent`, `AssistantMessageContent`, `ToolUseContent`, `InjectedContent`, and `SystemContent`. No other types SHALL be valid as `ContextItem` content.

#### Scenario: UserMessageContent carries the human's text
- **WHEN** a `UserMessageContent` is created with a `text` field
- **THEN** `text` SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: AssistantMessageContent carries the bot's final reply text
- **WHEN** an `AssistantMessageContent` is created with a `text` field
- **THEN** `text` SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: ToolUseContent carries an atomic tool call and result pair
- **WHEN** a `ToolUseContent` is created with `name`, `arguments_json`, `call_id`, and `output` fields
- **THEN** all four fields SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: InjectedContent carries manually added text with an explicit role
- **WHEN** an `InjectedContent` is created with `label`, `text`, and `role` fields
- **THEN** all three fields SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: SystemContent carries system prompt text
- **WHEN** a `SystemContent` is created with a `text` field
- **THEN** `text` SHALL be accessible and SHALL NOT be modifiable after construction

---

### Requirement: ItemMode is an enum with four values
The system SHALL define an `ItemMode` enum with exactly four members: `ORIGINAL`, `EDITED`, `SUMMARY`, and `DISABLED`. These SHALL be the only valid modes for a `ContextItem`.

#### Scenario: ItemMode members are accessible by name
- **WHEN** `ItemMode.ORIGINAL`, `ItemMode.EDITED`, `ItemMode.SUMMARY`, or `ItemMode.DISABLED` is accessed
- **THEN** each SHALL be a distinct enum member

---

### Requirement: ContextItem is an immutable value type
The system SHALL define `ContextItem` as a frozen dataclass with the following fields: `id` (str, UUID), `content` (ContextContent), `turn_id` (int), `mode` (ItemMode, default ORIGINAL), `edited` (str | None, default None), `summary` (str | None, default None), `role_override` (Role | None, default None), `pinned` (bool, default False). The `id` field SHALL default to a newly generated UUID string.

#### Scenario: ContextItem fields are set at construction
- **WHEN** a `ContextItem` is created with explicit values for all fields
- **THEN** those values SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: id defaults to a unique UUID string
- **WHEN** two `ContextItem`s are created without an explicit `id`
- **THEN** their `id` values SHALL differ

#### Scenario: mode defaults to ORIGINAL
- **WHEN** a `ContextItem` is created without an explicit `mode`
- **THEN** `mode` SHALL equal `ItemMode.ORIGINAL`

---

### Requirement: turn_id follows the monotonic increment convention
The system SHALL assign `turn_id` as `max(item.turn_id for item in context) + 1` when context is non-empty, and `0` when context is empty. All `ContextItem`s produced within a single `on_message()` call SHALL share the same `turn_id`.

#### Scenario: First turn has turn_id zero
- **WHEN** a turn_id is computed from an empty context list
- **THEN** the result SHALL be `0`

#### Scenario: Subsequent turns increment the maximum turn_id
- **WHEN** a turn_id is computed from a non-empty context list whose maximum turn_id is N
- **THEN** the result SHALL be `N + 1`

---

### Requirement: Pure operations on list[ContextItem] return new lists
The system SHALL provide pure functions for all context list mutations. None of these functions SHALL modify the input list or any of its items.

The following operations SHALL be provided:
- `next_turn_id(context: list[ContextItem]) -> int`
- `add_item(context: list[ContextItem], item: ContextItem) -> list[ContextItem]`
- `replace_item(context: list[ContextItem], item_id: str, new_item: ContextItem) -> list[ContextItem]`
- `set_mode(context: list[ContextItem], item_id: str, mode: ItemMode) -> list[ContextItem]`
- `set_edited(context: list[ContextItem], item_id: str, text: str) -> list[ContextItem]`
- `set_summary(context: list[ContextItem], item_id: str, text: str) -> list[ContextItem]`
- `inject_at(context: list[ContextItem], index: int, item: ContextItem) -> list[ContextItem]`

#### Scenario: add_item appends without mutating the original
- **WHEN** `add_item(ctx, item)` is called
- **THEN** the returned list SHALL contain all items from `ctx` followed by `item`
- **THEN** `ctx` SHALL be unchanged

#### Scenario: set_mode returns a list with the targeted item's mode changed
- **WHEN** `set_mode(ctx, item_id, mode)` is called with a valid `item_id`
- **THEN** the returned list SHALL contain the same items as `ctx` except the item with matching `id` SHALL have `mode` equal to the new value
- **THEN** all other items SHALL be unchanged

#### Scenario: inject_at inserts an item at the specified index
- **WHEN** `inject_at(ctx, index, item)` is called
- **THEN** the returned list SHALL have `item` at position `index` and all prior items before it
