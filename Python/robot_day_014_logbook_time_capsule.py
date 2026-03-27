"""Robot Day 014: Logbook Time Capsule

Theme: Personal log / time-capsule writer (local, stdlib-only).

What it does:
- Appends a timestamped "capsule entry" to a local text file.
- Shows a fun summary: today's entry count and the last few entries.
- Adds a tiny deterministic "mood gauge" based on the date (no randomness needed).

Why it's robot-y:
It reliably records tiny human moments with timestamps, like a friendly automation clerk.

Run:
  python robot_day_014_logbook_time_capsule.py

Tip:
  Set CAPSULE_FILE env var to change the output file location.
"""

from __future__ import annotations

import datetime as _dt
import os
import textwrap


MOODS = [
    "focused",
    "curious",
    "caffeinated",
    "methodical",
    "sparkly-brained",
    "quietly determined",
    "unreasonably optimistic",
    "mischief-managed",
]


def capsule_path() -> str:
    default = os.path.join(os.path.dirname(__file__), "time_capsule.log")
    return os.environ.get("CAPSULE_FILE", default)


def mood_for(date: _dt.date) -> str:
    # Deterministic "mood" so the same day always gets the same vibe.
    idx = (date.toordinal() * 7 + date.day * 13) % len(MOODS)
    return MOODS[idx]


def append_entry(path: str, when: _dt.datetime, entry: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    stamp = when.strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {entry.strip()}\n")


def read_entries(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def entries_today(entries: list[str], today: _dt.date) -> int:
    prefix = today.strftime("[%Y-%m-%d")
    return sum(1 for e in entries if e.startswith(prefix))


def main() -> None:
    now = _dt.datetime.now()
    today = now.date()
    path = capsule_path()

    print("Logbook Time Capsule (Robot Day 014)")
    print(f"Today feels: {mood_for(today)}")
    print(f"Capsule file: {path}")
    print("\nWrite a short entry. End with an empty line.")

    lines: list[str] = []
    while True:
        line = input("> ")
        if not line.strip():
            break
        lines.append(line)

    entry = " ".join(l.strip() for l in lines).strip()
    if not entry:
        print("No entry recorded. That's fine; the robot won't judge.")
        return

    wrapped = " ".join(textwrap.wrap(entry, width=120))
    append_entry(path, now, wrapped)

    entries = read_entries(path)
    print("\nRecorded.")
    print(f"Entries today: {entries_today(entries, today)}")

    tail_n = 5
    print(f"\nLast {min(tail_n, len(entries))} entr{'y' if min(tail_n, len(entries)) == 1 else 'ies'}:")
    for e in entries[-tail_n:]:
        print("  " + e)


if __name__ == "__main__":
    main()
