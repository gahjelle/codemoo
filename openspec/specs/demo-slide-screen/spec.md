# Spec: demo-slide-screen

## Purpose

TBD — defines the slide overlay screen shown before each bot session in demo mode, introducing the current bot to the audience.

## Requirements

### Requirement: Slide screen is shown before each bot session in demo mode
When demo mode starts a new bot session, a `SlideScreen` SHALL be pushed as a modal overlay before the user can interact with the chat.

#### Scenario: Slide appears on first bot
- **WHEN** the demo starts with the first bot
- **THEN** a `SlideScreen` SHALL be displayed as a modal on top of the empty chat

#### Scenario: Slide appears on each subsequent bot
- **WHEN** the user advances to the next bot with Ctrl-N
- **THEN** a `SlideScreen` SHALL be displayed before the new chat session is interactive

#### Scenario: No slide screen outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot`
- **THEN** no `SlideScreen` SHALL be pushed

### Requirement: Slide screen has an Agenda column listing the session's bots
The left column of the slide SHALL list every bot in the current demo session (emoji and name only, no type), with visual distinction between past, current, and upcoming bots.

#### Scenario: Previous bots are dimmed
- **WHEN** the slide for bot N (N > 1) is shown
- **THEN** bots 1 through N-1 SHALL appear dimmed in the Agenda column

#### Scenario: Current bot is highlighted
- **WHEN** the slide for bot N is shown
- **THEN** bot N SHALL appear highlighted (bold or accent color) in the Agenda column

#### Scenario: Upcoming bots are normal
- **WHEN** the slide for bot N is shown
- **THEN** bots N+1 through the end SHALL appear in normal (non-dimmed, non-bold) style

#### Scenario: Agenda reflects filtered session list only
- **WHEN** demo is started with `--start rune` and the session bots are [Rune, Ash, Loom]
- **THEN** the Agenda SHALL list only Rune, Ash, and Loom — no earlier bots appear

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

### Requirement: Slide is dismissed by OK button, Enter, or Escape
The presenter SHALL be able to dismiss the slide and proceed to the chat via any of three interactions.

#### Scenario: OK button dismisses the slide
- **WHEN** the user clicks the OK button
- **THEN** the `SlideScreen` SHALL be dismissed and the chat becomes interactive

#### Scenario: Enter key dismisses the slide
- **WHEN** the user presses Enter
- **THEN** the `SlideScreen` SHALL be dismissed and the chat becomes interactive

#### Scenario: Escape key dismisses the slide
- **WHEN** the user presses Escape
- **THEN** the `SlideScreen` SHALL be dismissed and the chat becomes interactive

#### Scenario: OK button is always enabled
- **WHEN** the LLM explanation is still loading
- **THEN** the OK button SHALL still be clickable and dismiss the slide
