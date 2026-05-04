## MODIFIED Requirements

### Requirement: ApprovalRequest carries the information needed to display the modal
`ApprovalRequest` SHALL be a frozen dataclass with fields `bot_name: str` and
`tool_use: ToolUse`. It SHALL be defined in `approval.py` (not `guard_bot.py`)
and used as the sole argument to `ask_fn`. All gated bots SHALL import it from
`codemoo.core.bots.approval`.

#### Scenario: ApprovalRequest fields are accessible
- **WHEN** an `ApprovalRequest` is constructed with a bot name and a ToolUse
- **THEN** `request.bot_name` and `request.tool_use` SHALL be accessible as attributes
