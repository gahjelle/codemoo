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
The modal SHALL present three choices in this order: Yes, No but with reason, and No.

- **Yes** button (`id="approve"`, `variant="success"`): dismisses immediately with `Approved()`
- **No, but …** button (`id="deny-reason"`, `variant="warning"`): transitions to a text input state
- **No** button (`id="deny"`, `variant="error"`): dismisses immediately with `Denied(reason=None)`

The button order and variants SHALL follow the traffic-light metaphor: green (proceed) / yellow (proceed with caveat) / red (stop).

#### Scenario: Approve button dismisses with Approved
- **WHEN** the user clicks Yes
- **THEN** the modal SHALL dismiss with `Approved()`

#### Scenario: Deny button dismisses with plain Denied
- **WHEN** the user clicks No
- **THEN** the modal SHALL dismiss with `Denied(reason=None)`

#### Scenario: Deny with reason button reveals the reason input
- **WHEN** the user clicks No, but …
- **THEN** the Yes / No, but … / No buttons SHALL be hidden and a text input SHALL appear, focused and ready for input

#### Scenario: Buttons appear in traffic-light order
- **WHEN** the modal is displayed
- **THEN** the buttons SHALL appear left-to-right as: Yes (green) / No, but … (yellow) / No (red)

### Requirement: Left and right arrow keys move focus between buttons
While the button row is visible, the left and right arrow keys SHALL move focus between the three buttons, wrapping at each end. Tab SHALL continue to work as before.

#### Scenario: Right arrow moves focus to the next button
- **WHEN** a button has focus and the user presses the right arrow key
- **THEN** focus SHALL move to the next button to the right, wrapping from No back to Yes

#### Scenario: Left arrow moves focus to the previous button
- **WHEN** a button has focus and the user presses the left arrow key
- **THEN** focus SHALL move to the next button to the left, wrapping from Yes back to No

### Requirement: Deny-with-reason state prompts with bot's name
When in the reason-input state, the modal SHALL display the prompt: `"What should {bot_name} do instead?"` where `{bot_name}` is the bot name from the `ApprovalRequest`.

#### Scenario: Reason prompt includes bot name
- **WHEN** the modal transitions to the reason-input state for a bot named "Cato"
- **THEN** the label SHALL read `"What should Cato do instead?"`

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

### Requirement: Tool call arguments are truncated in the modal display
The modal SHALL display tool arguments using `format_tool_call()` with `max_value_len=80`, ensuring long values (e.g. file content) do not overflow the layout.

#### Scenario: Long argument values are truncated with ellipsis
- **WHEN** a tool call has an argument value longer than 80 characters
- **THEN** the displayed value SHALL be truncated at 80 characters and end with `…`
