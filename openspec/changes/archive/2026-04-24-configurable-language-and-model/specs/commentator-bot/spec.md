## MODIFIED Requirements

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
