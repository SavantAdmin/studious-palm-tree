#!/usr/bin/env python3
"""Robot Day 010: Habit Streak Tracker (stdlib-only).

Stores habits + check-ins in a local JSON file next to this script, then shows
current/best streaks and a 7-day mini calendar. Run:
  python robot_day_010_habit_streak_tracker.py
"""

import datetime as dt
import json
import os
import sys

DATA_FILE = os.path.join(os.path.dirname(__file__), "habit_streaks.json")


def _load():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        out = {}
        for habit, dates in data.items():
            if isinstance(habit, str) and isinstance(dates, list):
                clean = sorted({dt.date.fromisoformat(d).isoformat() for d in dates if isinstance(d, str)})
                out[habit] = clean
        return out
    except Exception:
        return {}


def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def _streak(dates, end=None):
    if not dates:
        return 0
    seen = {dt.date.fromisoformat(d) for d in dates}
    cur = end or dt.date.today()
    n = 0
    while cur in seen:
        n += 1
        cur -= dt.timedelta(days=1)
    return n


def _best(dates):
    seq = sorted(dt.date.fromisoformat(d) for d in dates)
    best = cur = 0
    for i, d in enumerate(seq):
        cur = cur + 1 if i == 0 or (d - seq[i - 1]).days == 1 else 1
        best = max(best, cur)
    return best


def _week_bar(dates):
    seen = {dt.date.fromisoformat(d) for d in dates}
    end = dt.date.today()
    days = [end - dt.timedelta(days=i) for i in range(6, -1, -1)]
    glyphs = ["X" if d in seen else "." for d in days]
    labels = [d.strftime("%a")[0] for d in days]
    return "".join(glyphs) + "  " + "".join(labels)


def _status(data):
    print("\nHABIT STREAKS\n" + "=" * 50)
    if not data:
        print("No habits yet. Try: add <habit>\n")
        return
    for habit in sorted(data):
        dates = data[habit]
        last = dates[-1] if dates else "never"
        print(f"- {habit}")
        print(f"  current: {_streak(dates)} day(s)")
        print(f"  best:    {_best(dates)} day(s)")
        print(f"  last:    {last}")
        print(f"  week:    {_week_bar(dates)}\n")


def main(argv):
    data = _load()
    if len(argv) == 1:
        _status(data)
        print(
            "Commands:\n  status\n  add <habit>\n  done <habit> [YYYY-MM-DD]\n"
            "  rename <old> <new>\n  remove <habit>\n  help\n"
        )
        return 0

    cmd = argv[1].lower()
    if cmd in {"help", "-h", "--help"}:
        print(
            "Commands:\n  status\n  add <habit>\n  done <habit> [YYYY-MM-DD]\n"
            "  rename <old> <new>\n  remove <habit>\n  help\n"
        )
        return 0
    if cmd == "status":
        _status(data)
        return 0
    if cmd == "add" and len(argv) >= 3:
        habit = " ".join(argv[2:]).strip()
        if not habit:
            print("Habit name can't be empty.")
            return 2
        data.setdefault(habit, [])
        _save(data)
        print(f"Added: {habit}")
        return 0
    if cmd == "done" and len(argv) >= 3:
        habit = " ".join(argv[2:-1]).strip() if len(argv) >= 4 else argv[2].strip()
        if habit not in data:
            print(f"Unknown habit: {habit} (add it first)")
            return 2
        d = dt.date.today().isoformat() if len(argv) == 3 else dt.date.fromisoformat(argv[-1]).isoformat()
        data[habit] = sorted(set(data[habit] + [d]))
        _save(data)
        print(f"Done: {habit} on {d}")
        return 0
    if cmd == "rename" and len(argv) >= 4:
        old, new = argv[2], " ".join(argv[3:]).strip()
        if old not in data:
            print(f"Unknown habit: {old}")
            return 2
        if not new:
            print("New name can't be empty.")
            return 2
        data[new] = sorted(set(data.get(new, []) + data[old]))
        del data[old]
        _save(data)
        print(f"Renamed '{old}' to '{new}'")
        return 0
    if cmd == "remove" and len(argv) >= 3:
        habit = " ".join(argv[2:]).strip()
        if habit not in data:
            print(f"Unknown habit: {habit}")
            return 2
        del data[habit]
        _save(data)
        print(f"Removed: {habit}")
        return 0

    print("Unknown command or missing args.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
