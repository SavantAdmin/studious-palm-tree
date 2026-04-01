#!/usr/bin/env python3
"""robot_day_019_moon_phase_terminal.py

Moon Phase Terminal: a tiny astronomy-flavored terminal widget.

- Enter a date (or press Enter for today)
- Get the moon age (0..29.53 days), phase name, illumination estimate,
  and a small ASCII "moon".

Notes:
- This is an approximation (good enough for fun).
- Stdlib only.
"""

from __future__ import annotations

import datetime as _dt
import math

SYNODIC_MONTH = 29.53058867  # days


def _parse_date(s: str) -> _dt.date:
    s = s.strip()
    if not s:
        return _dt.date.today()
    try:
        return _dt.date.fromisoformat(s)
    except ValueError:
        raise SystemExit("Please enter a date as YYYY-MM-DD (example: 2026-04-01).")


def _julian_day(d: _dt.date) -> float:
    """Julian Day at 00:00 UTC for a Gregorian calendar date."""
    y, m, day = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + (a // 4)
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5
    return float(jd)


def _moon_age_days(d: _dt.date) -> float:
    """Approximate moon age in days since new moon."""
    # Reference new moon: 2000-01-06 18:14 UTC (commonly used approximation)
    ref = _dt.date(2000, 1, 6)
    days = _julian_day(d) - _julian_day(ref)
    age = days % SYNODIC_MONTH
    return age


def _illumination(age: float) -> float:
    """Approximate illuminated fraction (0..1) from moon age."""
    phase = 2 * math.pi * (age / SYNODIC_MONTH)
    return 0.5 * (1 - math.cos(phase))


def _phase_name(age: float) -> str:
    eighth = SYNODIC_MONTH / 8
    names = [
        "New Moon",
        "Waxing Crescent",
        "First Quarter",
        "Waxing Gibbous",
        "Full Moon",
        "Waning Gibbous",
        "Last Quarter",
        "Waning Crescent",
    ]
    idx = int((age + eighth / 2) // eighth) % 8
    return names[idx]


def _moon_art(age: float, width: int = 13, height: int = 7) -> str:
    """Render a small ASCII moon based on illumination and waxing/waning."""
    illum = _illumination(age)
    waxing = age < (SYNODIC_MONTH / 2)

    # Map illumination to a terminator offset (-1..1)
    # -1 = thin crescent, 0 = half, +1 = full
    offset = (2 * illum - 1)
    if not waxing:
        offset *= -1

    out = []
    rx, ry = 1.0, 1.0
    for j in range(height):
        y = (j - (height - 1) / 2) / ((height - 1) / 2)
        row = []
        for i in range(width):
            x = (i - (width - 1) / 2) / ((width - 1) / 2)
            inside = (x * x) / (rx * rx) + (y * y) / (ry * ry) <= 1.0
            if not inside:
                row.append(" ")
                continue

            # Terminator curve; tweak with y^2 to round it a bit.
            term = offset * (1 - 0.35 * y * y)
            lit = x >= -term
            row.append("#" if lit else ".")
        out.append("".join(row).rstrip())
    return "\n".join(out)


def main() -> None:
    print("Moon Phase Terminal")
    print("Enter a date as YYYY-MM-DD (or press Enter for today).")
    d = _parse_date(input("> "))

    age = _moon_age_days(d)
    illum = _illumination(age)
    name = _phase_name(age)

    print("\nDate:", d.isoformat())
    print(f"Moon age: {age:0.2f} days (0..{SYNODIC_MONTH:0.2f})")
    print("Phase:", name)
    print(f"Illumination: {illum*100:0.1f}%")
    print("\n" + _moon_art(age))

    # Tiny extra: next notable checkpoints (approx)
    checkpoints = [
        (0, "New Moon"),
        (SYNODIC_MONTH / 4, "First Quarter"),
        (SYNODIC_MONTH / 2, "Full Moon"),
        (3 * SYNODIC_MONTH / 4, "Last Quarter"),
    ]
    next_cp = None
    for t, label in checkpoints:
        if t > age:
            next_cp = (t, label)
            break
    if next_cp is None:
        next_cp = (SYNODIC_MONTH, "New Moon")

    days_until = next_cp[0] - age
    print(f"\nNext checkpoint: {next_cp[1]} in ~{days_until:0.1f} days")


if __name__ == "__main__":
    main()
