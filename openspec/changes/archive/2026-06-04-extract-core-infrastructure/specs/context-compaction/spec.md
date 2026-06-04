## MODIFIED Requirements

### Requirement: ChatApp calls compact() before on_message if the method exists
`ChatApp._collect_replies` SHALL check `getattr(participant, "compact_threshold", None)`
before calling `participant.on_message`. If the attribute is not `None`, it SHALL call
`self._chat_context = await compact_context(self._chat_context, participant.llm, threshold, getattr(participant, "commentator", None), participant.name)`
before the `on_message` call. The updated `_chat_context` SHALL be passed to `on_message`
and used for all subsequent context operations in that turn.

Compaction is triggered by a non-`None` `compact_threshold` attribute on the participant,
not by the presence of a `compact()` method. Participants opt into compaction via TOML
configuration; no bot-level code is required.

#### Scenario: Participant without compact_threshold is unaffected
- **WHEN** a participant does not have a `compact_threshold` attribute, or it is `None`
- **THEN** `ChatApp` SHALL call `on_message` with the unchanged `_chat_context`

#### Scenario: Participant with compact_threshold has _chat_context updated before on_message
- **WHEN** a participant has a non-`None` `compact_threshold` and `compact_context` returns a modified context
- **THEN** `ChatApp` SHALL replace `_chat_context` with the returned list before calling `on_message`

#### Scenario: ContextStatus reflects token count after compaction
- **WHEN** compact_context disables old items and _chat_context is updated
- **THEN** the ContextStatus token count SHALL drop because `build_context` skips DISABLED items
