# Spec: tui-trace-modal

## Purpose

Defines `TraceModal` — a Textual `ModalScreen` that renders the LLM request/response traffic collected by `TraceStore` for the most recent turn. Supports both Anthropic and OpenAI wire formats and presents tool calls and tool results as distinct labelled sections.

## Requirements

### Requirement: TraceModal is a Textual ModalScreen that displays the last turn's LLM traffic
The system SHALL provide `TraceModal(ModalScreen)` in `codemoo/chat/trace_modal.py`. It SHALL accept a `TraceStore` at construction, render all entries in a `VerticalScroll` container, and dismiss when the user presses any key. An empty store SHALL render an empty box without error.

#### Scenario: Modal opens with empty store
- **WHEN** `TraceModal` is pushed with a store that has no entries
- **THEN** it SHALL display an empty scrollable area without raising an exception

#### Scenario: Modal dismisses on any key press
- **WHEN** the user presses any key while the modal is visible
- **THEN** the modal SHALL dismiss and the chat UI SHALL resume

### Requirement: Each trace entry is rendered as up to four labelled sections in order
For each `TraceEntry` in the store, `TraceModal` SHALL render sections in this order:

1. **TOOL RESULT** (conditional) — shown when the last message of the request payload is a tool result
2. **REQUEST** — always shown; header includes the HTTP method and URL
3. **RESPONSE** — always shown; the full response payload
4. **TOOL CALL** (conditional) — shown when the response contains a tool call

All JSON payloads SHALL be rendered with `json.dumps(data, indent=2)`. Long lines SHALL NOT be wrapped — they overflow off-screen to the right. The modal uses vertical scrolling only.

#### Scenario: REQUEST section is always rendered
- **WHEN** a `TraceEntry` exists with any request payload
- **THEN** a REQUEST section SHALL be shown with the URL and pretty-printed JSON

#### Scenario: RESPONSE section is always rendered
- **WHEN** a `TraceEntry` exists with a non-None response
- **THEN** a RESPONSE section SHALL be shown with pretty-printed JSON

#### Scenario: TOOL RESULT section appears before REQUEST when present
- **WHEN** the last message of the request payload is a tool result (Anthropic or OpenAI format)
- **THEN** the TOOL RESULT section SHALL appear above the REQUEST section for that entry

#### Scenario: TOOL CALL section appears after RESPONSE when present
- **WHEN** the response payload contains a tool call (Anthropic or OpenAI format)
- **THEN** the TOOL CALL section SHALL appear below the RESPONSE section for that entry

### Requirement: Tool call extraction supports both Anthropic and OpenAI wire formats
`TraceModal` SHALL detect the wire format by inspecting the top-level keys of the response payload: a `"content"` list indicates Anthropic format; a `"choices"` key indicates OpenAI-like format. Extraction SHALL follow the format-specific paths defined below.

**Anthropic tool call** (from response): `response["content"][i]` where `["type"] == "tool_use"` → name from `.name`, args from `.input` (already a dict).

**OpenAI tool call** (from response): `response["choices"][0]["message"]["tool_calls"][0]["function"]` → name from `.name`, args from `.arguments` (JSON string, requires `json.loads`).

**Anthropic tool result** (from last request message): last message where `content` is a list and `content[0]["type"] == "tool_result"` → display `.content`.

**OpenAI tool result** (from last request message): last message where `role == "tool"` → display `.content`.

Tool call display format: `tool_name(arg1="val1", arg2="val2")` with args rendered as `key=repr(value)` pairs joined by `", "`.

#### Scenario: Anthropic tool call is extracted and displayed
- **WHEN** the response payload has `"content"` and one item has `"type": "tool_use"`
- **THEN** the TOOL CALL section SHALL show `tool_name(...)` with the extracted arguments

#### Scenario: OpenAI tool call is extracted and displayed
- **WHEN** the response payload has `"choices"` and `choices[0]["message"]["tool_calls"]` is non-empty
- **THEN** the TOOL CALL section SHALL show `tool_name(...)` with the parsed arguments

#### Scenario: Anthropic tool result is extracted from request
- **WHEN** the last message of the request has a `content` list and `content[0]["type"] == "tool_result"`
- **THEN** the TOOL RESULT section SHALL display the content text

#### Scenario: OpenAI tool result is extracted from request
- **WHEN** the last message of the request has `role == "tool"`
- **THEN** the TOOL RESULT section SHALL display the content

#### Scenario: No tool call in response — TOOL CALL section is omitted
- **WHEN** the response payload contains no tool use items
- **THEN** no TOOL CALL section SHALL appear for that entry

### Requirement: TraceModal CSS follows the structural/visual split convention
Structural CSS (height, layout, scroll) SHALL be in `TraceModal.DEFAULT_CSS`. Visual CSS (colors, borders, padding) SHALL be in `chat.tcss`. `TraceModal` SHALL NOT hardcode colors or borders in `DEFAULT_CSS`.

#### Scenario: DEFAULT_CSS contains only layout properties
- **WHEN** `TraceModal.DEFAULT_CSS` is inspected
- **THEN** it SHALL contain only properties that affect layout and scroll behaviour (e.g. `height`, `width`, `layout`)
