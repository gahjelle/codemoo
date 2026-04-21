## MODIFIED Requirements

### Requirement: Bubble color is keyed to the participant
Each participant type SHALL have a distinct bubble background color defined in the external stylesheet. The color SHALL be applied via a CSS class, not an inline style. The bot bubble background color SHALL be chosen to maintain visible contrast against Textual's Markdown code-block rendering.

#### Scenario: Human bubble uses human color class
- **WHEN** a human message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--human` and SHALL render with the human background color defined in the stylesheet

#### Scenario: Bot bubble uses bot color class
- **WHEN** a non-human participant's message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--bot` and SHALL render with the bot background color defined in the stylesheet

#### Scenario: Bot bubble background contrasts with code-block background
- **WHEN** a bot message contains a fenced code block
- **THEN** the code-block background SHALL be visually distinguishable from the surrounding bot bubble background
