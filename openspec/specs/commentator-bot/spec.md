# Spec: commentator-bot

## Purpose

TBD — defines `CommentatorBot`, a non-participant observer bot that generates persona-driven commentary on tool call events and posts it to the chat UI without entering the conversation history.

## Requirements

### Requirement: CommentatorBot generates persona-driven commentary on events
`CommentatorBot` SHALL accept a `CommentaryEvent` via its `comment(event)` method, randomly select one of its four personas (Arne, Herwich, Sølve, Rike), call the LLM backend with a persona-appropriate prompt, and post the resulting `ChatMessage` via its registered post callback. The persona SHALL be chosen freshly on each `comment()` call.

#### Scenario: Commentary posted with random persona name
- **WHEN** `comment(event)` is called
- **THEN** the `ChatMessage` posted via the callback SHALL have a `sender` matching one of: Arne, Herwich, Sølve, Rike

#### Scenario: Different personas may appear across multiple calls
- **WHEN** `comment(event)` is called multiple times in the same session
- **THEN** the sender name MAY differ between calls (persona is chosen per call, not per session)

### Requirement: CommentatorBot falls back to Streik on LLM failure
If the LLM call inside `comment()` raises any exception, `CommentatorBot` SHALL catch it, suppress it, and post a hardcoded fallback `ChatMessage` with sender "Streik" and a plain log-style text in the format: `{bot_name} calls {tool_name}({formatted_args})`.

#### Scenario: Fallback message posted on LLM error
- **WHEN** the LLM backend raises during `comment()`
- **THEN** a `ChatMessage` with sender "Streik" SHALL be posted via the callback
- **THEN** no exception SHALL propagate out of `comment()`

#### Scenario: Fallback text includes tool name and arguments
- **WHEN** the LLM backend raises during a `ToolCallEvent` comment
- **THEN** the fallback text SHALL include the tool name and a readable representation of the arguments

### Requirement: CommentatorBot registers a post callback before use
`CommentatorBot` SHALL expose a `register(post_fn)` method that stores the callable used to post `ChatMessage` objects to the UI. `comment()` SHALL only be called after `register()` has been called.

#### Scenario: Post function called with generated ChatMessage
- **WHEN** `comment(event)` is called after `register(fn)` has been called
- **THEN** `fn` SHALL be called with a `ChatMessage` whose `sender` is the chosen persona name

### Requirement: CommentatorBot is not a ChatParticipant
`CommentatorBot` SHALL NOT implement `on_message`, SHALL NOT appear in the `ChatApp` participants list, and SHALL NOT have its messages entered into the conversation history.

#### Scenario: Commentary messages absent from history
- **WHEN** `comment()` posts a message to the UI
- **THEN** that message SHALL NOT appear in the `history` list passed to subsequent `on_message` calls

### Requirement: Four personas with distinct characters
`CommentatorBot` SHALL define four named personas used for LLM commentary:
- **Arne** — enthusiastic; treats every tool call as exciting
- **Herwich** — formal and bureaucratic; precise and measured
- **Sølve** — dry and terse; one-liners, takes nothing seriously
- **Rike** — skeptical; questions the necessity of each action

Each persona SHALL supply a system-prompt that encodes its character and instructs the LLM to comment briefly (one sentence) on the tool call being observed. The system prompt SHALL NOT contain a hardcoded language instruction; instead it SHALL append `language_instruction()` from `codemoo.config`.

#### Scenario: Arne persona is enthusiastic
- **WHEN** Arne is the active persona
- **THEN** the LLM system prompt SHALL encode an enthusiastic character

#### Scenario: Sølve persona is dry and terse
- **WHEN** Sølve is the active persona
- **THEN** the LLM system prompt SHALL encode a dry, terse character and instruct brevity

#### Scenario: No hardcoded language in persona prompts
- **WHEN** `CODEMOO_LANGUAGE` is not set
- **THEN** no persona system prompt SHALL contain a hardcoded language instruction (e.g., "Answer in Norwegian")
