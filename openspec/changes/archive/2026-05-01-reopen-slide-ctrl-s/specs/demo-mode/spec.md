## ADDED Requirements

### Requirement: Ctrl-S reopens the current bot's slide in demo mode
While in a demo-mode `ChatApp` session, pressing Ctrl-S SHALL reopen the current bot's `SlideScreen` as a modal overlay. The chat log and input state SHALL be preserved while the modal is visible and restored when it is dismissed.

#### Scenario: Ctrl-S opens the slide mid-chat
- **WHEN** the user presses Ctrl-S during an active demo session
- **THEN** a `SlideScreen` for the current bot SHALL be pushed as a modal overlay on top of the chat

#### Scenario: Ctrl-S does not clear chat history
- **WHEN** the user sends several messages, presses Ctrl-S, and dismisses the slide
- **THEN** all prior chat bubbles SHALL still be visible in the log

#### Scenario: Ctrl-S is a no-op when a SlideScreen is already visible
- **WHEN** a `SlideScreen` is already displayed and the user presses Ctrl-S
- **THEN** no additional modal SHALL be pushed

#### Scenario: Ctrl-S is not active outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot` (not demo mode)
- **THEN** pressing Ctrl-S SHALL have no effect
