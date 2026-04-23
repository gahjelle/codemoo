## ADDED Requirements

### Requirement: Demo mode bot transitions reuse the same asyncio event loop
When advancing through the bot progression in demo mode, all `ChatApp` instances SHALL share a single asyncio event loop. The demo runner SHALL use `asyncio.run()` once at the outer level and `ChatApp.run_async()` for each iteration, so that shared async resources (e.g. the LLM backend's HTTP client) remain valid across transitions.

#### Scenario: First message after Ctrl-N succeeds without event loop error
- **WHEN** the user presses Ctrl-N to advance to the next bot and immediately sends a message
- **THEN** the bot SHALL respond successfully and no "event loop is closed" error SHALL occur

#### Scenario: Shared backend is valid after bot transition
- **WHEN** the user switches bots via Ctrl-N and the new bot makes an LLM API call
- **THEN** the API call SHALL succeed on the first attempt without requiring a retry
