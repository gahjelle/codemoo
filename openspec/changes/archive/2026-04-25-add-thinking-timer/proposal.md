## Why

Users need better feedback about how long bot operations are taking. Currently, the "Loom thinking..." indicator provides no sense of duration, which can be frustrating during longer operations. Adding a running timer provides transparency and improves user experience by setting expectations about wait times.

## What Changes

- Add a running timer to the thinking status display (e.g., "Loom thinking... (3s)")
- Include the total thinking time in bot message headers with subtle formatting (e.g., "Loom [dim](5s)[/dim]")
- Enhance `ThinkingStatus` widget to track and display elapsed time
- Add `thinking_time` field to `ChatMessage` data class
- Update message display to show thinking duration in headers

## Capabilities

### New Capabilities
- `thinking-timer`: Display real-time thinking duration in status bar and include total thinking time in bot message headers

### Modified Capabilities

*(None - this is a purely additive feature that doesn't change existing requirements)*

## Impact

- **UI Components**: `ThinkingStatus` widget, `ChatBubble` display, `ChatMessage` data structure
- **User Experience**: Improved feedback during bot operations
- **Performance**: Minimal impact (one timer per bot response)

## Non-goals

- Sub-second precision (whole seconds only)
- Timer for human typing/composition
- Historical analytics or logging of thinking times
- Multi-bot concurrent timing (not needed due to sequential processing)