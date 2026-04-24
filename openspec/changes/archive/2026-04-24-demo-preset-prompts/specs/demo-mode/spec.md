## ADDED Requirements

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
