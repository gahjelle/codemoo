## ADDED Requirements

### Requirement: ContextStatus displays message count and estimated token count
`ContextStatus` SHALL display both the number of context items and the estimated token count in the format `"N messages · ~Xk tokens"` for token counts ≥ 1000, or `"N messages · ~X tokens"` for counts < 1000. The `~` prefix SHALL always be present to signal that the count is an estimate.

#### Scenario: Token count below 1000 displays as plain integer
- **WHEN** `ContextStatus` is updated with 5 messages and 842 tokens
- **THEN** the widget SHALL display `"5 messages · ~842 tokens"`

#### Scenario: Token count at or above 1000 displays as Xk with one decimal
- **WHEN** `ContextStatus` is updated with 12 messages and 3200 tokens
- **THEN** the widget SHALL display `"12 messages · ~3.2k tokens"`

#### Scenario: Widget initialises with zero counts
- **WHEN** `ContextStatus` is first mounted with no updates applied
- **THEN** it SHALL display `"0 messages · ~0 tokens"`

### Requirement: ChatApp passes token estimate to ContextStatus on every context update
`ChatApp` SHALL call `estimate_tokens(build_context(self._chat_context))` and pass the result to `ContextStatus` every time it updates the widget. The token estimate SHALL be computed from the messages that `build_context` would send to the LLM (i.e., DISABLED items excluded).

#### Scenario: Token count reflects build_context output, not raw _chat_context
- **WHEN** some items in `_chat_context` have `mode=DISABLED`
- **THEN** the displayed token count SHALL NOT include tokens from those items

#### Scenario: ContextStatus is updated after each bot turn
- **WHEN** a bot's `on_message` returns new items and `_chat_context` is extended
- **THEN** `ContextStatus` SHALL be refreshed with the updated message count and token estimate
