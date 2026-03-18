#!/usr/bin/env python3
"""Robot Day 005: Password Forge

A small terminal bot that forges strong, readable passwords using only Python's
standard library.

Features:
- Choose length and character sets (lower/upper/digits/symbols)
- Avoid ambiguous characters by default (O/0, l/1, etc.)
- Guarantees at least one character from each selected set
- Optional "phrase" mode: builds a hyphenated password from a tiny built-in wordlist

Usage:
  python robot_day_005_password_forge.py

Notes:
- This script never writes passwords to disk.
- Copy/paste carefully in public places; your robot cannot cover your screen.
"""

from __future__ import annotations

import secrets
import string


AMBIGUOUS = set("O0Il1|`'\"")

# Small, built-in word list for a fun "phrase" mode.
WORDS = [
    "nebula", "cactus", "vector", "bamboo", "saffron", "orbit", "quartz",
    "mango", "mistral", "anvil", "panda", "tulip", "cobalt", "fjord",
    "hazelnut", "pixel", "rocket", "sphinx", "circuit", "lagoon",
]


def yn(prompt: str, default: bool = True) -> bool:
    """Yes/no prompt.

    When stdin is not interactive (or input is piped), we fall back to defaults
    instead of crashing.
    """
    d = "Y/n" if default else "y/N"
    while True:
        try:
            raw = input(f"{prompt} [{d}]: ").strip().lower()
        except EOFError:
            return default
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer y or n.")


def ask_int(prompt: str, default: int, min_value: int, max_value: int) -> int:
    """Integer prompt with safe default when stdin is non-interactive."""
    while True:
        try:
            raw = input(f"{prompt} [{default}]: ").strip()
        except EOFError:
            return default
        if not raw:
            return default
        try:
            v = int(raw)
        except ValueError:
            v = None
        if v is not None and min_value <= v <= max_value:
            return v
        print(f"Please enter a whole number between {min_value} and {max_value}.")


def pool_from_flags(lower: bool, upper: bool, digits: bool, symbols: bool, avoid_amb: bool) -> list[str]:
    pools: list[str] = []
    if lower:
        pools.append(string.ascii_lowercase)
    if upper:
        pools.append(string.ascii_uppercase)
    if digits:
        pools.append(string.digits)
    if symbols:
        pools.append("!@#$%^&*()-_=+[]{}:,.?")

    if avoid_amb:
        pools = ["".join(c for c in p if c not in AMBIGUOUS) for p in pools]

    # Remove empty pools (possible if avoid_amb strips everything, unlikely).
    return [p for p in pools if p]


def forge_password(length: int, pools: list[str]) -> str:
    """Forge a password ensuring at least one char from each selected pool."""
    if not pools:
        raise ValueError("No character sets selected")
    if length < len(pools):
        raise ValueError("Length is too short for the number of selected sets")

    rng = secrets.SystemRandom()

    # 1) Guarantee coverage: one from each pool.
    chars = [rng.choice(p) for p in pools]

    # 2) Fill remaining length from the combined pool.
    combined = "".join(pools)
    chars.extend(rng.choice(combined) for _ in range(length - len(pools)))

    # 3) Shuffle so guaranteed chars aren't predictable positions.
    rng.shuffle(chars)
    return "".join(chars)


def forge_phrase(words: int, digits: int, capitalize: bool) -> str:
    rng = secrets.SystemRandom()
    chosen = [rng.choice(WORDS) for _ in range(words)]
    if capitalize:
        chosen = [w.capitalize() for w in chosen]
    tail = "".join(rng.choice(string.digits) for _ in range(digits)) if digits else ""
    return "-".join(chosen) + tail


def main() -> int:
    print("\nPassword Forge Robot")
    print("--------------------")

    if yn("Use phrase mode (readable hyphenated words)?", default=False):
        w = ask_int("How many words", default=4, min_value=2, max_value=8)
        d = ask_int("Extra digits at the end", default=2, min_value=0, max_value=8)
        cap = yn("Capitalize words", default=True)
        print("\nForged password:")
        print(forge_phrase(w, d, cap))
        return 0

    length = ask_int("Password length", default=20, min_value=8, max_value=64)

    avoid_amb = yn("Avoid ambiguous characters (O/0, l/1, etc.)", default=True)
    lower = yn("Include lowercase", default=True)
    upper = yn("Include uppercase", default=True)
    digits = yn("Include digits", default=True)
    symbols = yn("Include symbols", default=True)

    pools = pool_from_flags(lower, upper, digits, symbols, avoid_amb)

    try:
        pwd = forge_password(length, pools)
    except ValueError as e:
        print(f"\nError: {e}")
        print("Tip: either increase length or select fewer character sets.")
        return 2

    print("\nForged password:")
    print(pwd)
    print("\nTip: generate a few and pick one you can type confidently.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
