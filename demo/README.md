# The Greeter

A small script that greets each bot in the Codemoo demo by name.

## Usage

```console
uv run python greeter.py
```

The script reads bot names from `names.txt`, sorts them alphabetically, and prints
a greeting for each one.

## Files

| File              | Description                             |
| ----------------- | --------------------------------------- |
| `greeter.py`      | Main script — loads names and greets    |
| `names.txt`       | One bot name per line                   |
| `test_greeter.py` | Pytest tests for the greeting functions |

## Running the tests

```console
uv run pytest test_greeter.py
```
