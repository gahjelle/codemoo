## MODIFIED Requirements

### Requirement: Slide content area introduces the current bot
The main area of the slide SHALL display the bot's name and type, a one-line description, and an LLM-generated explanation.

#### Scenario: Title shows bot name and type
- **WHEN** the slide for FileBot/Rune is shown
- **THEN** the content area SHALL display "Meet Rune, a FileBot" as the title

#### Scenario: Description is a hard-coded one-liner
- **WHEN** any slide is shown
- **THEN** a one-sentence description for the bot's type SHALL appear below the title

#### Scenario: What's new section for first bot
- **WHEN** the slide is shown for the first bot in the session (index 0)
- **THEN** the "what's new" section SHALL explain how this bot works, formatted as Markdown with at least one fenced code block showing a key line of code

#### Scenario: What's new section for subsequent bots
- **WHEN** the slide is shown for any bot after the first (index > 0)
- **THEN** the "what's new" section SHALL explain the key code addition compared to the previous bot, formatted as Markdown with at least one fenced code block highlighting the key difference

#### Scenario: Loading indicator while LLM generates content
- **WHEN** the slide is first displayed and the LLM explanation has not yet been received
- **THEN** the "what's new" area SHALL show a loading indicator (e.g. "Generating…")

#### Scenario: LLM content replaces loading indicator when ready
- **WHEN** the LLM finishes generating the explanation
- **THEN** the loading indicator SHALL be replaced by the generated Markdown text, rendered as rich text

#### Scenario: OK button is always enabled
- **WHEN** the LLM explanation is still loading
- **THEN** the OK button SHALL still be clickable and dismiss the slide
