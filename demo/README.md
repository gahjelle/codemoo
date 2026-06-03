# Demo Scripts

Two scripts for exploring correctness and performance in Python.

---

## kaprekar.py

A curious mathematical pattern: (20 + 25)² = 45² = 2025, and (30 + 25)² = 55² = 3025.
In general, a *Kaprekar pair* is a pair (a, b) where (a + b)² equals the concatenation
of a and b. `kaprekar.py` finds all such pairs with 0 ≤ a, b < 10000.

Uses an efficient algorithm: for each candidate n in range(0, 20000), it computes n²,
splits the decimal representation into two parts, and checks whether they sum to n.
Runs in milliseconds.

### Usage

```console
uv run kaprekar.py
```

### Files

| File          | Description                              |
| ------------- | ---------------------------------------- |
| `kaprekar.py` | Main script — finds and prints all pairs |

---

## greeter.py

A small script that greets each bot in the Codemoo demo by name.

The script reads bot names from `names.txt`, sorts them alphabetically, and prints
a greeting for each one.

### Usage

```console
uv run greeter.py
```

### Files

| File              | Description                             |
| ----------------- | --------------------------------------- |
| `greeter.py`      | Main script — loads names and greets    |
| `names.txt`       | One bot name per line                   |
| `test_greeter.py` | Pytest tests for the greeting functions |

### Running the tests

```console
uv run pytest test_greeter.py
```
