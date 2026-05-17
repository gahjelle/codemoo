## ADDED Requirements

### Requirement: CommentatorBot loads prompt templates from config at construction time
`CommentatorBot` SHALL accept a `templates: dict[str, str]` constructor argument containing pre-loaded template strings keyed by event outcome or kind (`"call"`, `"blocked"`, `"error"`, `"context"`, `"memory"`). The templates SHALL be loaded by `config/__init__.py` via `_resolve_commentary_template_refs()` and passed through `CodemooConfig.commentary_templates`. `CommentatorBot` SHALL NOT perform any file I/O itself.

#### Scenario: Templates available at first comment call
- **WHEN** `CommentatorBot` is constructed with a non-empty `templates` dict
- **THEN** `self.templates["call"]` SHALL return the loaded template string without any file read

#### Scenario: Missing template key raises at prompt-build time
- **WHEN** `comment(ToolEvent(outcome="call"))` is called
- **AND** `self.templates` does not contain the key `"call"`
- **THEN** a `KeyError` SHALL propagate (fail loudly, not silently)

### Requirement: Prompt templates use str.format() interpolation with named placeholders
Template files SHALL use Python `str.format()` named placeholders. `CommentatorBot` SHALL call `template.format(**variables)` where `variables` is a dict assembled from the event's fields. The available variables per template key SHALL be:

| Key | Available variables |
|---|---|
| `call` | `bot_name`, `tool_name`, `sig` |
| `blocked` | `bot_name`, `tool_name`, `sig`, `detail` |
| `error` | `bot_name`, `tool_name`, `sig`, `detail` |
| `context` | `bot_name`, `source_desc`, `content_len`, `preview` |
| `memory` | `bot_name`, `path`, `content_len`, `preview` |

#### Scenario: Template interpolation produces a non-empty prompt string
- **WHEN** a valid template is filled with event fields
- **THEN** the resulting prompt string SHALL be non-empty and contain at least one interpolated value

## MODIFIED Requirements

### Requirement: CommentatorBot generates persona-driven commentary on events
`CommentatorBot` SHALL accept a `CommentaryEvent` via its `comment(event)` method, randomly select one of its personas from `self.personas` (uniform weight), call the LLM backend with a persona-appropriate prompt built by interpolating the matching template from `self.templates`, and post the resulting `ChatMessage` via its registered post callback. The event union type SHALL be `ToolEvent | LoadEvent | BotRestartEvent`. The persona SHALL be chosen freshly on each `comment()` call.

#### Scenario: Commentary posted with random persona name
- **WHEN** `comment(event)` is called
- **THEN** the `ChatMessage` posted via the callback SHALL have a `sender` matching one of the names in `self.personas`

#### Scenario: Different personas may appear across multiple calls
- **WHEN** `comment(event)` is called multiple times in the same session
- **THEN** the sender name MAY differ between calls (persona is chosen per call, not per session)
