## ADDED Requirements

### Requirement: LLM explanation is cached in DemoContext for reuse across slide reopens
After the LLM explanation is successfully generated for a bot's slide, the text SHALL be stored in `DemoContext.cached_explanation`. On subsequent opens of `SlideScreen` for the same bot, the cached text SHALL be used directly without issuing a new LLM API call.

#### Scenario: First open generates and caches the explanation
- **WHEN** `SlideScreen` is opened for the first time for a given bot
- **THEN** `SlideContent._load_explanation()` SHALL call the LLM and store the result in `DemoContext.cached_explanation`

#### Scenario: Reopened slide shows the cached explanation immediately
- **WHEN** `SlideScreen` is reopened via Ctrl-S after the initial LLM call has completed
- **THEN** the "what's new" area SHALL display the cached text immediately, without showing the loading indicator

#### Scenario: Loading indicator is only shown on first open
- **WHEN** `SlideScreen` is opened for the first time and the LLM call has not yet returned
- **THEN** the loading indicator SHALL be displayed as before
- **WHEN** `SlideScreen` is reopened after the LLM call has completed
- **THEN** no loading indicator SHALL appear
