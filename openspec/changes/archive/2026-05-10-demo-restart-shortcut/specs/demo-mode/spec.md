## ADDED Requirements

### Requirement: Ctrl-R keyboard shortcut is documented in DemoHeader
The `DemoHeader` hint line SHALL include "Ctrl-R: restart" as a permanently visible hint, regardless of prompt count.

#### Scenario: Ctrl-R hint always present in demo header
- **WHEN** `DemoHeader` is constructed with zero or more prompts
- **THEN** `str(header.render())` SHALL contain "Ctrl-R"
