## MODIFIED Requirements

### Requirement: approval.py is the canonical home of the approval gate data model
A module `core/approval.py` SHALL export the complete approval gate
vocabulary: `Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`,
`_denial_message`, and `_async_approved`. No other module SHALL define these
types independently.

`Approved` SHALL be a frozen dataclass with no fields.
`Denied` SHALL be a frozen dataclass with one field: `reason: str | None = None`.
`GuardDecision` SHALL be the type alias `Approved | Denied`.
`ApprovalRequest` SHALL be a frozen dataclass with fields `bot_name: str` and
`tool_use: ToolUse`.
`_denial_message` SHALL be a pure function `(Denied) -> str` returning the
appropriate denial string.
`_async_approved` SHALL be an async function `(ApprovalRequest) -> GuardDecision`
that always returns `Approved()`.

#### Scenario: approval.py can be imported without side effects
- **WHEN** `from codemoo.core.approval import Approved, Denied, GuardDecision, ApprovalRequest` is executed
- **THEN** all four names SHALL be importable and no side effects SHALL occur

#### Scenario: _denial_message returns reason when present
- **WHEN** `_denial_message(Denied(reason="use archive/ instead"))` is called
- **THEN** it SHALL return `"Tool call denied: use archive/ instead"`

#### Scenario: _denial_message returns default when reason is None
- **WHEN** `_denial_message(Denied(reason=None))` is called
- **THEN** it SHALL return `"The user denied this tool call. Do not attempt it again — move on to the next step."`

#### Scenario: _async_approved always approves
- **WHEN** `await _async_approved(any_request)` is called
- **THEN** it SHALL return an `Approved` instance
