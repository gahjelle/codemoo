# Spec: chat-input

## Purpose

`ChatInput` is a self-contained Textual widget (subclass of `TextArea`) that provides multiline chat message entry. It manages its own height, submission event, and key bindings.

## Requirements

### Requirement: Submit message with Ctrl+Enter
`ChatInput` SHALL submit the current text when the user presses Ctrl+Enter, posting a `ChatInput.Submitted` message containing the stripped text, then clearing itself.

#### Scenario: Ctrl+Enter with non-empty text submits
- **WHEN** the user presses Ctrl+Enter with non-empty text in the input
- **THEN** `ChatInput.Submitted` SHALL be posted with `value` equal to the stripped text
- **THEN** the input field SHALL be cleared

#### Scenario: Ctrl+Enter with whitespace-only text is ignored
- **WHEN** the user presses Ctrl+Enter and the input contains only whitespace
- **THEN** no `ChatInput.Submitted` message SHALL be posted
- **THEN** the input field SHALL NOT be cleared

### Requirement: Enter key inserts a newline
`ChatInput` SHALL allow Enter to insert a newline character, using `TextArea`'s default behavior without override.

#### Scenario: Enter inserts newline
- **WHEN** the user presses Enter
- **THEN** a newline SHALL be inserted at the cursor position
- **THEN** no submission SHALL occur

### Requirement: Auto-grow height
`ChatInput` SHALL dynamically adjust its height between 1 and 4 rows based on the number of lines in the current text. Content beyond 4 rows SHALL remain accessible by scrolling.

#### Scenario: Single-line text shows one row
- **WHEN** the input contains a single line of text
- **THEN** the widget height SHALL be 1 row

#### Scenario: Height grows with additional lines
- **WHEN** the user adds a newline, increasing line count to N (where 1 < N ≤ 4)
- **THEN** the widget height SHALL be N rows

#### Scenario: Height is capped at four rows
- **WHEN** the text contains more than 4 lines
- **THEN** the widget height SHALL remain at 4 rows and content SHALL be scrollable

#### Scenario: Height resets after submission
- **WHEN** the input is cleared after a submission
- **THEN** the widget height SHALL return to 1 row

### Requirement: Multiline paste is accepted
`ChatInput` SHALL accept multiline text pasted via Ctrl-V, rendering it correctly and triggering auto-grow.

#### Scenario: Pasting multiline text expands the input
- **WHEN** the user pastes text containing newlines
- **THEN** the pasted text SHALL appear in full
- **THEN** the widget height SHALL grow to reflect the line count (capped at 4)

### Requirement: ChatInput fires a typed Submitted message
`ChatInput` SHALL define a nested `Submitted` message class with a `value: str` field containing the text to be sent.

#### Scenario: Submitted message carries the text value
- **WHEN** `ChatInput.Submitted` is posted
- **THEN** `event.value` SHALL equal the stripped text that was in the input at submission time
