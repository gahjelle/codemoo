## Context

`ApprovalModal.compose()` in `approval.py` yields three `Button` widgets inside a `Horizontal`. The current order and styling:

```python
yield Button("Approve", id="approve", variant="success")   # green
yield Button("Deny", id="deny", variant="error")           # red
yield Button("Deny with reason\N{HORIZONTAL ELLIPSIS}", id="deny-reason")  # gray
```

Textual's built-in button variants map directly to the traffic light metaphor: `success` = green, `warning` = yellow, `error` = red. No CSS overrides are needed.

## Goals / Non-Goals

**Goals:**
- Apply the traffic light metaphor: green (proceed) / yellow (proceed with caveat) / red (stop)
- Shorten labels for faster scanning

**Non-Goals:**
- Any changes to button IDs, event handlers, or dismiss logic
- CSS changes beyond what Textual's `variant` provides

## Decisions

### Button order: Yes → No, but … → No

Left-to-right matches the traffic light sequence green→yellow→red and puts the affirmative action first (standard dialog convention). The gray "Deny with reason" was last before; moving it to the middle makes the visual gradient coherent.

### Use `variant="warning"` for "No, but …"

Textual's `warning` variant is yellow in the default theme, which completes the traffic light. No custom CSS needed, and it degrades gracefully in themes that don't use traffic-light colors.

## Risks / Trade-offs

- [Theme variance] In non-default Textual themes, `warning` may not be yellow. Accepted — the semantic grouping (three distinct variants) still communicates hierarchy even if the exact colors differ.
