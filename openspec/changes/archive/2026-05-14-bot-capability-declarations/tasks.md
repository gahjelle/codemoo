## 1. Schema Changes

- [x] 1.1 Add `type BotCapability = Literal["context_management"]` to `src/codemoo/config/schema.py` alongside `BotType` and `ScriptName`
- [x] 1.2 Add `capabilities: list[BotCapability] = []` field to `BotVariantConfig` in `schema.py`
- [x] 1.3 Add `capabilities: list[str]` field to `ResolvedBotConfig` dataclass in `schema.py`
- [x] 1.4 Update `resolve()` to copy `variant.capabilities` into `ResolvedBotConfig.capabilities`

## 2. Config Update

- [x] 2.1 Add `capabilities = ["context_management"]` to `[bots.RetryBot.variants.code]` in `src/codemoo/config/codemoo.toml`
- [x] 2.2 Add `capabilities = ["context_management"]` to `[bots.RetryBot.variants.m365]` in `codemoo.toml`
- [x] 2.3 Add `capabilities = ["context_management"]` to `[bots.RetryBot.variants.workspace]` in `codemoo.toml`

## 3. ContextStatus Widget

- [x] 3.1 Create `src/codemoo/chat/context_status.py` with a `ContextStatus(Label)` widget; `DEFAULT_CSS` sets `height: 1`; `on_mount` hides the widget; expose `update_message_count(n: int)` that updates the label text to `f"Num messages: {n}"` and makes the widget visible
- [x] 3.2 Add `ContextStatus` CSS to `src/codemoo/chat/chat.tcss` (visual styling only: padding, color, text-style — matching `ThinkingStatus` styling)

## 4. ChatApp Capability Wiring

- [x] 4.1 Compute `self._active_capabilities: frozenset[str]` in `ChatApp.__init__` as the union of capabilities across all `resolved_bots`
- [x] 4.2 Add module-level `_CAPABILITY_BINDERS: dict[str, Callable[[ChatApp"], None]]` dict to `src/codemoo/chat/app.py`
- [x] 4.3 Implement `_bind_context_management(app: ChatApp) -> None` — mounts `ContextStatus` after `ThinkingStatus` in the compose tree (import `ContextStatus` inside the function)
- [x] 4.4 Register `"context_management": _bind_context_management` in `_CAPABILITY_BINDERS`
- [x] 4.5 In `ChatApp.on_mount`, iterate `_active_capabilities` and call each registered binder
- [x] 4.6 In `ChatApp._dispatch`, after `self._history.extend(replies)`, query for `ContextStatus` and call `update_message_count(len(self._history))` if the widget is mounted (guard with `try/except NoMatches`)

## 5. Tests

- [x] 5.1 Add tests to the appropriate test file for `BotVariantConfig.capabilities` field (default `[]`, valid name, invalid name raises)
- [x] 5.2 Add tests for `ResolvedBotConfig.capabilities` propagation via `resolve()`
- [x] 5.3 Add test that `ChatApp._active_capabilities` is the union of resolved bot capabilities

## 6. Verification

- [x] 6.1 Run `uv run ruff format src/ tests/`
- [x] 6.2 Run `uv run ruff check src/ tests/`
- [x] 6.3 Run `uv run ty check src/ tests/`
- [x] 6.4 Run `uv run pytest`
- [x] 6.5 Manually run `uv run codemoo --bot RetryBot` and verify the `ContextStatus` bar appears and increments with each exchange

## 7. Documentation

- [x] 7.1 Read `AGENTS.md` and update the `Bot Configuration` section to mention the `capabilities` field and the `BotCapability` type
