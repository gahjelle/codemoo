# Spec: demo-mode

## Purpose

TBD — defines the demo-mode behaviour of the application, where a progression of bots is shown one at a time and the user can advance through them with Ctrl-N.

## Requirements

### Requirement: Ctrl-N advances to the next bot in demo mode
While in a demo-mode `ChatApp` session, pressing Ctrl-N SHALL end the current session and start a fresh `ChatApp` with the next bot in the progression.

#### Scenario: Ctrl-N transitions to the next bot
- **WHEN** the user presses Ctrl-N during a demo session that is not on the last bot
- **THEN** the current `ChatApp` SHALL close and a new `ChatApp` SHALL open with the next bot in the progression

#### Scenario: Ctrl-N on the last bot exits the application
- **WHEN** the user presses Ctrl-N during a demo session on the last bot
- **THEN** the application SHALL exit cleanly

#### Scenario: Ctrl-N is not active outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot` (not demo mode)
- **THEN** pressing Ctrl-N SHALL have no effect

### Requirement: Each bot transition starts with a fresh chat history
When Ctrl-N advances to the next bot, the new session SHALL start with an empty message history.

#### Scenario: History cleared on transition
- **WHEN** the user sends several messages and then presses Ctrl-N
- **THEN** the new bot's `ChatApp` SHALL display an empty log with no prior messages

### Requirement: Demo mode shows a header identifying the current bot and position
When `ChatApp` is running in demo mode, a header bar SHALL be visible at the top of the screen showing the current bot's emoji, name, type, position in the **session's filtered bot list**, and the Ctrl-N keyboard hint.

#### Scenario: Header is visible in demo mode
- **WHEN** `ChatApp` is launched in demo mode
- **THEN** a `DemoHeader` widget SHALL be visible above the chat log

#### Scenario: Header content reflects session list position
- **WHEN** demo is started with `--start rune` and Rune is the first bot shown
- **THEN** the header SHALL display "1 of 3" (not "6 of 8")

#### Scenario: Header updates on transition
- **WHEN** the user advances from the first to the second bot in the session
- **THEN** the new `ChatApp`'s header SHALL show "2 of N" where N is the session bot count

#### Scenario: No header outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot`
- **THEN** the `DemoHeader` widget SHALL NOT be present in the widget tree

### Requirement: Demo mode operates on a filtered bot list based on --script, --start, and --end
The demo SHALL build its session bot list in three steps: (1) resolve the named script to an ordered `list[BotType]`; (2) instantiate those bots via `make_bots()`; (3) apply `--start` and `--end` to slice the list. All position numbering, header display, and bot comparisons SHALL use the final sliced list exclusively.

#### Scenario: --script alone filters the bot list
- **WHEN** demo is started with `--script focused` and `focused = ["LlmBot", "ChatBot", "AgentBot"]`
- **THEN** the demo session SHALL contain exactly [LlmBot, ChatBot, AgentBot]

#### Scenario: --start and --end combine with --script
- **WHEN** demo is started with `--script focused --end ChatBot` and `focused = ["LlmBot", "ChatBot", "AgentBot"]`
- **THEN** the demo session SHALL contain exactly [LlmBot, ChatBot]

#### Scenario: Numerical index for --start and --end is script-relative
- **WHEN** `focused = ["LlmBot", "ChatBot", "AgentBot"]` and demo is started with `--script focused --end 2`
- **THEN** `--end 2` SHALL resolve to `ChatBot` (the 2nd bot in the focused list) and the session SHALL contain [LlmBot, ChatBot]

#### Scenario: Bot not in script raises a descriptive error
- **WHEN** demo is started with `--script focused --end EchoBot` and `EchoBot` is not in the `focused` script
- **THEN** the application SHALL exit with a descriptive error message naming the bots that are valid within that script

#### Scenario: No --script uses the "default" script
- **WHEN** demo is started without `--script`
- **THEN** the demo session SHALL use the `"default"` script, which contains all bots in the standard order

#### Scenario: No --start and no --end uses the full script list
- **WHEN** demo is started with `--script focused` and neither `--start` nor `--end` is provided
- **THEN** the demo session SHALL contain all bots in the focused list from the first to the last

#### Scenario: --start slices from the given bot onward within the script
- **WHEN** demo is started with `--script focused --start ChatBot` and `focused = ["LlmBot", "ChatBot", "AgentBot"]`
- **THEN** the demo session SHALL contain [ChatBot, AgentBot]

#### Scenario: --end is inclusive
- **WHEN** demo is started with `--end AgentBot` on the default script
- **THEN** the session SHALL include AgentBot as the last bot

### Requirement: Demo mode bot transitions reuse the same asyncio event loop
When advancing through the bot progression in demo mode, all `ChatApp` instances SHALL share a single asyncio event loop. The demo runner SHALL use `asyncio.run()` once at the outer level and `ChatApp.run_async()` for each iteration, so that shared async resources (e.g. the LLM backend's HTTP client) remain valid across transitions.

#### Scenario: First message after Ctrl-N succeeds without event loop error
- **WHEN** the user presses Ctrl-N to advance to the next bot and immediately sends a message
- **THEN** the bot SHALL respond successfully and no "event loop is closed" error SHALL occur

#### Scenario: Shared backend is valid after bot transition
- **WHEN** the user switches bots via Ctrl-N and the new bot makes an LLM API call
- **THEN** the API call SHALL succeed on the first attempt without requiring a retry

### Requirement: DemoHeader is reactive and updates when prompt count changes
The `DemoHeader` widget SHALL store its display data as instance fields and expose an `update_prompt_state(remaining: int)` method. Calling this method SHALL update the header text immediately without reconstructing the widget.

#### Scenario: update_prompt_state reflects the new count
- **WHEN** `header.update_prompt_state(1)` is called
- **THEN** `str(header.render())` SHALL reflect one remaining prompt

#### Scenario: update_prompt_state(0) shows exhaustion state
- **WHEN** `header.update_prompt_state(0)` is called
- **THEN** `str(header.render())` SHALL indicate no more examples remain

### Requirement: DemoHeader includes the Ctrl-E hint when prompts are available
When constructed with a non-zero total prompt count, `DemoHeader` SHALL include "Ctrl-E" in its rendered text.

#### Scenario: Ctrl-E hint present when prompts configured
- **WHEN** `DemoHeader` is constructed with a bot that has 2 prompts
- **THEN** `str(header.render())` SHALL contain "Ctrl-E"

#### Scenario: No Ctrl-E hint when no prompts configured
- **WHEN** `DemoHeader` is constructed with a bot that has 0 prompts
- **THEN** `str(header.render())` SHALL NOT contain "Ctrl-E"

### Requirement: Ctrl-S reopens the current bot's slide in demo mode
While in a demo-mode `ChatApp` session, pressing Ctrl-S SHALL reopen the current bot's `SlideScreen` as a modal overlay. The chat log and input state SHALL be preserved while the modal is visible and restored when it is dismissed.

#### Scenario: Ctrl-S opens the slide mid-chat
- **WHEN** the user presses Ctrl-S during an active demo session
- **THEN** a `SlideScreen` for the current bot SHALL be pushed as a modal overlay on top of the chat

#### Scenario: Ctrl-S does not clear chat history
- **WHEN** the user sends several messages, presses Ctrl-S, and dismisses the slide
- **THEN** all prior chat bubbles SHALL still be visible in the log

#### Scenario: Ctrl-S is a no-op when a SlideScreen is already visible
- **WHEN** a `SlideScreen` is already displayed and the user presses Ctrl-S
- **THEN** no additional modal SHALL be pushed

#### Scenario: Ctrl-S is not active outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot` (not demo mode)
- **THEN** pressing Ctrl-S SHALL have no effect
