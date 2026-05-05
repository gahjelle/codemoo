## ADDED Requirements

### Requirement: List Gmail messages
The system SHALL provide a tool to list recent Gmail messages with sender, subject, and date.

#### Scenario: List inbox messages
- **WHEN** list_gmail tool is called
- **THEN** system returns up to 10 most recent messages from inbox
- **AND** each message shows date, sender email, and subject line

#### Scenario: Limit message count
- **WHEN** list_gmail tool is called with top parameter
- **THEN** system returns at most the specified number of messages

### Requirement: Read Gmail message content
The system SHALL provide a tool to read the body content of a Gmail message identified by subject keyword.

#### Scenario: Read message by subject keyword
- **WHEN** read_gmail tool is called with subject_keyword
- **THEN** system returns the first matching message's full body content
- **AND** response includes sender and subject headers

#### Scenario: No matching message
- **WHEN** read_gmail tool is called with non-matching keyword
- **THEN** system returns error message indicating no match found

### Requirement: Send Gmail message
The system SHALL provide a tool to send an email via Gmail.

#### Scenario: Send email
- **WHEN** send_gmail tool is called with recipient, subject, and body
- **THEN** system sends email via Gmail API
- **AND** system returns success confirmation

#### Scenario: Invalid recipient
- **WHEN** send_gmail tool is called with invalid recipient format
- **THEN** system returns error indicating invalid address

### Requirement: Gmail body extraction handles multipart
The system SHALL correctly extract text content from Gmail's multipart MIME messages.

#### Scenario: Plain text message
- **WHEN** message contains only text/plain part
- **THEN** system returns decoded plain text body

#### Scenario: Multipart message
- **WHEN** message contains both text/plain and text/html parts
- **THEN** system returns text/plain content preferentially
