#!/usr/bin/env python3
"""Robot Day 015: Caesar Message Spinner

A tiny terminal toy that:
- Encodes/decodes messages with a classic Caesar shift cipher
- Provides a fun "spinner" animation while processing

Stdlib only. Safe to run offline.
"""

import string
import sys
import time

ALPH = string.ascii_uppercase


def spinner(seconds: float = 0.8, label: str = "Working") -> None:
    """Simple terminal spinner animation."""
    frames = "|/-\\"
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{label} {frames[i % len(frames)]}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(label) + 4) + "\r")


def caesar(text: str, shift: int) -> str:
    """Shift A-Z letters by shift positions, preserving case; leaves others unchanged."""
    out = []
    for ch in text:
        up = ch.upper()
        if up in ALPH:
            idx = (ALPH.index(up) + shift) % 26
            new = ALPH[idx]
            out.append(new if ch.isupper() else new.lower())
        else:
            out.append(ch)
    return "".join(out)


def ask_int(prompt: str, default: int) -> int:
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        print("Please enter an integer.")
        return ask_int(prompt, default)


def menu() -> str:
    print("Caesar Message Spinner")
    print("----------------------")
    print("1) Encode a message")
    print("2) Decode a message")
    print("3) Brute-force decode (try all shifts)")
    print("4) Quit")
    return input("Choose: ").strip()


def main() -> int:
    while True:
        choice = menu()
        if choice == "4":
            print("Bye.")
            return 0

        if choice not in {"1", "2", "3"}:
            print("Pick 1, 2, 3, or 4.\n")
            continue

        msg = input("Message: ")
        if choice in {"1", "2"}:
            shift = ask_int("Shift", 3) % 26
            spinner(label="Spinning gears")
            if choice == "2":
                shift = (-shift) % 26
            result = caesar(msg, shift)
            print("Result:")
            print(result)
            print()
        else:
            spinner(label="Trying shifts")
            print("All possibilities (shift -> text):")
            for s in range(26):
                print(f"{s:2d}: {caesar(msg, -s)}")
            print()


if __name__ == "__main__":
    raise SystemExit(main())
