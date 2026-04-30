## 1. Protocol and Interface Updates

- [x] 1.1 Update `ToolLLMBackend` protocol in `core/backend.py` to have single `complete(messages, tools=None)` method
- [x] 1.2 Remove `TextResponse` class from `core/backend.py`
- [x] 1.3 Update type hints and imports throughout the codebase
- [x] 1.4 Verify all protocol implementations satisfy the new unified interface

## 2. Base Class Implementation

- [x] 2.1 Create `OpenAILikeBackend` base class with unified `complete()` method
- [x] 2.2 Implement `_serialize()` method for OpenAI-compatible message format
- [x] 2.3 Implement `_tool_schema()` method for OpenAI function-calling format
- [x] 2.4 Add proper error handling and edge case management
- [x] 2.5 Write unit tests for the base class

## 3. Backend Refactoring

- [x] 3.1 Refactor `MistralBackend` to inherit from `OpenAILikeBackend`
- [x] 3.2 Refactor `OpenRouterBackend` to inherit from `OpenAILikeBackend`
- [x] 3.3 Update `AnthropicBackend` to implement unified `complete()` method
- [x] 3.4 Remove old `complete()` and `complete_step()` methods from all backends
- [x] 3.5 Update factory functions to work with new backend structure

## 4. Bot Updates

- [x] 4.1 Update `LlmBot` to use unified `complete()` method
- [x] 4.2 Update `SingleTurnToolBot` to use unified method with tools parameter
- [x] 4.3 Update `AgentBot` to use unified method in its loop
- [x] 4.4 Update all other bot implementations that use LLM backends
- [x] 4.5 Ensure demo bots work correctly with new interface

## 5. Test Updates

- [x] 5.1 Update existing LLM backend tests for new signatures
- [x] 5.2 Update bot tests for new method calls
- [x] 5.3 Add tests for unified method behavior
- [x] 5.4 Add tests for base class functionality
- [x] 5.5 Ensure all tests pass with new implementation

## 6. Documentation and Cleanup

- [x] 6.1 Update README.md if LLM usage examples are shown
- [x] 6.2 Update any relevant documentation files (BOTS.md, AGENTS.md, etc.)
- [x] 6.3 Remove deprecated code and unused imports
- [x] 6.4 Run `ruff format` on all modified files
- [x] 6.5 Run `ruff check` on all modified files
- [x] 6.6 Run `ty check` on all modified files
- [x] 6.7 Run `pytest` to ensure all tests pass

## 7. Verification and Finalization

- [x] 7.1 Test all bots manually to ensure they work correctly
- [x] 7.2 Verify demo scenarios work as expected
- [x] 7.3 Check that the unified approach improves code clarity
- [x] 7.4 Confirm that backend reuse is working properly
- [x] 7.5 Final review of all changes and cleanup
