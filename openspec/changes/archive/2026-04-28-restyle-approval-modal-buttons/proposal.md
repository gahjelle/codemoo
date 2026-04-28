## Why

The current button labels ("Approve", "Deny", "Deny with reason…") are functional but formal. Shorter labels ("Yes", "No, but …", "No") paired with a traffic-light color scheme (green / yellow / red) make the choice faster to read and the risk level immediately visible.

## What Changes

- Button labels: "Approve" → "Yes", "Deny with reason…" → "No, but …", "Deny" → "No"
- Button order: Yes / No, but … / No (was: Approve / Deny / Deny with reason…)
- Button color: "No, but …" gets `variant="warning"` (yellow); "Yes" stays `variant="success"` (green); "No" stays `variant="error"` (red)
- Button IDs and all dismiss logic are unchanged

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `approval-modal`: Button labels, order, and variants are part of the modal's specified interaction contract.

## Impact

- `src/codemoo/chat/approval.py` — update `compose()` button definitions only

## Non-goals

- Changing button IDs (`approve`, `deny`, `deny-reason`)
- Changing any dismiss logic or `GuardDecision` values
- Changing any other part of the modal layout or CSS
