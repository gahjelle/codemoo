# Spec: approval-modal

## Purpose

TBD — Defines the `ApprovalModal` Textual widget that presents tool call approval requests to the user and returns a `GuardDecision`.

## Requirements

### Requirement: ApprovalModal is a Textual ModalScreen that returns a GuardDecision
`ApprovalModal` SHALL be a `ModalScreen[GuardDecision]` that accepts an `ApprovalRequest` and displays the proposed tool call. It SHALL dismiss with an `Approved()` or `Denied(...)` value when the user makes a choice. It SHALL block all interaction with the underlying chat UI until dismissed.

#### Scenario: Modal displays bot name and tool call
- **WHEN** `ApprovalModal` is shown with an `ApprovalRequest`
- **THEN** it SHALL display the bot's name and the formatted tool call signature

#### Scenario: Modal blocks the underlying UI
- **WHEN** the modal is active
- **THEN** the user SHALL NOT be able to interact with the chat input or log behind it

### Requirement: ApprovalModal offers three interaction paths
The modal SHALL present three choices: Approve, Deny, and Deny with reason.

- **Approve** button: dismisses immediately with `Approved()`
- **Deny** button: dismisses immediately with `Denied(reason=None)`
- **Deny with reason** button: transitions to a text input state

#### Scenario: Approve button dismisses with Approved
- **WHEN** the user clicks Approve
- **THEN** the modal SHALL dismiss with `Approved()`

#### Scenario: Deny button dismisses with plain Denied
- **WHEN** the user clicks Deny
- **THEN** the modal SHALL dismiss with `Denied(reason=None)`

#### Scenario: Deny with reason button reveals the reason input
- **WHEN** the user clicks Deny with reason
- **THEN** the Approve/Deny/Deny-with-reason buttons SHALL be hidden and a text input SHALL appear, focused and ready for input

### Requirement: Deny-with-reason state prompts with bot's name
When in the reason-input state, the modal SHALL display the prompt: `"What should {bot_name} do instead?"` where `{bot_name}` is the bot name from the `ApprovalRequest`.

#### Scenario: Reason prompt includes bot name
- **WHEN** the modal transitions to the reason-input state for a bot named "Cato"
- **THEN** the label SHALL read `"What should Cato do instead?"`

### Requirement: Submitting a reason dismisses with Denied(reason=...)
When in the reason-input state, pressing Enter (or clicking Send) SHALL dismiss the modal with `Denied(reason=<entered text>)`. If the input is empty, it SHALL behave identically to a plain Deny.

#### Scenario: Non-empty reason produces Denied with reason
- **WHEN** the user types "use archive/ instead" and submits
- **THEN** the modal SHALL dismiss with `Denied(reason="use archive/ instead")`

#### Scenario: Empty reason produces plain Denied
- **WHEN** the user submits an empty reason input
- **THEN** the modal SHALL dismiss with `Denied(reason=None)`

### Requirement: Tool call arguments are truncated in the modal display
The modal SHALL display tool arguments using `format_tool_call()` with `max_value_len=80`, ensuring long values (e.g. file content) do not overflow the layout.

#### Scenario: Long argument values are truncated with ellipsis
- **WHEN** a tool call has an argument value longer than 80 characters
- **THEN** the displayed value SHALL be truncated at 80 characters and end with `…`
