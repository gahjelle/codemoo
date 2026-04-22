# Spec: read-file-tool

## Purpose

TBD — Defines the `read_file` tool that enables LLM bots to read file contents by path.

## Requirements

### Requirement: read_file tool reads a file and returns its contents
The `tools` module SHALL export a `read_file` `ToolDef`. When invoked with a `path: str` argument, `fn` SHALL return the full text content of the file at that path.

#### Scenario: Existing file is read and returned
- **WHEN** `read_file.fn` is called with a valid path to an existing text file
- **THEN** it SHALL return the file's full text content as a string

#### Scenario: Non-existent file returns an error string
- **WHEN** `read_file.fn` is called with a path that does not exist
- **THEN** it SHALL return a descriptive error string (not raise an exception)

#### Scenario: Unreadable file returns an error string
- **WHEN** `read_file.fn` is called with a path that cannot be read (e.g., permission denied)
- **THEN** it SHALL return a descriptive error string (not raise an exception)

### Requirement: read_file schema is a valid JSON-schema function definition
The `read_file.schema` dict SHALL conform to the LLM tool-calling API format: it SHALL include `type: "function"`, a `name` field set to `"read_file"`, a `description` field, and a `parameters` object with `type: "object"`, a `properties` dict containing a `path` property with `type: "string"`, and a `required` list containing `"path"`.

#### Scenario: Schema contains required top-level fields
- **WHEN** `read_file.schema` is inspected
- **THEN** it SHALL have `type: "function"`, and the nested `function` object SHALL have `"name": "read_file"`, `"description"`, and `"parameters"` with `"path"` in `required`
