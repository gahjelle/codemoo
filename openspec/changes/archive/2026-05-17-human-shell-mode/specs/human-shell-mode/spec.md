## ADDED Requirements

### Requirement: `!`-prefixed input is routed to the shell
When the user submits input beginning with `!`, the app SHALL strip the `!` prefix and pass the remainder to `_run_shell` directly, bypassing all bot participants and context machinery. The input SHALL still appear in the chat log as a human bubble.

#### Scenario: `!` command is intercepted before bots
- **WHEN** the user submits a message starting with `!`
- **THEN** no bot's `on_message` SHALL be called for that input
- **THEN** the text after `!` SHALL be passed to `_run_shell`

#### Scenario: Normal input is unaffected
- **WHEN** the user submits a message that does not start with `!`
- **THEN** the normal bot dispatch path SHALL execute unchanged

### Requirement: Shell output is displayed verbatim in a shell bubble
The output of a `!` command SHALL be displayed in a new shell output bubble attributed to a "Shell" sender with a 💻 emoji and `bubble--shell bubble--verbatim` CSS classes. The content SHALL be rendered as `Static` with `markup=False` (no Markdown parsing).

#### Scenario: Shell output appears in a distinct bubble
- **WHEN** a `!` command completes
- **THEN** a shell bubble SHALL be appended to the chat log
- **THEN** the bubble SHALL display the raw output text without Markdown rendering

#### Scenario: Shell output containing Markdown metacharacters renders correctly
- **WHEN** the shell output contains `#`, `*`, `` ` ``, or other Markdown syntax
- **THEN** those characters SHALL appear literally, not as formatted Markdown

### Requirement: Shell output is copied to the clipboard
After displaying the output, the app SHALL call `App.copy_to_clipboard()` with the full shell output string.

#### Scenario: Output is in clipboard after command
- **WHEN** a `!` command completes
- **THEN** the shell output SHALL be the current clipboard value

### Requirement: Shell output does not enter `_chat_context`
A `!` command's output SHALL NOT be added to `_chat_context` as a `ContextItem`. Bot participants SHALL not see it.

#### Scenario: Context is unchanged after shell command
- **WHEN** the user runs a `!` command
- **THEN** `_chat_context` SHALL contain only the human input item, with no shell output item appended

### Requirement: Shell commands run without sandbox or approval
`!` commands SHALL call `_run_shell` with no path validator and no `requires_approval` check. The session-folder sandbox applies only to LLM-initiated tool calls.

#### Scenario: Absolute path is permitted in `!` command
- **WHEN** the user submits `! cat /etc/hosts`
- **THEN** the command SHALL execute without being blocked by a path validator
