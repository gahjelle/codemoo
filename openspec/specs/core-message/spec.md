# Spec: core-message

## Purpose

TBD — Defines the requirements for the `codaroo.core` package containing pure types and protocols with no UI dependencies.

## Requirements

### Requirement: Core types reside in a dedicated pure package
The system SHALL provide a `codaroo.core` package containing only pure types and protocols: `ChatMessage`, `ChatParticipant`, `HumanParticipant`, and `EchoBot`. This package SHALL NOT import from `codaroo.chat` or any UI framework.

#### Scenario: Core package has no UI imports
- **WHEN** any module in `codaroo.core` is imported
- **THEN** no Textual or other UI framework module SHALL be transitively imported
