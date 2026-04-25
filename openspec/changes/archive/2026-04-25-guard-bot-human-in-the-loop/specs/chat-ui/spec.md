## ADDED Requirements

### Requirement: ChatApp detects and wires guard-capable participants at startup
`ChatApp.__init__` SHALL iterate over participants and, for any participant with a `register_guard` attribute, call `participant.register_guard(ask_fn)` where `ask_fn` is a coroutine that shows the `ApprovalModal` and returns a `GuardDecision`. This check SHALL use `hasattr`, not `isinstance`, keeping `ChatApp` decoupled from `GuardBot`.

#### Scenario: GuardBot participant gets ask_fn wired automatically
- **WHEN** a `GuardBot` is included in the participants list
- **THEN** `ChatApp.__init__` SHALL call `guard_bot.register_guard(ask_fn)` before the first message

#### Scenario: Non-guard participants are unaffected
- **WHEN** participants do not have a `register_guard` attribute
- **THEN** `ChatApp.__init__` SHALL not raise any error and behaviour SHALL be unchanged

### Requirement: The guard ask_fn shows ApprovalModal and returns a GuardDecision
The `ask_fn` wired by `ChatApp` SHALL:
1. Create an `asyncio.Future[GuardDecision]`
2. Call `self.push_screen(ApprovalModal(request), on_dismiss=future.set_result)`
3. Await and return the future's result

The worker suspends at `await future` without blocking the Textual event loop. When the modal dismisses, Textual calls `future.set_result(decision)`, which resumes the worker.

#### Scenario: Worker suspends while modal is shown
- **WHEN** `ask_fn` is awaited by a bot worker
- **THEN** the Textual UI SHALL remain responsive while the worker is suspended

#### Scenario: Worker resumes with the user's decision after modal dismissal
- **WHEN** the ApprovalModal dismisses with a GuardDecision
- **THEN** `ask_fn` SHALL return that decision to the awaiting bot worker

#### Scenario: Worker cancellation during modal is clean
- **WHEN** `app.exit()` is called while a worker is awaiting the Future
- **THEN** the worker SHALL receive `CancelledError` and terminate without error
- **THEN** the unresolved Future SHALL be garbage collected without side effects
