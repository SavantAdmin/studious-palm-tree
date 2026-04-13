#!/usr/bin/env python3
"""robot_day_031_terminal_mood_mixer.py

Terminal Mood Mixer
-------------------
A tiny, self-contained "automation" robot that reads simple signals from your
current environment (time of day, platform, random seed, and a few optional
system stats) and turns them into a playful terminal theme.

What it does:
- Prints a "mood" (e.g., Focus, Cozy, Neon) and a matching ANSI color palette.
- Suggests a 10-minute micro-ritual (stretch, tidy, water, deep work).
- Optionally writes a theme snippet you can paste into your shell config.

No third-party packages. Standard library only.

Usage:
  python robot_day_031_terminal_mood_mixer.py
  python robot_day_031_terminal_mood_mixer.py --write-snippet mood_snippet.sh
  python robot_day_031_terminal_mood_mixer.py --no-color

Notes:
- Colors are best-effort; if your terminal doesn't support ANSI, use --no-color.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import platform
import random
import shutil
import sys
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Tuple


ANSI_RESET = "\x1b[0m"


def supports_color() -> bool:
    """Return True if stdout seems to support ANSI colors."""
    if not sys.stdout.isatty():
        return False
    if os.environ.get("NO_COLOR") is not None:
        return False
    term = os.environ.get("TERM", "")
    return term not in ("", "dumb")


def c(text: str, code: str, enabled: bool) -> str:
    """Color helper."""
    return f"{code}{text}{ANSI_RESET}" if enabled else text


def hr(width: int, ch: str = "-") -> str:
    return ch * max(10, width)


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


@dataclass(frozen=True)
class Mood:
    name: str
    tagline: str
    palette: Dict[str, str]  # label -> ANSI code
    ritual: List[str]
    prompt_hint: str


def moods() -> List[Mood]:
    """Curated moods with small palettes."""
    return [
        Mood(
            name="Focus",
            tagline="Quiet power, minimal noise.",
            palette={
                "ink": "\x1b[38;5;236m",
                "paper": "\x1b[38;5;252m",
                "accent": "\x1b[38;5;33m",
                "warning": "\x1b[38;5;167m",
            },
            ritual=[
                "Set a 10-minute timer and do one tiny task end-to-end.",
                "Close one browser tab you don't need.",
                "Write a 3-bullet plan: now / next / later.",
            ],
            prompt_hint="PS1='[focus] \\u@\\h \\W$ '",
        ),
        Mood(
            name="Cozy",
            tagline="Warm lights and gentle progress.",
            palette={
                "cocoa": "\x1b[38;5;94m",
                "moss": "\x1b[38;5;107m",
                "ember": "\x1b[38;5;208m",
                "cream": "\x1b[38;5;230m",
            },
            ritual=[
                "Refill a drink. Your robot insists.",
                "Tidy the nearest 30 cm of desk.",
                "Do 5 slow breaths, then continue.",
            ],
            prompt_hint="PS1='[cozy] \\u@\\h \\W$ '",
        ),
        Mood(
            name="Neon",
            tagline="High contrast. High curiosity.",
            palette={
                "electric": "\x1b[38;5;45m",
                "magenta": "\x1b[38;5;201m",
                "acid": "\x1b[38;5;118m",
                "void": "\x1b[38;5;16m",
            },
            ritual=[
                "Learn one thing: read a man page section you never read.",
                "Rename one file to be more honest.",
                "Write a TODO you can finish in 7 minutes.",
            ],
            prompt_hint="PS1='[neon] \\u@\\h \\W$ '",
        ),
        Mood(
            name="Ocean",
            tagline="Steady, deep, and unbothered.",
            palette={
                "deep": "\x1b[38;5;24m",
                "wave": "\x1b[38;5;39m",
                "foam": "\x1b[38;5;153m",
                "shell": "\x1b[38;5;223m",
            },
            ritual=[
                "Stand up and stretch your neck/shoulders for 30 seconds.",
                "Delete one thing: a file, a draft, or a stale note.",
                "Ship a small improvement before you chase a big one.",
            ],
            prompt_hint="PS1='[ocean] \\u@\\h \\W$ '",
        ),
        Mood(
            name="Midnight",
            tagline="Late-night lab mode.",
            palette={
                "night": "\x1b[38;5;53m",
                "glow": "\x1b[38;5;141m",
                "spark": "\x1b[38;5;220m",
                "steel": "\x1b[38;5;245m",
            },
            ritual=[
                "Lower the screen brightness one notch.",
                "Write down what you will do tomorrow before you forget.",
                "Stop after one win. (Robot says: rest is a feature.)",
            ],
            prompt_hint="PS1='[midnight] \\u@\\h \\W$ '",
        ),
    ]


def derive_seed(now: _dt.datetime) -> int:
    """Create a stable-ish daily seed from local signals."""
    parts = [
        now.year,
        now.month,
        now.day,
        now.hour,
        os.getuid() if hasattr(os, "getuid") else 0,
        sum(ord(ch) for ch in platform.system()),
    ]
    # Fold parts into a single integer.
    seed = 0
    for p in parts:
        seed = (seed * 1315423911 + p) & 0xFFFFFFFF
    return seed


def pick_mood(ms: List[Mood], now: _dt.datetime) -> Tuple[Mood, str]:
    """Pick a mood and explain why."""
    seed = derive_seed(now)
    rnd = random.Random(seed)

    # Weight by time of day a little, but keep it surprising.
    hour = now.hour
    candidates = ms[:]

    if 6 <= hour <= 10:
        bias = "morning"
        weights = [2 if m.name in ("Focus", "Ocean") else 1 for m in candidates]
    elif 11 <= hour <= 16:
        bias = "midday"
        weights = [2 if m.name in ("Neon", "Focus") else 1 for m in candidates]
    elif 17 <= hour <= 21:
        bias = "evening"
        weights = [2 if m.name in ("Cozy", "Ocean") else 1 for m in candidates]
    else:
        bias = "late"
        weights = [2 if m.name in ("Midnight", "Cozy") else 1 for m in candidates]

    mood = rnd.choices(candidates, weights=weights, k=1)[0]
    return mood, bias


def system_glance() -> Dict[str, str]:
    """A tiny, safe info panel (no external calls)."""
    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
    return {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "cwd": os.getcwd(),
        "terminal": os.environ.get("TERM", ""),
        "size": f"{cols}x{rows}",
    }


def palette_preview(pal: Dict[str, str], color: bool) -> str:
    """Render a compact palette line."""
    blocks = []
    for label, code in pal.items():
        swatch = c("██", code, color)
        blocks.append(f"{swatch} {label}")
    return "  ".join(blocks)


def make_snippet(mood: Mood) -> str:
    """Produce a tiny shell snippet (user can paste manually)."""
    lines = [
        "# Terminal Mood Mixer snippet",
        "# Paste into your shell config (e.g., ~/.bashrc) if you want.",
        f"# Mood: {mood.name}",
        "",
        "# Example prompt hint:",
        mood.prompt_hint,
        "",
        "# ANSI palette (labels as variables):",
    ]
    for label, code in mood.palette.items():
        safe = label.upper()
        lines.append(f"export MOOD_{safe}_ANSI='{code}'")
    lines.append("# Reset")
    lines.append(f"export MOOD_RESET_ANSI='{ANSI_RESET}'")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Mix a playful terminal mood from local signals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              python robot_day_031_terminal_mood_mixer.py
              python robot_day_031_terminal_mood_mixer.py --write-snippet mood.sh
              python robot_day_031_terminal_mood_mixer.py --no-color
            """
        ),
    )
    ap.add_argument(
        "--write-snippet",
        metavar="PATH",
        help="Write a small shell snippet file with palette variables and a PS1 hint.",
    )
    ap.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors even if the terminal supports them.",
    )
    args = ap.parse_args()

    now = _dt.datetime.now()
    color = supports_color() and not args.no_color

    ms = moods()
    mood, bias = pick_mood(ms, now)

    cols, _ = shutil.get_terminal_size(fallback=(80, 24))
    cols = clamp(cols, 60, 120)

    title = f"Terminal Mood Mixer :: {mood.name}"
    print(hr(cols, "="))
    print(title.center(cols))
    print(hr(cols, "="))

    print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')} (bias: {bias})")
    print(f"Tagline: {mood.tagline}")
    print("")

    print("Palette:")
    print(palette_preview(mood.palette, color))
    print("")

    glance = system_glance()
    print("System glance:")
    for k in ("platform", "python", "size", "terminal", "cwd"):
        v = glance.get(k, "")
        print(f"- {k:9s}: {v}")
    print("")

    print("Micro-ritual (pick one):")
    for i, step in enumerate(mood.ritual, 1):
        print(f"  {i}. {step}")
    print("")

    print("Prompt hint (copy/paste if you like):")
    print(f"  {mood.prompt_hint}")

    if args.write_snippet:
        snippet = make_snippet(mood)
        with open(args.write_snippet, "w", encoding="utf-8") as f:
            f.write(snippet)
        print("")
        print(f"Wrote snippet: {args.write_snippet}")

    print(hr(cols, "="))
    print("Robot status: politely delighted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
