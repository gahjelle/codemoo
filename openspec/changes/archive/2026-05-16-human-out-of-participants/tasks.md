## 1. Protocol and HumanParticipant

- [x] 1.1 Remove `is_human: ClassVar[bool]` from `ChatParticipant` protocol in `src/codemoo/core/participant.py`
- [x] 1.2 Remove `on_message` and `is_human` from `HumanParticipant`; make it a plain dataclass
- [x] 1.3 Drop `is_human: ClassVar[bool] = False` from all bot classes (`chat_bot`, `llm_bot`, `echo_bot`, `agent_bot`, `guard_bot`, `project_bot`, `memory_bot`, `retry_bot`, `system_bot`, `error_bot`, `single_turn_tool_bot`)

## 2. ChatApp wiring

- [x] 2.1 Add `human: HumanParticipant` as an explicit argument to `ChatApp.__init__`; set `self._human = human` directly
- [x] 2.2 Change `_sender_info` tuple to `(emoji, css_class)`; populate human's entry from `self._human` explicitly; remove `is_human` field from all entries
- [x] 2.3 Update `_append_to_log` to unpack the two-element tuple and pass `css_class` to `ChatBubble`
- [x] 2.4 Remove `if status and not participant.is_human:` guard from `_collect_replies`; call `status.set_bot(...)` unconditionally
- [x] 2.5 Replace `next(p for p in self._participants if not p.is_human)` with `self._participants[0]` in `compose` (line 95) and `_restart_bot` (line 258)

## 3. ChatBubble CSS alignment

- [x] 3.1 Move `css_class` from `_BubbleContent` to the outer `ChatBubble` widget; remove `css_class` parameter from `_BubbleContent`
- [x] 3.2 Change `_BubbleContent` width from `4fr` to `80%`; remove the `Static` spacer from `ChatBubble.compose`
- [x] 3.3 Remove `is_human` parameter from `ChatBubble`; derive all behavior from `css_class`
- [x] 3.4 Add `ChatBubble.bubble--human { align-horizontal: right; }` to `chat.tcss`; verify visual rules (background, border, padding) still render correctly on the outer widget

## 4. Call sites

- [x] 4.1 Update the three `ChatApp(...)` call sites in `tui.py` from `participants=[setup.human, *setup.available]` to `human=setup.human, participants=setup.available`
- [x] 4.2 Delete `FUTURE_human-out-of-participants.md` from the repo root

## 5. Tests

- [x] 5.1 Update `tests/core/test_participant.py`: remove `is_human` from `_MinimalParticipant`; remove `is_human`-related protocol assertions
- [x] 5.2 Update `tests/chat/test_collect_replies.py`: remove `is_human` from all mock participants; update `_make_app` to pass `human=HumanParticipant()` separately
- [x] 5.3 Rewrite `tests/chat/test_bubble.py`: replace `is_human=True/False` with `css_class="bubble--human"/"bubble--bot"`; verify CSS class is on outer `ChatBubble` widget

## 6. Review for simplification

- [x] 6.1 Read through `src/codemoo/chat/app.py`, `src/codemoo/chat/bubble.py`, and `src/codemoo/core/participant.py` looking for design decisions that were shaped by `HumanParticipant` being a full participant (e.g. guards, branches, data structures that no longer need to account for a non-bot in the loop)
- [x] 6.2 For each opportunity found: if the change is small and self-contained, implement it directly; if it is larger or has wider impact, write it up as a future-change note in a Markdown file at the project root (following the pattern of `FUTURE_human-out-of-participants.md`)

## 7. Verify

- [x] 7.1 Run `uv run pytest tests/core/test_participant.py tests/chat/test_bubble.py tests/chat/test_collect_replies.py`
- [x] 7.2 Run `uv run ruff check . && uv run ruff format . && uv run ty check .`
- [x] 7.3 Run `uv run codemoo` and visually confirm human bubbles are right-aligned and bot bubbles are left-aligned
