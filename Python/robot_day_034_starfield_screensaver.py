#!/usr/bin/env python3
"""robot_day_034_starfield_screensaver.py

A tiny terminal "screensaver" that renders a drifting starfield.

Features:
- Deterministic (seeded) and configurable starfield
- Parallax layers (near stars move faster)
- Optional "warp" bursts
- Graceful exit on Ctrl+C

Stdlib only. Works best in a real terminal (not a tiny output pane).

Usage:
  python robot_day_034_starfield_screensaver.py
  python robot_day_034_starfield_screensaver.py --width 120 --height 40 --fps 30
  python robot_day_034_starfield_screensaver.py --seed 123 --no-warp

Tip:
  If your terminal is larger than the default size, pass --auto-size.
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import sys
import time
from dataclasses import dataclass


ANSI_HIDE_CURSOR = "\x1b[?25l"
ANSI_SHOW_CURSOR = "\x1b[?25h"
ANSI_CLEAR = "\x1b[2J"
ANSI_HOME = "\x1b[H"


@dataclass
class Star:
    """One star particle."""

    x: float
    y: float
    z: int  # layer depth: 0 (far) .. (layers-1) (near)


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Terminal starfield screensaver (stdlib-only).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument("--width", type=int, default=80, help="Render width in characters")
    p.add_argument("--height", type=int, default=24, help="Render height in characters")
    p.add_argument("--auto-size", action="store_true", help="Use terminal size")

    p.add_argument("--stars", type=int, default=260, help="Total star count")
    p.add_argument("--layers", type=int, default=3, help="Parallax layers")
    p.add_argument("--fps", type=float, default=24.0, help="Target frames per second")
    p.add_argument("--speed", type=float, default=0.65, help="Base drift speed")

    p.add_argument("--seed", type=int, default=None, help="Random seed (deterministic run)")
    p.add_argument(
        "--no-warp",
        action="store_true",
        help="Disable occasional warp bursts",
    )

    return p.parse_args()


def term_size_fallback(width: int, height: int) -> tuple[int, int]:
    """Use terminal size when possible; otherwise keep provided defaults."""

    try:
        cols, rows = shutil.get_terminal_size(fallback=(width, height))
        # Leave one row for safety; some terminals scroll if you draw on the last line.
        return max(20, cols), max(10, rows - 1)
    except Exception:
        return width, height


def spawn_star(rng: random.Random, width: int, height: int, layers: int) -> Star:
    """Create a star at a random position and depth."""

    return Star(
        x=rng.random() * (width - 1),
        y=rng.random() * (height - 1),
        z=rng.randrange(layers),
    )


def layer_char(z: int, layers: int, warp: bool) -> str:
    """Pick a character for a star based on depth."""

    # Far stars: subtle dots. Near stars: brighter characters.
    if warp:
        return "/" if z >= layers - 1 else "."

    if layers <= 1:
        return "*"

    # Map depth to density/brightness.
    if z == 0:
        return "."
    if z == layers - 1:
        return "*"
    return "+"


def layer_speed(z: int, layers: int, base_speed: float, warp: bool) -> float:
    """Parallax: nearer layers move faster."""

    if layers <= 1:
        mult = 1.0
    else:
        # z in [0, layers-1] -> multiplier in ~[0.5, 1.8]
        mult = 0.5 + (z / (layers - 1)) * 1.3

    if warp:
        mult *= 4.0

    return base_speed * mult


def render_frame(width: int, height: int, stars: list[Star], layers: int, warp: bool) -> str:
    """Render stars into a single string frame."""

    grid = [[" " for _ in range(width)] for _ in range(height)]

    for s in stars:
        x = int(s.x)
        y = int(s.y)
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = layer_char(s.z, layers, warp)

    # Add a tiny HUD in the corner (but keep it minimal).
    hud = "WARP" if warp else "STARFIELD"
    for i, ch in enumerate(hud[:width]):
        grid[0][i] = ch

    return "\n".join("".join(row) for row in grid)


def animate(args: argparse.Namespace) -> int:
    if args.seed is None:
        rng = random.Random()
    else:
        rng = random.Random(args.seed)

    width, height = (args.width, args.height)
    if args.auto_size:
        width, height = term_size_fallback(args.width, args.height)

    layers = clamp(args.layers, 1, 8)
    stars = [spawn_star(rng, width, height, layers) for _ in range(max(20, args.stars))]

    # Small random drift direction: like flying slightly "down-right".
    vx, vy = 1.0, 0.33

    frame_delay = 1.0 / max(1.0, args.fps)

    warp = False
    warp_until = 0.0
    next_warp_check = 0.0

    sys.stdout.write(ANSI_HIDE_CURSOR + ANSI_CLEAR)
    sys.stdout.flush()

    try:
        last = time.perf_counter()
        while True:
            now = time.perf_counter()
            dt = now - last
            last = now

            if not args.no_warp:
                # Occasionally trigger a short warp burst.
                if now >= next_warp_check:
                    next_warp_check = now + rng.uniform(1.2, 2.8)
                    if not warp and rng.random() < 0.12:
                        warp = True
                        warp_until = now + rng.uniform(0.35, 0.9)
                if warp and now >= warp_until:
                    warp = False

            for s in stars:
                sp = layer_speed(s.z, layers, args.speed, warp)
                s.x += vx * sp * dt * 18.0
                s.y += vy * sp * dt * 18.0

                # Wrap around edges for a seamless drift.
                if s.x >= width:
                    s.x -= width
                    s.y = rng.random() * (height - 1)
                if s.y >= height:
                    s.y -= height
                    s.x = rng.random() * (width - 1)

            frame = render_frame(width, height, stars, layers, warp)
            sys.stdout.write(ANSI_HOME + frame)
            sys.stdout.flush()

            # Basic frame pacing.
            elapsed = time.perf_counter() - now
            sleep_for = frame_delay - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        return 0
    finally:
        # Put the terminal back the way we found it.
        sys.stdout.write("\n" + ANSI_SHOW_CURSOR)
        sys.stdout.flush()


def main() -> int:
    args = parse_args()

    # If output isn't a terminal (piped to file), don't spam escape sequences.
    if not sys.stdout.isatty():
        sys.stderr.write("This script is meant to run in an interactive terminal.\n")
        return 2

    # On Windows, enable ANSI escape processing where possible.
    if os.name == "nt":
        try:
            import ctypes  # stdlib

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        except Exception:
            pass

    return animate(args)


if __name__ == "__main__":
    raise SystemExit(main())
