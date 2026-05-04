## ADDED Requirements

### Requirement: demoo agent runs a full tool loop until the LLM returns plain text
The `demoo agent` command SHALL accept a query string and run a `while True` loop that calls `llm.complete(messages, tools)` and, when the response is a `ToolUse`, executes the tool, appends both the assistant message and the tool result to context, and continues. When the LLM returns a plain string, the loop SHALL exit and the string SHALL be rendered as Markdown.

#### Scenario: Agent resolves a query that requires multiple tool calls
- **WHEN** `demoo agent "List Python files then read the first one"` is run
- **THEN** the loop SHALL execute at least two tool calls before producing a final reply, and the terminal SHALL show each round numbered

#### Scenario: Agent resolves a query requiring no tool calls
- **WHEN** `demoo agent "What is the capital of France?"` is run
- **THEN** the loop SHALL complete in round 1 with no tool calls, and the reply SHALL appear after a single Request + Response trace

### Requirement: demoo agent exposes read_file, write_file, list_files, and run_shell
The tools available to `demoo agent` SHALL be exactly `["read_file", "write_file", "list_files", "run_shell"]` sourced from `TOOL_REGISTRY`. No other tools SHALL be passed to the LLM.

#### Scenario: Tool registry lookup for agent tools
- **WHEN** the `agent` command initializes
- **THEN** it SHALL look up each of the four tool names from `TOOL_REGISTRY` and pass the resulting `ToolDef` list to `llm.complete()`

### Requirement: demoo agent traces each round with a round number label
Each iteration of the tool loop SHALL produce console sections labeled "Round N · Request", "Round N · Response", and (when a tool is called) "Round N · Tool Call" and "Round N · Tool Result", where N is the 1-based iteration index. The final "Reply" section SHALL have no round number.

#### Scenario: Round labels increment correctly
- **WHEN** the agent loop executes three rounds before producing a reply
- **THEN** the terminal SHALL show rules labeled "Round 1 · Request", "Round 1 · Response", "Round 1 · Tool Call", "Round 1 · Tool Result", "Round 2 · Request", ..., "Round 3 · Response", "Reply"

### Requirement: demoo agent traces tool calls and results with call IDs
When the LLM returns a `ToolUse`, the `agent` command SHALL print a "Round N · Tool Call" section showing the tool name, call ID, and arguments (as formatted JSON), and after executing the tool SHALL print a "Round N · Tool Result" section showing the call ID and tool output.

#### Scenario: Tool call section content
- **WHEN** the LLM calls `read_file` with `{"path": "demo/greeter.py"}` and call ID `call_abc123`
- **THEN** the "Round N · Tool Call" section SHALL display `read_file`, `call_abc123`, and the arguments JSON

#### Scenario: Tool result section links back to call ID
- **WHEN** the tool result is printed
- **THEN** it SHALL display the same call ID `call_abc123` and the string output of the tool

### Requirement: demoo agent runs with a default system prompt overridable via --system
The `agent` command SHALL default to the system message `"You are a helpful assistant with access to file and shell tools."` and SHALL accept an optional `--system` CLI option that replaces it. The resolved system message SHALL be the first `Message(role="system", ...)` in every `complete()` call.

#### Scenario: Default system prompt used when --system is not provided
- **WHEN** `demoo agent "List files"` is run without `--system`
- **THEN** the payload SHALL include `"You are a helpful assistant with access to file and shell tools."` as the system prompt

#### Scenario: --system overrides the default system prompt
- **WHEN** `demoo agent "List files" --system "You are a file explorer."`
- **THEN** the payload SHALL include `"You are a file explorer."` as the system prompt and SHALL NOT include the default prompt
