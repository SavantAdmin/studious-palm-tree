#!/usr/bin/env python3
"""Robot Day 026: ASCII Maze Runner

A tiny, self-contained terminal game:
- Generates a perfect maze (depth-first search)
- Lets you walk it with WASD
- Tracks steps and time

No third-party packages. Works in most terminals.
"""

import os
import random
import sys
import time

WALL = "#"
PATH = " "
YOU = "@"
EXIT = "X"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def make_maze(w, h, seed=None):
    """Return maze grid as list[list[str]] of size (2h+1) x (2w+1)."""
    if seed is not None:
        random.seed(seed)

    gw, gh = 2 * w + 1, 2 * h + 1
    g = [[WALL for _ in range(gw)] for _ in range(gh)]

    def carve(cx, cy):
        g[2 * cy + 1][2 * cx + 1] = PATH
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and g[2 * ny + 1][2 * nx + 1] == WALL:
                g[2 * cy + 1 + dy][2 * cx + 1 + dx] = PATH  # knock down wall
                carve(nx, ny)

    carve(0, 0)
    return g


def draw(g, px, py, steps, started_at, msg=""):
    clear()
    elapsed = time.time() - started_at
    print("ASCII Maze Runner  (WASD to move, Q to quit)")
    print(f"Steps: {steps}   Time: {elapsed:0.1f}s")
    if msg:
        print(msg)

    for y, row in enumerate(g):
        line = []
        for x, ch in enumerate(row):
            if (x, y) == (px, py):
                line.append(YOU)
            else:
                line.append(ch)
        print("".join(line))


def read_key():
    """Best-effort single-key reader. Falls back to input() on unsupported envs."""
    try:
        if os.name == "nt":
            import msvcrt

            return msvcrt.getwch()
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        return input("Move (W/A/S/D, Q): ").strip()[:1]


def main():
    w = 14
    h = 8

    g = make_maze(w, h)

    # Place exit at bottom-right cell.
    ex, ey = 2 * w - 1, 2 * h - 1
    g[ey][ex] = EXIT

    px, py = 1, 1
    steps = 0
    started_at = time.time()

    draw(g, px, py, steps, started_at, msg="Find the X.")

    while True:
        k = (read_key() or "").lower()
        if k == "q":
            draw(g, px, py, steps, started_at, msg="Quit. The maze will wait patiently.")
            return 0

        dx, dy = {"w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0)}.get(k, (0, 0))
        nx, ny = px + dx, py + dy

        if dx == dy == 0:
            draw(g, px, py, steps, started_at, msg="Use W/A/S/D (or Q).")
            continue

        if 0 <= ny < len(g) and 0 <= nx < len(g[0]) and g[ny][nx] != WALL:
            px, py = nx, ny
            steps += 1

        if (px, py) == (ex, ey):
            elapsed = time.time() - started_at
            draw(g, px, py, steps, started_at, msg=f"Escaped in {steps} steps and {elapsed:0.1f}s. Nice.")
            return 0

        draw(g, px, py, steps, started_at)


if __name__ == "__main__":
    raise SystemExit(main())
