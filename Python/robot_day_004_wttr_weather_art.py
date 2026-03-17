#!/usr/bin/env python3
"""Robot Day 004: Weather Art (wttr.in)

A tiny terminal bot that fetches a compact weather readout for a location and
prints it inside a retro ASCII "viewport".

- Stdlib only (urllib + json)
- Works offline-ish: if the network call fails, it prints a friendly fallback.

Usage:
  python robot_day_004_wttr_weather_art.py
  python robot_day_004_wttr_weather_art.py Bogota
  python robot_day_004_wttr_weather_art.py "New York"
"""

from __future__ import annotations

import sys
import textwrap
import urllib.parse
import urllib.request


def fetch_weather_text(location: str) -> str:
    """Return a short weather report from wttr.in (plain text)."""
    loc = urllib.parse.quote(location.strip() or "")
    # format=3 => one-liner: "City: +23C" etc.
    # m => metric units
    url = f"https://wttr.in/{loc}?format=3&m"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "studious-palm-tree-robot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        return r.read().decode("utf-8", errors="replace").strip()


def box(lines: list[str], width: int = 60) -> str:
    """Wrap lines in a simple ASCII box."""
    inner = width - 4
    top = "+" + "-" * (width - 2) + "+"
    out = [top]
    for ln in lines:
        for w in textwrap.wrap(ln, inner) or [""]:
            out.append("| " + w.ljust(inner) + " |")
    out.append(top)
    return "\n".join(out)


def main(argv: list[str]) -> int:
    location = " ".join(argv[1:]).strip() or "Bogota"

    try:
        report = fetch_weather_text(location)
        if not report:
            raise RuntimeError("Empty reply")
        mood = "Forecast acquired. Sky lasers calibrated."
    except Exception as e:
        report = f"{location}: (no signal)"
        mood = f"Could not reach wttr.in ({type(e).__name__}). Running on vibes."

    art = [
        "   .--.",
        " .(    ).",
        "(___.__)__)   tiny cloud module",
        "  '  '  '     (rain sold separately)",
        "",
        f"Weather: {report}",
        mood,
        "",
        "Tip: pass a location as an argument (e.g., 'Medellin' or 'Paris').",
    ]

    print(box(art, width=66))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
