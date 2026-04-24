# Spec: structured-tool-def

## Purpose

TBD — Defines the structured `ToolParam` and `ToolDef` dataclasses and the per-backend `_tool_schema` converter that replaces the raw `schema: dict` field.

## Requirements

### Requirement: ToolParam is a dataclass describing one tool parameter
The `tools` module SHALL export a `ToolParam` dataclass with fields `name: str`, `description: str`, `type: str = "string"`, and `required: bool = True`. It SHALL be used to describe individual parameters within a `ToolDef`.

#### Scenario: ToolParam can be constructed with name and description only
- **WHEN** a `ToolParam` is constructed with only `name` and `description`
- **THEN** `type` SHALL default to `"string"` and `required` SHALL default to `True`

#### Scenario: ToolParam accepts non-string types
- **WHEN** a `ToolParam` is constructed with `type="integer"`
- **THEN** the `type` field SHALL hold `"integer"`

### Requirement: ToolDef has first-class name, description, and parameters fields
The `ToolDef` dataclass SHALL have fields `name: str`, `description: str`, `parameters: list[ToolParam]`, and `fn: Callable[..., str]`. The `schema: dict` field SHALL be removed.

#### Scenario: ToolDef exposes name directly
- **WHEN** a `ToolDef` is accessed via `tool.name`
- **THEN** it SHALL return the tool's name string without any dict traversal

#### Scenario: ToolDef can be constructed with all fields
- **WHEN** a `ToolDef` is constructed with `name`, `description`, `parameters`, and `fn`
- **THEN** all fields SHALL be accessible as attributes

### Requirement: Each backend module provides a _tool_schema converter function
Each backend module (`llm/mistral.py`, `llm/anthropic.py`, `llm/openrouter.py`) SHALL provide a module-private `_tool_schema(tool: ToolDef) -> dict` function that converts a `ToolDef` to the wire format expected by that provider. Mistral and OpenRouter SHALL use the OpenAI function-calling shape; Anthropic SHALL use the Anthropic tool shape with `input_schema`.

#### Scenario: Mistral/OpenRouter converter produces OpenAI function schema
- **WHEN** `_tool_schema(tool)` is called in `llm/mistral.py` or `llm/openrouter.py`
- **THEN** the result SHALL be a dict with `"type": "function"` and a nested `"function"` block containing `"name"`, `"description"`, and `"parameters"`

#### Scenario: Anthropic converter produces Anthropic tool schema
- **WHEN** `_tool_schema(tool)` is called in `llm/anthropic.py`
- **THEN** the result SHALL be a dict with top-level `"name"`, `"description"`, and `"input_schema"` keys (no `"type": "function"` wrapper)

### Requirement: All existing tools are rewritten using ToolParam and structured ToolDef
The four built-in tools (`read_file`, `write_file`, `reverse_string`, `run_shell`) SHALL be rewritten using the new `ToolDef` and `ToolParam` dataclasses. Their callable behavior SHALL be unchanged.

#### Scenario: read_file tool has structured definition
- **WHEN** `read_file` is inspected
- **THEN** `read_file.name` SHALL be `"read_file"` and `read_file.parameters` SHALL be a list containing one `ToolParam` with `name="path"`
