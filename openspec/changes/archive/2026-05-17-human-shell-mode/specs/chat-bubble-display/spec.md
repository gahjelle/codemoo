## ADDED Requirements

### Requirement: Shell output bubbles use `bubble--shell` CSS class
A shell output bubble SHALL carry the CSS classes `bubble--shell` and `bubble--verbatim`. Its color and alignment SHALL be defined in the external TCSS stylesheet via `bubble--shell`, distinct from `bubble--bot`, `bubble--human`, `bubble--error`, and `bubble--commentator`.

#### Scenario: Shell bubble has correct CSS classes
- **WHEN** a shell output bubble is appended to the chat log
- **THEN** the bubble SHALL have the CSS class `bubble--shell`
- **THEN** the bubble SHALL have the CSS class `bubble--verbatim`

## MODIFIED Requirements

### Requirement: Bubble color is keyed to the participant
Each participant type SHALL have a distinct bubble background color defined in the external stylesheet. The color SHALL be applied via a CSS class, not an inline style. The bot bubble background color SHALL be chosen to maintain visible contrast against Textual's Markdown code-block rendering. Error bot messages SHALL use a distinct red-tinted background to visually distinguish them from normal bot messages. Commentary messages SHALL use a distinct grey-tinted background that is softer and less prominent than the main bot bubble, signalling that the content is an aside rather than a direct reply. Shell output messages SHALL use a distinct background that signals terminal/system output, visually separate from all other bubble types.

When a message's sender is not found in the app's sender registry, the bubble SHALL default to the `bubble--commentator` CSS class, allowing new commentator personas to appear without explicit registration.

The five CSS classes are:
- `bubble--human`: blue-tinted background for human messages
- `bubble--bot`: dark violet background for regular bot messages
- `bubble--error`: dark red background for ErrorBot messages
- `bubble--commentator`: soft grey background for CommentatorBot messages
- `bubble--shell`: distinct background for shell output messages

#### Scenario: Human bubble uses human color class
- **WHEN** a human message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--human` and SHALL render with the human background color defined in the stylesheet

#### Scenario: Bot bubble uses bot color class
- **WHEN** a non-human, non-error participant's message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--bot` and SHALL render with the bot background color defined in the stylesheet

#### Scenario: ErrorBot bubble uses error color class
- **WHEN** an ErrorBot message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--error` and SHALL render with a red-tinted background visually distinct from both `bubble--human` and `bubble--bot`

#### Scenario: Bot bubble background contrasts with code-block background
- **WHEN** a bot message contains a fenced code block
- **THEN** the code-block background SHALL be visually distinguishable from the surrounding bot bubble background

#### Scenario: Commentator bubble uses commentator color class
- **WHEN** a CommentatorBot message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--commentator` and SHALL render with a soft grey background visually distinct from `bubble--bot` and `bubble--error`

#### Scenario: Unknown sender falls back to commentator class
- **WHEN** a message is appended whose sender name is not in the sender registry
- **THEN** the bubble SHALL default to `bubble--commentator` CSS class

#### Scenario: Shell bubble uses shell color class
- **WHEN** a shell output bubble is appended to the chat log
- **THEN** the bubble SHALL have the CSS class `bubble--shell` and SHALL render with a background color visually distinct from all other bubble types

### Requirement: Non-Markdown bubbles render as Static with appropriate markup mode
`_BubbleContent` SHALL render the message body via `Static` (not `Markdown`) for commentator and shell bubbles, using different markup modes suited to each:

- Bubbles with the `bubble--commentator` CSS class SHALL use `Static(text, markup=True)`, allowing Rich markup (e.g. `[dim]`, `[bold]`) to render.
- Bubbles with the `bubble--verbatim` CSS class SHALL use `Static(text, markup=False)`, rendering all text as literal characters with no markup processing.
- All other bubbles SHALL use `Markdown`.

The `bubble--commentator` class does NOT carry `bubble--verbatim`; they are separate rendering paths.

#### Scenario: Commentator bubble renders as Rich-markup Static
- **WHEN** a bubble with the `bubble--commentator` CSS class is rendered
- **THEN** the message body SHALL be rendered via `Static` with `markup=True`
- **THEN** Rich markup such as `[dim]text[/dim]` SHALL render as styled text

#### Scenario: Shell bubble renders as plain-text Static
- **WHEN** a bubble with the `bubble--verbatim` CSS class is rendered
- **THEN** the message body SHALL be rendered via `Static` with `markup=False`
- **THEN** Markdown syntax and Rich markup in the text SHALL appear as literal characters

#### Scenario: Bot bubble renders as Markdown
- **WHEN** a bubble with neither `bubble--commentator` nor `bubble--verbatim` is rendered
- **THEN** the message body SHALL be rendered via `Markdown`
