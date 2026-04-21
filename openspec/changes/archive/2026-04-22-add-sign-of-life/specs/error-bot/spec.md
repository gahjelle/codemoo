## ADDED Requirements

### Requirement: ErrorBot is always present in every session
The system SHALL include an `ErrorBot` instance in every chat session automatically, without requiring the user to select it on the bot selection screen. It SHALL be registered alongside `HumanParticipant` before the user-chosen bots.

#### Scenario: ErrorBot present without user selection
- **WHEN** a chat session starts with any set of user-selected bots
- **THEN** an `ErrorBot` instance SHALL be registered as a participant

#### Scenario: ErrorBot silent during normal operation
- **WHEN** all participant `on_message()` calls succeed without raising exceptions
- **THEN** `ErrorBot` SHALL produce no messages in the chat log

### Requirement: ErrorBot surfaces exceptions as in-chat error bubbles
When any other participant's `on_message()` raises an exception, the dispatch loop SHALL call `ErrorBot.format_error(participant, exception)` and yield the resulting `ChatMessage` into the log. The dispatch loop SHALL then continue processing remaining participants rather than aborting. Error messages SHALL NOT be added to the BFS dispatch queue — they are display-only and SHALL NOT trigger responses from other participants.

#### Scenario: Error bubble appears on participant failure
- **WHEN** a participant's `on_message()` raises an exception
- **THEN** an error `ChatMessage` from `ErrorBot` SHALL appear in the chat log
- **THEN** the dispatch loop SHALL continue with remaining participants

#### Scenario: Other bots do not respond to error messages
- **WHEN** an error bubble is added to the chat log
- **THEN** no other participant's `on_message()` SHALL be called with that error message

#### Scenario: Multiple failures produce multiple error bubbles
- **WHEN** two participants each raise exceptions in the same dispatch round
- **THEN** two separate error bubbles SHALL appear in the chat log

### Requirement: ErrorBot uses LLM to generate error messages with a plain-text fallback
`ErrorBot.format_error()` SHALL attempt a single LLM completion to produce a human-readable, personality-flavored error message. If the LLM call itself raises an exception, `format_error()` SHALL return a plain-text fallback message containing the failing participant's name and the exception's string representation. The fallback SHALL NOT raise.

#### Scenario: LLM available — flavored message returned
- **WHEN** `format_error()` is called and the LLM responds successfully
- **THEN** the returned `ChatMessage` SHALL contain the LLM-generated text as its body

#### Scenario: LLM unavailable — plain fallback returned
- **WHEN** `format_error()` is called and the LLM call raises an exception
- **THEN** the returned `ChatMessage` SHALL contain a plain-text message identifying the failing participant and the exception
- **THEN** `format_error()` SHALL NOT raise

### Requirement: ErrorBot adopts a randomly chosen persona at startup
At instantiation, `ErrorBot` SHALL randomly select one of three named personas: **Errol**, **Glitch**, or **Murphy**. The selected persona determines the bot's `name`, `emoji`, and the system prompt used for LLM-generated error messages. The persona is fixed for the lifetime of the session.

The three personas are:
- **Errol** (`🦉`): Bumbling and apologetic. Deeply sorry about whatever just went wrong, prone to over-explaining.
- **Glitch** (`⚡`): Chaotic and technical. Treats errors as fascinating anomalies, speaks in half-finished debug thoughts.
- **Murphy** (`🌧️`): Fatalistic and dry. Everything that could go wrong did, and Murphy saw it coming.

#### Scenario: Persona is chosen at instantiation
- **WHEN** an `ErrorBot` instance is created
- **THEN** its `name` and `emoji` SHALL reflect one of the three personas for the entire session

#### Scenario: Each persona uses a distinct system prompt
- **WHEN** `format_error()` calls the LLM
- **THEN** the system prompt SHALL match the active persona's personality description

#### Scenario: ErrorBot is not human
- **WHEN** `ErrorBot.is_human` is accessed
- **THEN** it SHALL return `False`
