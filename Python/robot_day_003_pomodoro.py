#!/usr/bin/env python3
"""robot_day_003_pomodoro.py

A tiny, self-contained terminal Pomodoro timer.
- No external deps (stdlib only)
- Works on macOS/Linux/Windows

Usage:
  python robot_day_003_pomodoro.py

Tips:
- Press Ctrl+C to stop early.
"""

from __future__ import annotations

import sys
import time


def fmt_seconds(total: int) -> str:
    m, s = divmod(max(0, total), 60)
    return f"{m:02d}:{s:02d}"


def ask_int(prompt: str, default: int, min_value: int = 1, max_value: int = 240) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            v = int(raw)
            if min_value <= v <= max_value:
                return v
        except ValueError:
            pass
        print(f"Please enter a whole number between {min_value} and {max_value}.")


def countdown(label: str, minutes: int) -> None:
    seconds = minutes * 60
    start = time.time()

    # We repaint a single line so it feels like a little robot dashboard.
    try:
        while True:
            elapsed = int(time.time() - start)
            remaining = seconds - elapsed
            if remaining <= 0:
                break
            bar_len = 20
            done = int(bar_len * (elapsed / seconds)) if seconds else bar_len
            bar = "#" * min(bar_len, done) + "-" * max(0, bar_len - done)
            msg = f"{label}: {fmt_seconds(remaining)} [{bar}]"
            sys.stdout.write("\r" + msg + " " * max(0, 6 - (len(msg) % 6)))
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped. Your robot respects boundaries.")
        raise

    sys.stdout.write("\r" + f"{label}: 00:00 [" + "#" * 20 + "]\n")
    sys.stdout.flush()


def beep() -> None:
    # Terminal bell is widely supported; harmless if ignored.
    sys.stdout.write("\a")
    sys.stdout.flush()


def main() -> int:
    print("\nPomodoro Robot")
    print("--------------")
    work = ask_int("Work minutes", default=25, min_value=1, max_value=180)
    rest = ask_int("Break minutes", default=5, min_value=1, max_value=60)
    rounds = ask_int("How many rounds", default=4, min_value=1, max_value=20)

    print("\nReady. When the timer finishes, you will hear a tiny terminal beep.")
    print("Press Ctrl+C anytime to exit.\n")

    try:
        for i in range(1, rounds + 1):
            print(f"Round {i}/{rounds}")
            countdown("FOCUS", work)
            beep()
            if i == rounds:
                break
            countdown("BREAK", rest)
            beep()
            print("")
    except KeyboardInterrupt:
        return 130

    print("All rounds complete. Good job, human.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
