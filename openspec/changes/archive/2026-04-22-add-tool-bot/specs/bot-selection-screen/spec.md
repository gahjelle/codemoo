# Spec: bot-selection-screen (delta)

## MODIFIED Requirements

### Requirement: Selection screen presents all available bots in a fixed order
The startup selection screen SHALL display a multi-select list of all available bot participants. The bots SHALL appear in the fixed order: EchoBot, LLMBot, ChatBot, SystemBot, ToolBot. Each item in the list SHALL show both the instance name and the bot type (e.g. "Mistral (LLMBot)").

#### Scenario: Bots appear in fixed order
- **WHEN** the selection screen is rendered
- **THEN** the list SHALL show EchoBot first, LLMBot second, ChatBot third, SystemBot fourth, and ToolBot fifth, regardless of the order they were passed to the screen

#### Scenario: Each item shows name and type
- **WHEN** a bot named "Mistral" of type `LLMBot` is in the available list
- **THEN** its list entry SHALL display text containing both "Mistral" and "LLMBot"
