## Why

Gaia needs a user-facing chat interface to serve as the primary interaction surface for the agentic loop. This MVP establishes the core chat UI and a pluggable participant architecture so that both human users and code-based agents can exchange messages in a unified conversation.

## What Changes

- Add Textual as a runtime dependency for the terminal UI
- Add dev dependencies: ruff, ty, pytest
- Introduce a `ChatParticipant` protocol defining the interface for all chat actors
- Implement a `HumanParticipant` that reads input from the Textual UI
- Implement an `EchoBot` participant that echoes any message not sent by itself
- Build a Textual `ChatApp` that wires participants into a live chat session
- Wire `gaia` CLI entry point to launch the chat app

## Capabilities

### New Capabilities

- `chat-ui`: Terminal-based chat interface built with Textual, displaying messages and accepting human input
- `chat-participant`: Protocol and participant slot system enabling human and code-based actors to join a chat session
- `echo-bot`: Reference bot participant that echoes incoming messages back to the chat

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- **Dependencies**: `textual` added as runtime dep; `ruff`, `ty`, `pytest` added as dev deps via `uv`
- **Entry point**: `gaia` CLI (`src/gaia/__main__.py` or similar) launches the Textual chat app
- **New modules**: `src/gaia/chat/` package containing UI, participant protocol, and bot implementations
- **pyproject.toml**: Updated with new dependencies
