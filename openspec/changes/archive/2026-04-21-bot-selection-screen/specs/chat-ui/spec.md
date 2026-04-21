## MODIFIED Requirements

### Requirement: Launch via CLI entry point
The `codaroo` CLI entry point SHALL launch a bot selection screen first. After the user confirms their selection, the Textual chat application SHALL start with the human participant and the chosen bots.

#### Scenario: Running codaroo shows the selection screen first
- **WHEN** the user runs `uv run codaroo` from the terminal
- **THEN** the bot selection screen SHALL appear before the chat UI

#### Scenario: Confirming selection opens the chat UI
- **WHEN** the user confirms their bot selection on the selection screen
- **THEN** the Textual chat application SHALL start and render the chat log and input field with the selected participants
