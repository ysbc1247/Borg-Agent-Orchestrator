#!/usr/bin/env python3

import sys


def fibonacci(count: int) -> list[int]:
    sequence: list[int] = []
    a, b = 0, 1

    for _ in range(count):
        sequence.append(a)
        a, b = b, a + b

    return sequence


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <count>")
        return 1

    try:
        count = int(sys.argv[1])
    except ValueError:
        print("Count must be an integer.")
        return 1

    if count < 0:
        print("Count must be non-negative.")
        return 1

    print(" ".join(str(number) for number in fibonacci(count)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
