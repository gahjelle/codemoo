## 1. Tools Module

- [x] 1.1 Create `src/codemoo/core/tools/__init__.py` exporting `ToolDef` and `reverse_string`
- [x] 1.2 Implement `ToolDef` dataclass with `schema: dict` and `fn: Callable[..., str]` fields
- [x] 1.3 Implement `reverse_string` `ToolDef` with JSON-schema definition and `fn` that reverses a string by codepoints
- [x] 1.4 Write unit tests for `reverse_string.fn` (ASCII, empty, Unicode)

## 2. Backend: complete_step

- [x] 2.1 Add `TextResponse` and `ToolUse` dataclasses to `src/codemoo/core/backend.py`
- [x] 2.2 Add `complete_step(messages, tools) -> TextResponse | ToolUse` to the `ToolLLMBackend` protocol (separate from `LLMBackend` to preserve existing mock compatibility)
- [x] 2.3 Implement `complete_step` on `_MistralBackend` in `src/codemoo/llm/backend.py`: send tools to Mistral, map the response to `TextResponse` or `ToolUse` (do NOT invoke the tool or re-submit)
- [x] 2.4 Write unit tests for `complete_step`: text-response path and tool-use path (mock the Mistral client)

## 3. ToolBot

- [x] 3.1 Create `src/codemoo/core/bots/tool_bot.py` with `ToolBot` dataclass implementing `ChatParticipant`
- [x] 3.2 Add lightweight default `_INSTRUCTIONS` string (tool-aware, no rigid persona)
- [x] 3.3 Implement `on_message`: call `backend.complete_step`, handle `ToolUse` branch (invoke `fn`, append tool result, call `backend.complete`), wrap final text in `ChatMessage`
- [x] 3.4 Write unit tests for `ToolBot.on_message`: text-response path (no tool invoked), tool-use path (tool invoked, backend called twice, sender correct)

## 4. CLI and Selection Screen

- [x] 4.1 Instantiate `ToolBot` (name="Telo", emoji="🔧") with `[reverse_string]` in `src/codemoo/__init__.py` and add it to the available bots list
- [x] 4.2 Implement the `tool` CLI command stub in `cli.py` (single-turn call via `complete_step` + manual tool handling, for quick smoke-testing outside the TUI)
- [x] 4.3 Update selection screen ordering test / snapshot if one exists to include ToolBot as fifth entry
