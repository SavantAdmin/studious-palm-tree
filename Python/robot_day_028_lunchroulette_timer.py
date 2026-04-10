#!/usr/bin/env python3
"""Robot Day 028: LunchRoulette Timer

A quirky lunch-break companion:
- asks your available minutes
- spins a tiny ASCII roulette wheel
- picks a bite-sized activity from built-ins or your custom list
- runs a simple countdown with gentle beeps (if your terminal supports it)

Stdlib only. No network. No installs.
"""

from __future__ import annotations

import random
import sys
import time

DEFAULT_ACTIVITIES = [
    "drink water",
    "stretch shoulders",
    "walk to a window and look far away",
    "tidy 10 items",
    "do 10 slow breaths",
    "write 3 bullet notes about today",
    "eat mindfully for 5 minutes",
    "text a friend hello",
    "step outside for fresh air",
    "prepare tomorrow's first task",
]

WHEEL = [
    "  .-''''-.  ",
    " /  .--.  \\",
    "|  /    \\  |",
    "| |  ()  | |",
    "|  \\    /  |",
    " \\  '--'  / ",
    "  '-.__.-'  ",
]


def ask_int(prompt: str, default: int) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            n = int(raw)
            if n <= 0:
                raise ValueError
            return n
        except ValueError:
            print("Please enter a positive whole number.")


def ask_activities() -> list[str]:
    print("\nOptional: add your own activities (comma-separated).")
    raw = input("Custom activities (or press Enter to skip): ").strip()
    if not raw:
        return DEFAULT_ACTIVITIES[:]
    custom = [a.strip() for a in raw.split(",") if a.strip()]
    pool = DEFAULT_ACTIVITIES[:] + custom
    # De-duplicate while preserving order.
    seen = set()
    out = []
    for a in pool:
        key = a.lower()
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out


def spin_wheel(seconds: float = 2.2) -> None:
    frames = ["|", "/", "-", "\\"]
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        print("\rSpinning " + frames[i % len(frames)] + " ", end="")
        time.sleep(0.07)
        i += 1
    print("\rSpinning done!   ")


def countdown(total_seconds: int) -> None:
    print("\nCountdown started. Press Ctrl+C to stop early.")
    start = time.time()
    try:
        while True:
            elapsed = int(time.time() - start)
            remaining = max(0, total_seconds - elapsed)
            mins, secs = divmod(remaining, 60)
            print(f"\rTime left: {mins:02d}:{secs:02d}", end="")
            if remaining == 0:
                break
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopped. Your robot respects boundaries.")
        return
    print("\n\aTime! LunchRoulette complete.")


def main() -> int:
    print("LunchRoulette Timer")
    print("=" * 20)
    for line in WHEEL:
        print(line)

    minutes = ask_int("How many minutes do you have for lunch?", default=20)
    activities = ask_activities()

    spin_wheel()
    pick = random.choice(activities)

    # Make the chosen activity feel like a "result" on a wheel.
    print("\nYour lunch quest:")
    print(f"  -> {pick}")

    # Reserve a tiny buffer so the countdown isn't overly strict.
    buffer_seconds = 15
    total_seconds = max(60, minutes * 60 - buffer_seconds)
    countdown(total_seconds)

    print("\nRobot note: if you enjoyed this, run it again tomorrow for a new quest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
