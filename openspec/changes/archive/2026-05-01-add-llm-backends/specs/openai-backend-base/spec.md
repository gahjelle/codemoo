## MODIFIED Requirements

### Requirement: Concrete backends inherit from base class
MistralBackend, OpenRouterBackend, OpenAIBackend, GoogleBackend, and OllamaBackend SHALL all inherit from `OpenAILikeBackend` and provide only the minimal necessary overrides: a constructor that stores the client and model, and a `_call()` implementation that invokes the provider API. Base-URL configuration is the responsibility of the factory function, not the class.

#### Scenario: MistralBackend inherits from base class
- **WHEN** `MistralBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`

#### Scenario: OpenRouterBackend inherits from base class
- **WHEN** `OpenRouterBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`

#### Scenario: OpenAIBackend inherits from base class
- **WHEN** `_OpenAIBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`

#### Scenario: GoogleBackend inherits from base class
- **WHEN** `_GoogleBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`

#### Scenario: OllamaBackend inherits from base class
- **WHEN** `_OllamaBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`
