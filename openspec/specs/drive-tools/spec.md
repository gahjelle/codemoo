# Spec: drive-tools

## Purpose

TBD — defines the Google Drive tool implementations for listing, reading, and writing files via the Google Drive API.

## Requirements

### Requirement: List Google Drive files
The system SHALL provide a tool to list files in the user's Google Drive.

#### Scenario: List root-level files
- **WHEN** list_drive tool is called
- **THEN** system returns files from the user's My Drive
- **AND** each file shows name and type

#### Scenario: Limit result count
- **WHEN** list_drive tool is called with top parameter
- **THEN** system returns at most that many files

### Requirement: Read Google Drive file content
The system SHALL provide a tool to download and return the text content of a Drive file.

#### Scenario: Read text file
- **WHEN** read_drive tool is called with file ID or name
- **THEN** system downloads and returns file content as text

#### Scenario: File not found
- **WHEN** read_drive tool is called with non-existent file name
- **THEN** system returns error indicating file not found

### Requirement: Write Google Drive file
The system SHALL provide a tool to create or update a file in Google Drive.

#### Scenario: Create new file
- **WHEN** write_drive tool is called with file name and content
- **THEN** system creates new file in user's Drive
- **AND** system returns file ID

#### Scenario: Update existing file
- **WHEN** write_drive tool is called with existing file name
- **THEN** system updates file content in place
