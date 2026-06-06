# Demo Environment

The `demo/` folder is a purpose-built environment for live demonstrations — not production code. It contains intentional issues that **must stay in place**.

## Intentional Bugs — Do Not Fix

**`demo/greeter.py`** opens `names.txt` with `encoding="ascii"`. This causes a `UnicodeDecodeError` at runtime. AgentBot (Loom) attempts to fix it but raises on the tool error; RetryBot (Crow) succeeds by feeding the error back to the LLM. Do not change this encoding.

**`demo/README.md`** claims:

- the `kaprekar.py` script "uses an efficient algorithm" and "runs in milliseconds". Neither is true. This is intentional — it makes the ReadBot comparison prompt reveal a real difference between the README and the code.
- the `greeter.py` script "sorts names alphabetically." The code does not sort. This discrepancy is intentional.

**`demo/whoami.py`** is a legacy demo artifact — it is no longer part of the active demo script.

When modifying `demo/` files for other reasons, preserve these intentional issues.
