## ADDED Requirements

### Requirement: A bot spec resolves to a single bot by index, name, or type
The `resolve_bot(spec, bots)` function SHALL accept a string spec and an ordered list of `ChatParticipant` instances, and return the single matching bot. Resolution SHALL be attempted in this order: 1-based integer index, case-insensitive name match, case-insensitive type name match.

#### Scenario: Resolve by 1-based integer index
- **WHEN** `spec` is `"1"` and the first bot in the list is `EchoBot`
- **THEN** `resolve_bot` SHALL return that `EchoBot` instance

#### Scenario: Resolve by case-insensitive name
- **WHEN** `spec` is `"ash"` and a bot named `"Ash"` exists in the list
- **THEN** `resolve_bot` SHALL return that bot

#### Scenario: Resolve by case-insensitive type name
- **WHEN** `spec` is `"shellbot"` and a bot of type `ShellBot` exists in the list
- **THEN** `resolve_bot` SHALL return that bot

#### Scenario: Exact case is not required
- **WHEN** `spec` is `"ECHOBOT"` or `"EchoBot"` or `"echobot"`
- **THEN** `resolve_bot` SHALL return the `EchoBot` instance in all cases

### Requirement: An unrecognised spec raises an error with helpful context
If the spec matches nothing by index, name, or type, `resolve_bot` SHALL raise an error that includes the unrecognised spec and a listing of all valid names, types, and 1-based indices.

#### Scenario: Unknown spec raises error
- **WHEN** `spec` is `"UnknownBot"` and no bot matches by name or type
- **THEN** `resolve_bot` SHALL raise a `ValueError` (or equivalent CLI error type)

#### Scenario: Out-of-range index raises error
- **WHEN** `spec` is `"99"` and the list has fewer than 99 bots
- **THEN** `resolve_bot` SHALL raise an error indicating the index is out of range

### Requirement: Index resolution is 1-based
The integer index in a spec string SHALL be interpreted as 1-based, matching the human-visible numbering in documentation and the demo header.

#### Scenario: Index 1 returns the first bot
- **WHEN** `spec` is `"1"`
- **THEN** `resolve_bot` SHALL return `bots[0]`

#### Scenario: Index 0 is out of range
- **WHEN** `spec` is `"0"`
- **THEN** `resolve_bot` SHALL raise an error
