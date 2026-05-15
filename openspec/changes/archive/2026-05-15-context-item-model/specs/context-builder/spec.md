## ADDED Requirements

### Requirement: build_context is a pure function with no side effects
The system SHALL provide a `build_context(items: list[ContextItem]) -> list[Message]` function. It SHALL be a pure function: it SHALL NOT modify its input, SHALL NOT perform I/O, and SHALL produce the same output for the same input.

#### Scenario: Empty context produces an empty message list
- **WHEN** `build_context([])` is called
- **THEN** the returned list SHALL be empty

---

### Requirement: DISABLED items are excluded from the output
Any `ContextItem` with `mode == ItemMode.DISABLED` SHALL be omitted from the `list[Message]` produced by `build_context()`.

#### Scenario: Disabled item does not appear in output
- **WHEN** `build_context()` is called with a list containing a `ContextItem` whose `mode` is `DISABLED`
- **THEN** no `Message` corresponding to that item SHALL appear in the output

---

### Requirement: EDITED mode substitutes the edited field for content text
When a `ContextItem` has `mode == ItemMode.EDITED`, `build_context()` SHALL use the value of `item.edited` as the message content instead of the content type's natural text. The content type determines the role.

#### Scenario: EDITED item uses edited text
- **WHEN** `build_context()` is called with a `ContextItem` whose `mode` is `EDITED` and `edited` is a non-None string
- **THEN** the corresponding `Message` SHALL have `content` equal to `item.edited`

---

### Requirement: SUMMARY mode substitutes the summary field for content text
When a `ContextItem` has `mode == ItemMode.SUMMARY`, `build_context()` SHALL use the value of `item.summary` as the message content. The content type determines the role.

#### Scenario: SUMMARY item uses summary text
- **WHEN** `build_context()` is called with a `ContextItem` whose `mode` is `SUMMARY` and `summary` is a non-None string
- **THEN** the corresponding `Message` SHALL have `content` equal to `item.summary`

---

### Requirement: ToolUseContent is unrolled into two Messages
A `ContextItem` containing `ToolUseContent` SHALL produce exactly two `Message`s in the output: an assistant message carrying the tool call (with `tool_calls_json` set) followed by a tool-role message carrying the result (with `tool_call_id` set). The order SHALL always be call before result.

#### Scenario: ToolUseContent produces assistant then tool messages
- **WHEN** `build_context()` processes a `ContextItem` with `ToolUseContent`
- **THEN** the output SHALL contain an `assistant`-role `Message` with `tool_calls_json` encoding the call
- **THEN** immediately followed by a `tool`-role `Message` with `tool_call_id` matching the call's `call_id` and `content` equal to the result output

#### Scenario: DISABLED ToolUseContent produces no messages
- **WHEN** `build_context()` processes a `ContextItem` with `ToolUseContent` and `mode == DISABLED`
- **THEN** neither the assistant call message nor the tool result message SHALL appear in the output

---

### Requirement: role_override replaces the natural role of an item
When `ContextItem.role_override` is not `None`, `build_context()` SHALL use `role_override` as the `Message.role` instead of the role derived from the content type. `role_override` SHALL NOT apply to `ToolUseContent` items (which produce two messages with fixed roles).

#### Scenario: role_override changes the message role
- **WHEN** `build_context()` processes a `ContextItem` with `role_override` set to a non-None value and content that is not `ToolUseContent`
- **THEN** the corresponding `Message` SHALL have `role` equal to `role_override`

#### Scenario: role_override is ignored for ToolUseContent
- **WHEN** `build_context()` processes a `ContextItem` with `ToolUseContent` and a non-None `role_override`
- **THEN** the two output Messages SHALL use their fixed roles (`assistant` and `tool`), ignoring `role_override`

---

### Requirement: Content types map to natural roles
When `role_override` is None, `build_context()` SHALL derive the `Message` role from the content type as follows: `UserMessageContent` → `"user"`, `AssistantMessageContent` → `"assistant"`, `InjectedContent` → the value of `InjectedContent.role`, `SystemContent` → `"system"`.

#### Scenario: UserMessageContent produces a user-role message
- **WHEN** `build_context()` processes a `ContextItem` with `UserMessageContent` and no `role_override`
- **THEN** the output `Message` SHALL have `role == "user"`

#### Scenario: InjectedContent uses its own role field
- **WHEN** `build_context()` processes a `ContextItem` with `InjectedContent(role="assistant")`
- **THEN** the output `Message` SHALL have `role == "assistant"`
