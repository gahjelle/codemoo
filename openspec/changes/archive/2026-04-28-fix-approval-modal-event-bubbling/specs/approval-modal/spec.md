## MODIFIED Requirements

### Requirement: Submitting a reason dismisses with Denied(reason=...)
When in the reason-input state, pressing Enter SHALL dismiss the modal with `Denied(reason=<entered text>)`. If the input is empty, it SHALL behave identically to a plain Deny. After dismissing, the modal SHALL stop the `Input.Submitted` event from propagating further, preventing the denial reason from being processed by any ancestor widget or screen.

#### Scenario: Non-empty reason produces Denied with reason
- **WHEN** the user types "use archive/ instead" and submits
- **THEN** the modal SHALL dismiss with `Denied(reason="use archive/ instead")`

#### Scenario: Empty reason produces plain Denied
- **WHEN** the user submits an empty reason input
- **THEN** the modal SHALL dismiss with `Denied(reason=None)`

#### Scenario: Reason submission does not propagate to parent screens
- **WHEN** the user submits a denial reason in the modal
- **THEN** the `Input.Submitted` event SHALL NOT reach any handler outside the modal
