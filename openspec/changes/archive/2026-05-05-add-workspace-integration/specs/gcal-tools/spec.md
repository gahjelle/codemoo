## ADDED Requirements

### Requirement: List Google Calendar events
The system SHALL provide a tool to list upcoming calendar events within a configurable time range.

#### Scenario: List next 7 days of events
- **WHEN** list_gcal tool is called without parameters
- **THEN** system returns events for the next 7 days
- **AND** each event shows start time and subject

#### Scenario: Custom date range
- **WHEN** list_gcal tool is called with days parameter
- **THEN** system returns events for the specified number of days ahead

#### Scenario: No events in range
- **WHEN** no events exist in the specified range
- **THEN** system returns "No events found" message

### Requirement: Create Google Calendar event
The system SHALL provide a tool to create a new calendar event.

#### Scenario: Create single event
- **WHEN** create_gcal_event tool is called with summary, start, and end times
- **THEN** system creates event on primary calendar
- **AND** system returns confirmation with event ID

#### Scenario: All-day event
- **WHEN** create_gcal_event is called with date-only values
- **THEN** system creates all-day event spanning those dates
