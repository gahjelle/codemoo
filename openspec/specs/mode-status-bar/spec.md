# Spec: mode-status-bar

## Purpose

TBD — Defines how the active mode name is displayed in the `BackendStatus` widget's left section.

## Requirements

### Requirement: BackendStatus displays mode name in the left section
`BackendStatus` SHALL display the active mode name, title-cased (e.g. `"Code"`, `"Business"`), in its left section. The existing backend/model text SHALL remain in the right section.

#### Scenario: Mode label shows title-cased mode name
- **WHEN** `BackendStatus` is constructed with `mode="code"`
- **THEN** the left label SHALL display `"Code"`

#### Scenario: Business mode label is title-cased
- **WHEN** `BackendStatus` is constructed with `mode="business"`
- **THEN** the left label SHALL display `"Business"`

### Requirement: BackendStatus left and right labels are laid out horizontally
`BackendStatus` SHALL use `layout: horizontal` so the mode label occupies the left and the backend/model label occupies the right of the same row.

#### Scenario: Both labels are visible in the same row
- **WHEN** `BackendStatus` is mounted with `mode="code"` and a backend info
- **THEN** both the mode label and the backend/model label SHALL be visible within `BackendStatus`'s single-line height
