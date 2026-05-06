## MODIFIED Requirements

### Requirement: List Google Drive files
The system SHALL provide a `list_gdrive` tool that lists files in a given Google Drive folder and returns each file's name and ID.

#### Scenario: List files in root
- **WHEN** `list_gdrive` tool is called with no arguments
- **THEN** system returns files from the user's My Drive root
- **AND** each entry is formatted as `<name>  |  <id>`

#### Scenario: List files in a specific folder
- **WHEN** `list_gdrive` tool is called with a `folder_id` parameter
- **THEN** system returns files whose parent is that folder ID
- **AND** each entry is formatted as `<name>  |  <id>`

#### Scenario: Empty folder
- **WHEN** `list_gdrive` tool is called on a folder with no files
- **THEN** system returns "No files found"

#### Scenario: Drive API error
- **WHEN** the Drive API returns an error status
- **THEN** system returns `Error <status>: <message>`

### Requirement: Read Google Drive file content
The system SHALL provide a `read_gdrive` tool that downloads and returns the text content of a Drive file by its ID.

#### Scenario: Read a native Google Doc
- **WHEN** `read_gdrive` tool is called with the ID of a Google Docs file
- **AND** the file's mimeType is `application/vnd.google-apps.document`
- **THEN** system exports the file as `text/plain` and returns the content

#### Scenario: Read an uploaded text or Markdown file
- **WHEN** `read_gdrive` tool is called with the ID of a plain text or Markdown file
- **AND** the file's mimeType starts with `text/`
- **THEN** system downloads the file using the media endpoint and returns the content as UTF-8 text

#### Scenario: Unsupported MIME type
- **WHEN** `read_gdrive` tool is called with the ID of a non-text file (e.g., PDF, image)
- **THEN** system returns `"Unsupported file type: <mimeType>. Only Google Docs and text files are supported."`

#### Scenario: File not found
- **WHEN** `read_gdrive` tool is called with a non-existent file ID
- **THEN** system returns `Error 404: <message>`

### Requirement: Write Google Drive file
The system SHALL provide a `write_gdrive` tool that creates or updates a plain text file in Google Drive using multipart upload.

#### Scenario: Create new file
- **WHEN** `write_gdrive` tool is called with a filename and content
- **AND** no file with that name exists in the target folder
- **THEN** system creates the file in the target folder using a multipart POST to `/upload/drive/v3/files?uploadType=multipart`
- **AND** returns `"Created <filename> (<id>)"`

#### Scenario: Update existing file
- **WHEN** `write_gdrive` tool is called with a filename and content
- **AND** a file with that name exists in the target folder
- **THEN** system updates the file content using a multipart PATCH to `/upload/drive/v3/files/<id>?uploadType=multipart`
- **AND** returns `"Updated <filename> (<id>)"`

#### Scenario: Write to specific folder
- **WHEN** `write_gdrive` tool is called with an explicit `folder_id`
- **THEN** the created or updated file resides in that folder

#### Scenario: write_gdrive requires approval
- **WHEN** `write_gdrive` ToolDef is defined
- **THEN** `requires_approval` is set to `True`
- **AND** GuardBot and ProjectBot will prompt the user before executing it

#### Scenario: Drive API error on write
- **WHEN** the Drive API returns an error status during create or update
- **THEN** system returns `Error <status>: <message>`

## ADDED Requirements

### Requirement: Drive context source reads team context by filename
The system SHALL provide a private `_read_gdrive_by_name(filename)` function in `workspace/tools/read.py` that searches My Drive root for a file by name and returns its text content.

#### Scenario: File found by name
- **WHEN** `_read_gdrive_by_name("TEAM.md")` is called
- **AND** a file named "TEAM.md" exists in My Drive root
- **THEN** system returns the file's text content using the same MIME-type-aware logic as `read_gdrive`

#### Scenario: File not found by name
- **WHEN** `_read_gdrive_by_name("TEAM.md")` is called
- **AND** no file named "TEAM.md" exists in My Drive root
- **THEN** system returns `None`

#### Scenario: Multiple files with same name
- **WHEN** `_read_gdrive_by_name("TEAM.md")` is called
- **AND** multiple files share that name
- **THEN** system reads the most recently modified one
