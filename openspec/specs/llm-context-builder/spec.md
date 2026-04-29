# Spec: llm-context-builder

## Purpose

~~Defines the `build_llm_context` pure function that converts chat history and a current message into a filtered, role-mapped `list[Message]` suitable for passing to an `LLMBackend`.~~

**DEPRECATED**: `build_llm_context` has been removed. Each bot now builds its `list[Message]` inline in `on_message`. Context construction is no longer centralized.

## Requirements

*(All requirements have been removed. See individual bot specs for inline context construction patterns.)*
