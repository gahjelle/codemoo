## REMOVED Requirements

### Requirement: BackendStatus displays mode name in the left section
**Reason**: Mode is removed. The left section now displays bot type and variant instead (see `backend-status-bar` delta spec).
**Migration**: Remove the mode label from `BackendStatus`. Replace with `{BotType} ({variant})` entries derived from `list[ResolvedBotConfig]`.

### Requirement: BackendStatus left and right labels are laid out horizontally
**Reason**: The layout requirement is now covered entirely by the updated `backend-status-bar` spec. No change to the horizontal layout itself — only the content of the left label changes.
**Migration**: No layout changes needed; only the left label content changes.
