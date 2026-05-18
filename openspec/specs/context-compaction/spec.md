# Spec: context-compaction

## Purpose

TBD — defines the duck-typing protocol by which `ChatApp` integrates context compaction into its message-handling loop, allowing any bot that implements `compact()` to trim conversation context before `on_message` is called.

## Requirements

### Requirement: ChatApp calls compact() before on_message if the method exists
`ChatApp._collect_replies` SHALL check `hasattr(participant, 'compact')` before calling `participant.on_message`. If the method exists, it SHALL call `self._chat_context = await participant.compact(self._chat_context)` before the `on_message` call. The updated `_chat_context` SHALL be passed to `on_message` and used for all subsequent context operations in that turn.

#### Scenario: Participant without compact() is unaffected
- **WHEN** a participant does not have a `compact` attribute
- **THEN** `ChatApp` SHALL call `on_message` with the unchanged `_chat_context`

#### Scenario: Participant with compact() has _chat_context updated before on_message
- **WHEN** a participant implements `compact()` and returns a modified context
- **THEN** `ChatApp` SHALL replace `_chat_context` with the returned list before calling `on_message`

#### Scenario: ContextStatus reflects token count after compaction
- **WHEN** compact() disables old items and _chat_context is updated
- **THEN** the ContextStatus token count SHALL drop because `build_context` skips DISABLED items
