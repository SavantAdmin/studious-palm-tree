#!/usr/bin/env python3
"""robot_day_008_terminal_constellation.py

Terminal Constellation Robot

This tiny bot draws a randomized "night sky" in your terminal, then lets you
re-roll the stars or save the current sky to a text file.

Why it's fun:
- Uses only the Python standard library.
- Turns your terminal into a little ASCII planetarium.

Usage:
  python robot_day_008_terminal_constellation.py
"""

from __future__ import annotations

import os
import random
import textwrap
import time
from datetime import datetime


STAR_GLYPHS = [".", "*", "+", "x"]


def clear_screen() -> None:
    # Works on Windows + POSIX.
    os.system("cls" if os.name == "nt" else "clear")


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def ask_int(prompt: str, default: int, lo: int, hi: int) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            v = int(raw)
            return clamp(v, lo, hi)
        except ValueError:
            print(f"Please enter a whole number between {lo} and {hi}.")


def make_sky(width: int, height: int, density: float, seed: int) -> list[str]:
    rng = random.Random(seed)

    # Start with empty space.
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Sprinkle stars.
    for y in range(height):
        for x in range(width):
            if rng.random() < density:
                grid[y][x] = rng.choice(STAR_GLYPHS)

    # Add a couple of "constellations" (short connected lines).
    for _ in range(rng.randint(2, 4)):
        x = rng.randrange(0, width)
        y = rng.randrange(0, height)
        for _ in range(rng.randint(6, 14)):
            grid[y][x] = "#"
            dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)])
            x = clamp(x + dx, 0, width - 1)
            y = clamp(y + dy, 0, height - 1)

    # Add one "planet".
    px, py = rng.randrange(2, width - 2), rng.randrange(1, height - 1)
    grid[py][px] = "O"

    return ["".join(row) for row in grid]


def render(sky: list[str], seed: int, width: int, height: int, density: float) -> str:
    header = f"Terminal Constellation Robot  |  seed={seed}  size={width}x{height}  density={density:.3f}"
    line = "-" * len(header)
    return "\n".join([header, line, *sky, line])


def save_snapshot(rendered: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"constellation_{ts}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(rendered)
        f.write("\n")
    return filename


def main() -> int:
    clear_screen()
    print("Terminal Constellation Robot")
    print("----------------------------")
    print(textwrap.fill(
        "Pick a canvas size. If you're not sure, use the defaults and then just re-roll.",
        width=72,
    ))
    print()

    width = ask_int("Width (columns)", default=64, lo=20, hi=200)
    height = ask_int("Height (rows)", default=18, lo=8, hi=60)

    # Density: percent-ish of cells that become stars (not counting lines/planet).
    density_pct = ask_int("Star density (1-20)", default=8, lo=1, hi=20)
    density = density_pct / 200.0  # 0.005 .. 0.10

    seed = int(time.time())

    while True:
        clear_screen()
        sky = make_sky(width, height, density, seed)
        rendered = render(sky, seed, width, height, density)
        print(rendered)
        print("\n[r]eroll  [s]ave snapshot  [q]uit")
        choice = input("> ").strip().lower()[:1]

        if choice == "q":
            print("Goodnight. Your robot turns off the telescope.")
            return 0
        if choice == "s":
            fname = save_snapshot(rendered)
            print(f"Saved: {fname}")
            input("Press Enter to continue...")
            continue

        # Default: re-roll (new seed).
        seed += 1


if __name__ == "__main__":
    raise SystemExit(main())
