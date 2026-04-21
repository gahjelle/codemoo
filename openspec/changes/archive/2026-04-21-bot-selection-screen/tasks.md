## 1. Bot bubble color fix

- [x] 1.1 Update `.bubble--bot` background color in `chat.tcss` to `#2a1f4a` (dark violet) for contrast with Markdown code-block rendering

## 2. SelectionApp widget

- [x] 2.1 Create `src/codaroo/chat/selection.py` with a `SelectionApp(App[list[ChatParticipant]])` class
- [x] 2.2 Add a `SelectionList` widget populated from the injected `available_bots` list, sorted in fixed order (EchoBot, LLMBot, ChatBot by type)
- [x] 2.3 Format each list item as `"Name (TypeName)"` (e.g. `"Mistral (LLMBot)"`)
- [x] 2.4 Add a confirm action (button or keybinding) that calls `self.exit()` with the list of selected `ChatParticipant` objects in fixed order
- [x] 2.5 Add CSS for the selection screen layout (title, list, confirm button) to `chat.tcss` or a new `selection.tcss`

## 3. Wire up startup flow

- [x] 3.1 Update `main()` in `src/codaroo/__init__.py` to instantiate all three candidate bots (EchoBot, LLMBot, ChatBot) plus the human participant
- [x] 3.2 Run `SelectionApp(available_bots)` first and capture the returned participant list
- [x] 3.3 Prepend the human participant to the selected list and pass it to `ChatApp`

## 4. Tests

- [x] 4.1 Add unit tests for the fixed-order sorting logic in `SelectionApp` (pure function, no Textual required)
- [x] 4.2 Add unit tests for the list item label formatting (`"Name (TypeName)"`)
