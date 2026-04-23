## ADDED Requirements

### Requirement: Each bot type has a hard-coded one-liner description
A description string SHALL exist for every bot type used in the demo progression. These descriptions SHALL be stored in `slides_data.py` in the chat UI layer, not in the core bot classes.

#### Scenario: Description exists for all standard bot types
- **WHEN** the slide screen looks up the description for any of EchoBot, LLMBot, ChatBot, SystemBot, ToolBot, FileBot, ShellBot, or AgentBot
- **THEN** a non-empty string SHALL be returned

#### Scenario: Descriptions are not on bot classes
- **WHEN** any core bot class (EchoBot, LLMBot, etc.) is inspected
- **THEN** it SHALL NOT have a `description` attribute or any other demo-specific metadata

### Requirement: Each bot type has a curated source file list for LLM context
A mapping SHALL exist from each bot type to the source files that are most relevant for explaining that bot's implementation. This mapping SHALL be stored in `slides_data.py`.

#### Scenario: GeneralToolBot subclasses include the base class file
- **WHEN** the source file mapping is looked up for ToolBot, FileBot, or ShellBot
- **THEN** the result SHALL include both the bot's own source file and `general_tool_bot.py`

#### Scenario: Other bots list only their own file
- **WHEN** the source file mapping is looked up for EchoBot, LLMBot, ChatBot, SystemBot, or AgentBot
- **THEN** the result SHALL contain only that bot's own source file

#### Scenario: Runtime tools list supplements the source mapping
- **WHEN** building the LLM prompt for a bot that has a `.tools` attribute
- **THEN** the tool function names SHALL be included in the prompt context alongside the source files
