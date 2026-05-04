# Spec: demoo-tool-tracing

## Purpose

TBD — Defines the tracing output for the `demoo tool` command, which shows both LLM round-trips, the tool call section, and the tool result section in the terminal.

## Requirements

### Requirement: demoo tool runs with a default system prompt overridable via --system
The `tool` command SHALL default to the system message `"You are a helpful assistant with access to file tools."` and SHALL accept an optional `--system` CLI option that replaces it. The resolved system message SHALL be included as the first message in every `complete()` call.

#### Scenario: Default system prompt used when --system is not provided
- **WHEN** `demoo tool "Read demo/greeter.py"` is run without `--system`
- **THEN** the request payload SHALL include `"You are a helpful assistant with access to file tools."` as the system prompt

#### Scenario: --system overrides the default system prompt
- **WHEN** `demoo tool "Read demo/greeter.py" --system "You are a code reviewer."`
- **THEN** the payload SHALL include `"You are a code reviewer."` as the system prompt and SHALL NOT include the default prompt

### Requirement: demoo tool traces two LLM round-trips and the tool call/result between them
The `demoo tool` command SHALL trace both LLM calls (request + response) and also print a "Tool Call" section and a "Tool Result" section between the two LLM round-trips. The "Tool Call" section SHALL show the tool name, call ID, and arguments. The "Tool Result" section SHALL show the call ID and the tool output. All sections SHALL be delimited by labeled `console.rule()` calls. The final "Reply" section renders markdown as before.

#### Scenario: Full trace for a tool-using query
- **WHEN** `demoo tool "Read the file demo/greeter.py"` is run
- **THEN** the terminal SHALL show in order: "Request" rule + payload, "Response" rule + response JSON (containing tool call), "Tool Call" rule + tool name + call ID + arguments, "Tool Result" rule + call ID + output, "Request" rule + second payload (with tool result), "Response" rule + second response JSON, "Reply" rule + markdown

#### Scenario: Call ID links tool call to tool result
- **WHEN** the "Tool Call" and "Tool Result" sections are printed
- **THEN** both SHALL display the same call ID string so the audience can see the correlation

#### Scenario: No tool call falls back to single round-trip trace
- **WHEN** the LLM responds without requesting a tool
- **THEN** only one "Request" and one "Response" section SHALL appear, followed by the "Reply"
