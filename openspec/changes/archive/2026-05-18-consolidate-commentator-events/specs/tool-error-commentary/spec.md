## REMOVED Requirements

### Requirement: ToolErrorEvent is emitted by dispatch_tool when a tool returns an error string
**Reason**: `ToolErrorEvent` is replaced by `ToolEvent(outcome="error")`. The emission logic in `dispatch_tool` is preserved but now uses the consolidated `ToolEvent` dataclass. See the updated `commentary-events` spec requirement "dispatch_tool is the sole emitter of ToolEvent for all outcomes".
**Migration**: Replace `ToolErrorEvent(bot_name=..., tool_name=..., arguments=..., result=...)` with `ToolEvent(outcome="error", bot_name=..., tool_name=..., arguments=..., detail=result)`.

### Requirement: ToolErrorEvent is a frozen dataclass with bot_name, tool_name, arguments, and result
**Reason**: Superseded by `ToolEvent` which carries the same information via the `detail` field for error outcomes.
**Migration**: Use `ToolEvent.detail` where `ToolErrorEvent.result` was previously accessed.

### Requirement: CommentatorBot generates in-character commentary for ToolErrorEvent
**Reason**: Superseded by the unified `ToolEvent` handler in `CommentatorBot`. The `"error"` template key drives the same behavior as the former `_comment_on_tool_error` method. See the updated `commentary-events` spec requirement "CommentatorBot handles ToolEvent outcomes via template lookup".
**Migration**: No action needed — `CommentatorBot` handles `ToolEvent(outcome="error")` automatically.
