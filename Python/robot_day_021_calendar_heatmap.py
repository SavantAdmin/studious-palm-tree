#!/usr/bin/env python3
"""robot_day_021_calendar_heatmap.py

Print a GitHub-style activity heatmap for any date range.
Reads a CSV of events (date,count), buckets by week, and draws a compact
text heatmap you can paste into a README.

Stdlib-only.

Usage:
  python robot_day_021_calendar_heatmap.py --csv events.csv
  cat events.csv | python robot_day_021_calendar_heatmap.py
  python robot_day_021_calendar_heatmap.py --demo   # prints demo CSV

CSV format:
  YYYY-MM-DD,count
  2026-04-01,3
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime, timedelta

LEVELS = " .:-=+*#%@"  # 10 levels, low -> high


def parse_rows(fp) -> dict[date, int]:
    data: dict[date, int] = {}
    r = csv.reader(fp)
    for row in r:
        if not row or len(row) < 2:
            continue
        if row[0].strip().lower().startswith("date"):
            continue
        d = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
        data[d] = data.get(d, 0) + int(row[1])
    return data


def align_to_sunday(d: date) -> date:
    # Sunday=6 in weekday() where Monday=0
    return d - timedelta(days=(d.weekday() + 1) % 7)


def level_char(v: int, vmax: int) -> str:
    if vmax <= 0:
        return LEVELS[0]
    idx = int((len(LEVELS) - 1) * (v / vmax) + 0.5)
    return LEVELS[max(0, min(idx, len(LEVELS) - 1))]


def build_grid(data: dict[date, int], start: date, end: date) -> list[list[str]]:
    start_sun = align_to_sunday(start)
    end_sat = end + timedelta(days=(5 - end.weekday()) % 7)  # extend to Saturday
    vmax = max(data.values(), default=0)

    weeks: list[list[str]] = []
    cur = start_sun
    while cur <= end_sat:
        col: list[str] = []
        for i in range(7):
            d = cur + timedelta(days=i)
            if d < start or d > end:
                col.append(" ")
            else:
                col.append(level_char(data.get(d, 0), vmax))
        weeks.append(col)
        cur += timedelta(days=7)
    return weeks


def print_heatmap(weeks: list[list[str]], start: date, end: date) -> None:
    # Month initials along the top, aligned to week columns.
    month_line = []
    last_m = None
    cur = align_to_sunday(start)
    for _ in weeks:
        m = (cur + timedelta(days=6)).strftime("%b")
        month_line.append(m[0] if m != last_m else " ")
        last_m = m
        cur += timedelta(days=7)

    print(f"Calendar heatmap: {start.isoformat()} to {end.isoformat()}")
    print("Months:  " + "".join(month_line))

    labels = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    for row in range(7):
        print(labels[row] + " " + "".join(col[row] for col in weeks))

    print("\nLegend: ' ' out of range, then low -> high")
    print("        " + LEVELS)


def demo_csv() -> str:
    # Fake data: gentle rise over the last 10 weeks.
    today = date.today()
    start = today - timedelta(days=70)
    rows = ["date,count"]
    n = 0
    cur = start
    while cur <= today:
        n += 1
        rows.append(f"{cur.isoformat()},{(n // 7) % 9}")
        cur += timedelta(days=1)
    return "\n".join(rows) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Print a GitHub-style calendar heatmap from CSV.")
    p.add_argument("--csv", help="Path to CSV file (date,count). If omitted, read stdin.")
    p.add_argument("--start", help="Start date YYYY-MM-DD (default: min date in data)")
    p.add_argument("--end", help="End date YYYY-MM-DD (default: max date in data)")
    p.add_argument("--demo", action="store_true", help="Print a demo CSV to stdout and exit")
    args = p.parse_args()

    if args.demo:
        sys.stdout.write(demo_csv())
        return 0

    fp = open(args.csv, "r", encoding="utf-8", newline="") if args.csv else sys.stdin
    with fp:
        data = parse_rows(fp)

    if not data and (args.start is None or args.end is None):
        print("No data read. Provide --csv or pipe CSV on stdin.")
        return 2

    start = datetime.strptime(args.start, "%Y-%m-%d").date() if args.start else min(data)
    end = datetime.strptime(args.end, "%Y-%m-%d").date() if args.end else max(data)
    if end < start:
        start, end = end, start

    weeks = build_grid(data, start, end)
    print_heatmap(weeks, start, end)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
