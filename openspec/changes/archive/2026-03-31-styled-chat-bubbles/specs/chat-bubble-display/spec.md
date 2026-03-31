## ADDED Requirements

### Requirement: Messages are displayed as styled chat bubbles
The chat UI SHALL render each message as a distinct chat bubble widget. The bubble SHALL display the sender's emoji and name in bold at the top, and the message body rendered as Markdown below.

#### Scenario: Bubble shows emoji and name header
- **WHEN** a message is appended to the chat log
- **THEN** the bubble SHALL display the sender's emoji and name in bold on the first line

#### Scenario: Bubble renders Markdown body
- **WHEN** a message with Markdown content is appended to the chat log
- **THEN** the bubble body SHALL render the Markdown (including bold, italics, code, and lists)

### Requirement: Bubble color is keyed to the participant
Each participant type SHALL have a distinct bubble background color defined in the external stylesheet. The color SHALL be applied via a CSS class, not an inline style.

#### Scenario: Human bubble uses human color class
- **WHEN** a human message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--human` and SHALL render with the human background color defined in the stylesheet

#### Scenario: Bot bubble uses bot color class
- **WHEN** a non-human participant's message is appended
- **THEN** the bubble SHALL have the CSS class `bubble--bot` and SHALL render with the bot background color defined in the stylesheet

### Requirement: Human messages align right; others align left
Human participant bubbles SHALL be aligned to the right side of the chat log. All other participant bubbles SHALL be aligned to the left. Both SHALL use most of the available width for content.

#### Scenario: Human bubble aligns right
- **WHEN** a message from the human participant is displayed
- **THEN** the bubble SHALL be positioned toward the right side of the chat area

#### Scenario: Bot bubble aligns left
- **WHEN** a message from a non-human participant is displayed
- **THEN** the bubble SHALL be positioned toward the left side of the chat area

### Requirement: All bubble styles are defined in an external stylesheet
No bubble styles SHALL be applied as inline styles in Python code. All visual styling (colors, alignment, padding, margins) SHALL be declared in a `.tcss` stylesheet file and applied via CSS classes.

#### Scenario: Stylesheet controls all visual properties
- **WHEN** the chat application renders a bubble
- **THEN** the bubble's appearance SHALL be determined solely by its CSS class(es) and the external `.tcss` stylesheet
