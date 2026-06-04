"""Find all Kaprekar pairs (a, b) where (a + b)² = concat(a, b).

Examples include (8 + 1)² = 81, (20 + 25)² = 2025, and (6048 + 1729)² = 60481729.
"""

import itertools

LIMIT = 10_000

for a, b in itertools.product(range(1, LIMIT), range(1, LIMIT)):
    n = a + b
    if n**2 == int(f"{a}{b}"):
        print(f"({a} + {b})² = {n}² = {n * n}", flush=True)
