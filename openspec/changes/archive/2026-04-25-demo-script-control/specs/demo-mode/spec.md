## MODIFIED Requirements

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
