## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Left and right arrow keys move focus between buttons
While the button row is visible, the left and right arrow keys SHALL move focus between the three buttons, wrapping at each end. Tab SHALL continue to work as before.

#### Scenario: Right arrow moves focus to the next button
- **WHEN** a button has focus and the user presses the right arrow key
- **THEN** focus SHALL move to the next button to the right, wrapping from No back to Yes

#### Scenario: Left arrow moves focus to the previous button
- **WHEN** a button has focus and the user presses the left arrow key
- **THEN** focus SHALL move to the next button to the left, wrapping from Yes back to No
