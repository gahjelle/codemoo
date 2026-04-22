# Spec: run-shell-tool

## Purpose

Defines the `run_shell` tool, a `ToolDef` that executes arbitrary shell commands via `subprocess.run` and returns a formatted result string containing exit code, stdout, and stderr. Used by `ShellBot` to give the LLM the ability to run commands on demand.

## Requirements

### Requirement: run_shell executes a shell command and returns its output
`run_shell` SHALL be a `ToolDef` whose `fn` accepts a `command: str` argument, runs it via `subprocess.run` with `shell=True`, captures stdout and stderr, and returns a formatted string containing the exit code, stdout, and stderr.

#### Scenario: Successful command returns stdout
- **WHEN** `run_shell.fn(command="echo hello")` is called
- **THEN** the returned string SHALL contain `"hello"` and indicate exit code 0

#### Scenario: Failing command returns stderr and non-zero exit code
- **WHEN** `run_shell.fn(command="false")` is called (a command that exits with code 1)
- **THEN** the returned string SHALL indicate a non-zero exit code, and SHALL NOT raise an exception

#### Scenario: Timeout is enforced
- **WHEN** a command runs longer than the configured timeout (default 30 s)
- **THEN** `run_shell.fn` SHALL return a string indicating the timeout rather than blocking indefinitely

### Requirement: run_shell has a valid JSON schema for LLM tool use
`run_shell.schema` SHALL follow the OpenAI function-calling format with `type: "function"`, a `name` of `"run_shell"`, a description, and a `command` parameter of type `string`.

#### Scenario: Schema top-level fields are correct
- **WHEN** `run_shell.schema` is inspected
- **THEN** it SHALL have `type == "function"`, `function.name == "run_shell"`, a non-empty description, and `parameters.required == ["command"]`
