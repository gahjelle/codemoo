## MODIFIED Requirements

### Requirement: Slide LLM prompt includes bot instructions alongside source and tools
The `_build_llm_prompt()` function SHALL append the current bot's instructions to the LLM prompt when `resolved.instructions` is non-empty, using the same conditional-append pattern as the existing tools line. The same SHALL apply to the previous bot's instructions when building a comparison prompt.

#### Scenario: Instructions line appended when non-empty for current bot
- **WHEN** `_build_llm_prompt()` is called and `current_resolved.instructions` is non-empty
- **THEN** the prompt SHALL contain a line of the form `"{bot_name} instructions:\n{instructions_text}"`

#### Scenario: Instructions line omitted when empty for current bot
- **WHEN** `_build_llm_prompt()` is called and `current_resolved.instructions` is `""`
- **THEN** the prompt SHALL NOT contain an instructions line for the current bot

#### Scenario: Previous bot instructions included in comparison prompt
- **WHEN** `_build_llm_prompt()` is called with a non-None `prev_resolved` that has non-empty instructions
- **THEN** the prompt SHALL include the previous bot's instructions alongside its source and tools

#### Scenario: ChatBot to SystemBot comparison shows instructions contrast
- **WHEN** `_build_llm_prompt()` is called comparing a ChatBot (empty instructions) with a SystemBot (non-empty instructions)
- **THEN** the prompt SHALL show instructions for SystemBot and omit an instructions line for ChatBot
- **AND** the slide LLM can identify the system prompt as the key change
