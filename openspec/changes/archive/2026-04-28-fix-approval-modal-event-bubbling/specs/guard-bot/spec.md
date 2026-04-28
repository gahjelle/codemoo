## MODIFIED Requirements

### Requirement: GuardBot acts on GuardDecision correctly
`GuardBot` SHALL handle all `GuardDecision` variants:
- `Approved` → execute the tool, use real output
- `Denied(reason=None)` → skip execution, use `"The user denied this tool call. Do not attempt it again — move on to the next step."` as tool output
- `Denied(reason=str)` → skip execution, use `f"Tool call denied: {reason}"` as tool output

The tool loop SHALL continue in all cases, sending the tool output back to the LLM.

#### Scenario: Approved decision runs the tool
- **WHEN** `_ask_fn` returns `Approved()`
- **THEN** the tool function SHALL be called and its output used in the follow-up LLM message

#### Scenario: Plain deny produces a firm denial message
- **WHEN** `_ask_fn` returns `Denied(reason=None)`
- **THEN** `"The user denied this tool call. Do not attempt it again — move on to the next step."` SHALL be used as the tool result

#### Scenario: Deny with reason includes the user's instruction
- **WHEN** `_ask_fn` returns `Denied(reason="use archive/ instead")`
- **THEN** `"Tool call denied: use archive/ instead"` SHALL be used as the tool result
