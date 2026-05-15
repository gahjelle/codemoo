# Spec: splash-screen

## Purpose

TBD — defines the cowsay-inspired animated splash screen shown at startup before heavy imports load, including layout, animations, and color scheme.

## Requirements

### Requirement: Splash screen appears before heavy imports load
The system SHALL display a Textual `SplashApp` within ~120ms of invocation,
before Pydantic, config loading, or the Anthropic SDK are imported. Heavy
imports and bot setup SHALL occur in a background worker thread while the
splash is visible.

#### Scenario: Splash appears before config loads
- **WHEN** the user runs `codemoo`
- **THEN** the splash screen SHALL be visible before `codemoo.config` is imported

#### Scenario: Splash dismissed when loading completes
- **WHEN** the background worker finishes setup
- **THEN** `SplashApp` SHALL exit immediately, even if animation is mid-frame

### Requirement: Splash displays cowsay-inspired animated ASCII art
The splash SHALL render a fixed-layout ASCII art scene containing a terminal
code window (thought bubble), connecting dots, a cow, and a title. The layout
SHALL NOT shift when animated elements change state.

#### Scenario: Terminal code window is present
- **WHEN** the splash screen is shown
- **THEN** a box drawn with `┌─ agent_loop.py ─…─┐` / `└─…─┘` SHALL be visible

#### Scenario: Cow ASCII art is present
- **WHEN** the splash screen is shown
- **THEN** the classic cowsay cow body (`^__^`, `(oo)`, hooves) SHALL be visible
  below the terminal window, connected by dot separators

#### Scenario: Title is present
- **WHEN** the splash screen is shown
- **THEN** `C O D E M O O` and the subtitle `coding agents, step by step` SHALL
  appear below the cow

### Requirement: Typewriter animation reveals the code snippet progressively
The splash SHALL reveal a four-line Python snippet character by character at
~40ms per character. The snippet is:

```
while True:
    thought = llm.think()
    if thought:
        moo()
```

The animation runs once; it does not loop. If the splash is dismissed before
the snippet is fully revealed, it stops mid-character.

#### Scenario: Code types in progressively
- **WHEN** the splash has been visible for 200ms
- **THEN** a partial prefix of the snippet SHALL be visible in the terminal window

#### Scenario: No looping
- **WHEN** the snippet is fully revealed
- **THEN** the typewriter SHALL stop and the cursor SHALL continue blinking

### Requirement: Cursor blinks at the current typing position
A block cursor (`█`) SHALL appear at the end of the most recently revealed
character. It SHALL blink on/off at ~500ms intervals.

#### Scenario: Cursor is visible at the type position
- **WHEN** the typewriter is mid-animation
- **THEN** `█` SHALL appear immediately after the last revealed character

#### Scenario: Cursor blinks after animation ends
- **WHEN** the snippet is fully revealed
- **THEN** the cursor SHALL continue blinking at the end of the last line

### Requirement: Cow tail wiggles during the splash
The tail segment `\/\` on the cow body line SHALL alternate to `/\/` every
~600ms, creating a subtle swishing animation. The surrounding layout SHALL
not shift.

#### Scenario: Tail alternates between two frames
- **WHEN** the splash is visible
- **THEN** the tail SHALL cycle between `\/\` and `/\/` at ~600ms intervals

### Requirement: Cow eyes blink and tongue occasionally appears
The cow's eyes `(oo)` SHALL periodically blink to `(--)` for ~150ms.
Occasionally after a blink, a tongue `~` SHALL appear on the reserved tongue
line for ~300ms before disappearing. The tongue line is always present in the
layout (as blank space) so no vertical shift occurs.

#### Scenario: Eyes blink
- **WHEN** the splash has been visible for several seconds
- **THEN** the eyes SHALL change from `(oo)` to `(--)` briefly

#### Scenario: Tongue appears after a blink
- **WHEN** the eye-blink animation fires on a tongue frame
- **THEN** `~` SHALL appear on the tongue line for ~300ms

#### Scenario: Layout does not shift when tongue appears
- **WHEN** the tongue appears or disappears
- **THEN** all other elements (body, hooves, title) SHALL remain in the same
  vertical positions

### Requirement: Splash uses a defined color scheme
The splash SHALL apply the following colors:

| Element | Color |
|---|---|
| Terminal window frame and filename | Dim white |
| Python keywords (`while`, `if`) | Bold `#7aa2f7` (soft blue) |
| Identifiers and cursor `█` | `#9ece6a` (green) |
| Tongue `~` | `#f7768e` (pink-red) |
| Cow body | Bright white |
| Thought-bubble dots | Dim |
| Title `C O D E M O O` | Bold `#7dcfff` (cyan) |
| Subtitle | Dim italic |

#### Scenario: Keywords are colored blue
- **WHEN** the typewriter reveals `while` or `if`
- **THEN** those tokens SHALL render in `#7aa2f7`

#### Scenario: Title is bold cyan
- **WHEN** the splash is shown
- **THEN** `C O D E M O O` SHALL render in bold `#7dcfff`
