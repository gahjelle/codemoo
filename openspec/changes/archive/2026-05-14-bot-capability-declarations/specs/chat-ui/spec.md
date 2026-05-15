## ADDED Requirements

### Requirement: context_management capability mounts a ContextStatus widget
When the `"context_management"` capability is active, `ChatApp` SHALL mount a `ContextStatus` widget between `ThinkingStatus` and `ChatInput`. The widget SHALL display `Num messages: N` where `N` is the current total count of messages in `self._history`. The widget SHALL be hidden when the capability is not active.

#### Scenario: ContextStatus is present when capability is declared
- **WHEN** the active bot declares `capabilities = ["context_management"]`
- **THEN** the composed layout SHALL contain a `ContextStatus` widget

#### Scenario: ContextStatus is absent when capability is not declared
- **WHEN** the active bot has no `capabilities` entry
- **THEN** the composed layout SHALL NOT contain a `ContextStatus` widget

### Requirement: ContextStatus updates after each reply batch
After `_dispatch` completes processing a turn (all replies collected and appended to `self._history`), `ChatApp` SHALL call `ContextStatus.update_message_count(len(self._history))` if the widget is mounted.

#### Scenario: Message count increments after a bot reply
- **WHEN** the user sends a message and the bot replies
- **THEN** `ContextStatus` SHALL display `Num messages: N` where `N` reflects both the user message and the bot reply

#### Scenario: Message count is correct after multiple turns
- **WHEN** three complete turns have occurred (3 user messages + 3 bot replies = 6 messages)
- **THEN** `ContextStatus` SHALL display `Num messages: 6`
