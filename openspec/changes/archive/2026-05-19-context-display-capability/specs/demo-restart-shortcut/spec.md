## MODIFIED Requirements

### Requirement: Ctrl-R restarts the current bot session in any ChatApp session
Pressing Ctrl-R SHALL reset the current bot session in any `ChatApp` session (demo or non-demo). The reset SHALL clear conversation history, re-run `startup()` for bots that define it, and mount a visual divider in the log. In demo mode only, Ctrl-R SHALL additionally reset the preset prompt index and update `DemoHeader`. In non-demo mode, those two steps are skipped.

#### Scenario: Ctrl-R clears conversation history in any session
- **WHEN** the user sends several messages and then presses Ctrl-R (demo or non-demo mode)
- **THEN** `ChatApp._chat_context` SHALL be an empty list
- **AND** the next message SHALL be processed as if no prior conversation occurred

#### Scenario: Ctrl-R resets the preset prompt index in demo mode only
- **WHEN** the user has consumed two preset prompts via Ctrl-E and then presses Ctrl-R in demo mode
- **THEN** `_prompt_index` SHALL be reset to 0
- **AND** `DemoHeader` SHALL show the full original prompt count as remaining

#### Scenario: Ctrl-R does not update DemoHeader outside demo mode
- **WHEN** `ChatApp` is launched without a `demo_context` and the user presses Ctrl-R
- **THEN** `DemoHeader.update_prompt_state` SHALL NOT be called

#### Scenario: Ctrl-R re-runs startup for bots with a startup method
- **WHEN** the user presses Ctrl-R while a `ProjectBot` or `MemoryBot` is active
- **THEN** `startup()` SHALL be called again via `run_worker`
- **AND** the bot's `context` and/or `memory` fields SHALL reflect any on-disk changes since the last load

### Requirement: Ctrl-R mounts a static divider in the chat log
When Ctrl-R is pressed in any session, a `Label` widget with CSS class `restart-divider` SHALL be synchronously mounted in the `#log` `VerticalScroll`. The prior conversation bubbles SHALL remain visible above the divider.

#### Scenario: Divider appears immediately on Ctrl-R
- **WHEN** the user presses Ctrl-R
- **THEN** a `restart-divider` widget SHALL appear in the log before any async work begins

#### Scenario: Prior messages remain visible above the divider
- **WHEN** the user presses Ctrl-R after a conversation
- **THEN** all prior chat bubbles SHALL still be visible above the divider in the log

### Requirement: DemoHeader displays the Ctrl-R hint in demo mode
The `DemoHeader` hint line SHALL include the text "Ctrl-R: restart" alongside the existing Ctrl-N, Ctrl-S, and Ctrl-E hints.

#### Scenario: Ctrl-R hint visible in demo header
- **WHEN** `ChatApp` is launched in demo mode
- **THEN** the `DemoHeader` rendered text SHALL contain "Ctrl-R"
