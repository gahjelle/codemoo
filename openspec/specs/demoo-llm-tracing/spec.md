# Spec: demoo-llm-tracing

## Purpose

TBD — Defines the tracing output for the `demoo llm` command, which displays the endpoint URL, request payload, full API response, and final markdown reply in the terminal.

## Requirements

### Requirement: demoo llm traces endpoint URL, request payload, response, and final reply
The `demoo llm` command SHALL pass a `RichTracer` to `resolve_backend()`. Before displaying the final reply it SHALL print, in order: a "Request" rule, the endpoint URL in cyan, the JSON request payload syntax-highlighted in blue, a "Response" rule, the full JSON response syntax-highlighted in green, a "Reply" rule, and the markdown-rendered reply. Each section SHALL be delimited by a `console.rule()` with a descriptive label.

#### Scenario: Full trace output for a simple LLM call
- **WHEN** `demoo llm "What is 2+2?"` is run with the Anthropic backend
- **THEN** the terminal SHALL show a "Request" rule, `POST https://api.anthropic.com/v1/messages` in cyan, the JSON payload with `model`, `system`, `messages`, a "Response" rule, the full API response JSON, a "Reply" rule, and the markdown reply

#### Scenario: OpenAI-like backend shows system in messages list
- **WHEN** `demoo llm "..."` is run with an OpenAI-like backend (e.g. Ollama)
- **THEN** the request payload SHALL contain `messages` with a `{"role": "system", ...}` entry and SHALL NOT have a top-level `"system"` key
