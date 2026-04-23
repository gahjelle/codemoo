# Spec: bot-selection-screen

## Purpose

TBD — defines the startup bot selection screen that allows the user to choose which bot participants to include before launching the chat session.

## Requirements

### Requirement: Selection screen presents all available bots in a fixed order
The startup selection screen SHALL display a multi-select list of all available bot participants. The bots SHALL appear in the fixed progression order: EchoBot, LLMBot, ChatBot, SystemBot, ToolBot, FileBot, ShellBot, AgentBot. Each item in the list SHALL show both the instance name and the bot type (e.g. "Coco (EchoBot)").

#### Scenario: Bots appear in fixed progression order
- **WHEN** the selection screen is rendered
- **THEN** the list SHALL show bots in the defined progression order regardless of the order they were passed to the screen

#### Scenario: Each item shows name and type
- **WHEN** a bot named "Coco" of type `EchoBot` is in the available list
- **THEN** its list entry SHALL display text containing both "Coco" and "EchoBot"

### Requirement: User can select zero or more bots before starting the chat
The selection screen SHALL allow the user to toggle any combination of bots on or off, including selecting none. Confirming with zero bots selected SHALL be valid and SHALL start a session with only the human participant.

#### Scenario: All bots selected
- **WHEN** the user selects all available bots and confirms
- **THEN** the chat session SHALL start with all eight bot types plus the human participant

#### Scenario: No bots selected
- **WHEN** the user confirms with no bots selected
- **THEN** the chat session SHALL start with only the human participant and no bots

#### Scenario: Subset of bots selected
- **WHEN** the user selects only LLMBot and confirms
- **THEN** the chat session SHALL start with the human participant and LLMBot only

### Requirement: Confirmation launches the chat session with selected participants
When the user confirms their selection, the selection screen SHALL close and the chat application SHALL start with the human participant plus the selected bots, in the fixed display order.

#### Scenario: Chat starts after confirmation
- **WHEN** the user confirms the selection
- **THEN** the Textual chat application SHALL open and display the chat log and input field

#### Scenario: Participant order in chat matches fixed order
- **WHEN** the user selects a mix of bots and confirms
- **THEN** the participants passed to the chat session SHALL follow the order: human, EchoBot (if selected), LLMBot (if selected), ChatBot (if selected), SystemBot (if selected), ToolBot (if selected), FileBot (if selected), ShellBot (if selected), AgentBot (if selected)

### Requirement: Selection screen is accessed via the select subcommand
The selection screen SHALL only be shown when the user explicitly runs `codemoo select`. It SHALL NOT appear on bare `codemoo` invocation.

#### Scenario: select subcommand shows the selection screen
- **WHEN** the user runs `codemoo select`
- **THEN** `SelectionApp` SHALL be displayed

#### Scenario: Bare invocation does not show the selection screen
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `SelectionApp` SHALL NOT be shown
