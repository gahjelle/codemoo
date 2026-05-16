## ADDED Requirements

### Requirement: Human bubbles are right-aligned via CSS
The chat UI SHALL render human message bubbles right-aligned and bot message bubbles left-aligned. Alignment SHALL be implemented via CSS (`align-horizontal: right` on the outer `ChatBubble` widget for the `bubble--human` class), not via Python spacer logic. The `ChatBubble` widget SHALL NOT require an `is_human` parameter; the CSS class alone determines alignment and color.

#### Scenario: Human bubble is right-aligned
- **WHEN** a human message is appended to the chat log
- **THEN** the bubble content SHALL appear on the right side of the chat log row

#### Scenario: Bot bubble is left-aligned
- **WHEN** a bot message is appended to the chat log
- **THEN** the bubble content SHALL appear on the left side of the chat log row
