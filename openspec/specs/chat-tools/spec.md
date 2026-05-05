# Spec: chat-tools

## Purpose

TBD — defines the Google Chat tool implementations for posting messages to Google Chat spaces.

## Requirements

### Requirement: Post Google Chat message
The system SHALL provide a tool to post a message to a Google Chat space.

#### Scenario: Post to space
- **WHEN** post_chat_message tool is called with space ID and message text
- **THEN** system posts message to specified Google Chat space
- **AND** system returns confirmation

#### Scenario: Invalid space
- **WHEN** post_chat_message tool is called with non-existent space ID
- **THEN** system returns error indicating space not found

### Requirement: Chat message formatting
The system SHALL support plain text messages to Google Chat.

#### Scenario: Plain text message
- **WHEN** message contains no special formatting
- **THEN** system posts as plain text
