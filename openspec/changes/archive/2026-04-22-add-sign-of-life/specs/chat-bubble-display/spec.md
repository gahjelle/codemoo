## MODIFIED Requirements

### Requirement: Bubble color is keyed to the participant
Each participant type SHALL have a distinct bubble background color defined in the external stylesheet. The color SHALL be applied via a CSS class, not an inline style. The bot bubble background color SHALL be chosen to maintain visible contrast against Textual's Markdown code-block rendering. Error bot messages SHALL use a distinct red-tinted background to visually distinguish them from normal bot messages.

The three CSS classes are:
- `bubble--human`: blue-tinted background for human messages
- `bubble--bot`: dark violet background for regular bot messages
- `bubble--error`: dark red background for ErrorBot messages

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
