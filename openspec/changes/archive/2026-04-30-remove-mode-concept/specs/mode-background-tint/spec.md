## REMOVED Requirements

### Requirement: ChatApp applies a mode-specific CSS class to the app root
**Reason**: Mode is removed. Background tinting based on mode is dropped entirely.
**Migration**: Remove `self.add_class(f"mode-{self._mode}")` from `ChatApp.on_mount`. Remove the `mode` parameter from `ChatApp.__init__`.

### Requirement: Mode CSS classes define a subtle background tint
**Reason**: Background tints are removed along with the mode concept.
**Migration**: Remove `.mode-code` and `.mode-business` rules from `chat.tcss`.

### Requirement: ChatApp accepts a mode parameter
**Reason**: Mode is removed from `ChatApp`. The app no longer needs to know which mode it is running in.
**Migration**: Remove `mode: ModeName = "code"` from `ChatApp.__init__`. Update all `ChatApp(...)` call sites to omit the `mode=` argument.
