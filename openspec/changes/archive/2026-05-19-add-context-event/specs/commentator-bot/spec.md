## MODIFIED Requirements

### Requirement: CommentatorBot generates persona-driven commentary on events
`CommentatorBot` SHALL accept a `CommentaryEvent` via its `comment(event)` method, randomly select one of its personas from `self.personas` (uniform weight), call the LLM backend with a persona-appropriate prompt built by interpolating the matching template from `self.templates`, and post the resulting `ChatMessage` via its registered post callback. The event union type SHALL be `ToolEvent | LoadEvent | ContextEvent`. The persona SHALL be chosen freshly on each `comment()` call.

#### Scenario: Commentary posted with random persona name
- **WHEN** `comment(event)` is called
- **THEN** the `ChatMessage` posted via the callback SHALL have a `sender` matching one of the names in `self.personas`

#### Scenario: Different personas may appear across multiple calls
- **WHEN** `comment(event)` is called multiple times in the same session
- **THEN** the sender name MAY differ between calls (persona is chosen per call, not per session)
