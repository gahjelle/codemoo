"""Find all Kaprekar pairs (a, b) where (a + b)² = concat(a, b)."""

import itertools

LIMIT = 10_000

for a, b in itertools.product(range(1, LIMIT), range(1, LIMIT)):
    n = a + b
    if n**2 == int(f"{a}{b}"):
        print(f"({a} + {b})² = {n}² = {n * n}", flush=True)
