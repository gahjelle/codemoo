## MODIFIED Requirements

### Requirement: CommentatorBot generates persona-driven commentary on events
`CommentatorBot` SHALL accept a `CommentaryEvent` via its `comment(event)` method, randomly select one of its personas from `self.personas` (uniform weight), call the LLM backend with a persona-appropriate prompt, and post the resulting `ChatMessage` via its registered post callback. The persona SHALL be chosen freshly on each `comment()` call.

#### Scenario: Commentary posted with random persona name
- **WHEN** `comment(event)` is called
- **THEN** the `ChatMessage` posted via the callback SHALL have a `sender` matching one of the names in `self.personas`

#### Scenario: Different personas may appear across multiple calls
- **WHEN** `comment(event)` is called multiple times in the same session
- **THEN** the sender name MAY differ between calls (persona is chosen per call, not per session)

## MODIFIED Requirements

### Requirement: Ten personas with distinct characters
`CommentatorBot` SHALL use the `personas: list[Persona]` injected at construction time. The module-level `_PERSONAS` list SHALL be removed. The ten personas and their characters are defined in the `commentator-personas` capability spec. Each persona supplies a system-prompt that encodes its character and instructs the LLM to comment briefly on the tool call being observed.

#### Scenario: All ten persona names available as senders
- **WHEN** `sender_info()` is called on a `CommentatorBot` built with all ten personas
- **THEN** the returned dict SHALL contain keys for all ten persona names plus `Streik`

#### Scenario: Empty personas list results in Streik-only fallback
- **WHEN** `CommentatorBot` is constructed with `personas=[]`
- **THEN** every `comment()` call SHALL fall back to posting a Streik message (random choice from empty list raises; implementation SHALL guard against this)

## REMOVED Requirements

### Requirement: Four personas with distinct characters
**Reason**: Replaced by the ten-persona requirement driven by injected `personas` list. The four hardcoded personas (Arne, Herwig, Sølve, Rike) are migrated to config files with updated or unchanged characters.
**Migration**: All four personas are preserved as entries in `codemoo.toml` with `instructions_file` references. Arne's character changes to sage elder; Herwig's emoji changes. No test that checks for exactly four personas remains valid.
