#!/usr/bin/env python3
"""Robot Day 011: System Symphony

A quirky system info displayer that turns your machine stats into a tiny
"song" made of text bars. Stdlib only.

Run:
  python robot_day_011_system_symphony.py
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
import time


def term_width(default: int = 80) -> int:
    try:
        return shutil.get_terminal_size((default, 20)).columns
    except Exception:
        return default


def bar(label: str, value: str, width: int, ch: str = "#") -> str:
    """Draw a fixed-width bar whose fill depends on value length (silly but fun)."""
    # We avoid privileged system calls and keep it portable.
    fill = min(width, max(0, len(str(value))))
    return f"{label:<12} [{ch * fill}{'.' * (width - fill)}] {value}"


def bytes_human(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    f = float(n)
    for u in units:
        if f < 1024 or u == units[-1]:
            return f"{f:.1f}{u}" if u != "B" else f"{int(f)}{u}"
        f /= 1024
    return f"{n}B"


def uptime_guess() -> str:
    """Best-effort uptime without external deps.

    - On Linux, reads /proc/uptime.
    - Else, returns a polite shrug.
    """
    if os.path.exists("/proc/uptime"):
        try:
            with open("/proc/uptime", "r", encoding="utf-8") as f:
                seconds = float(f.read().split()[0])
            m, s = divmod(int(seconds), 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            return f"{d}d {h}h {m}m"
        except Exception:
            pass
    return "(unknown)"


def main() -> int:
    w = term_width()
    inner = max(10, min(40, w - 30))

    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Python": sys.version.split()[0],
        "Machine": platform.machine() or "(unknown)",
        "CPU": platform.processor() or "(unknown)",
        "Uptime": uptime_guess(),
        "CWD": os.getcwd(),
        "User": os.environ.get("USERNAME") or os.environ.get("USER") or "(unknown)",
    }

    total, used, free = shutil.disk_usage(os.getcwd())
    info["Disk"] = f"{bytes_human(used)}/{bytes_human(total)} used"

    title = "System Symphony"
    print("=" * min(w, 80))
    print(title.center(min(w, 80)))
    print("=" * min(w, 80))

    for k, v in info.items():
        print(bar(k, v, inner, ch="|") )

    # A tiny "tempo" line based on current time.
    t = time.localtime()
    tempo = (t.tm_sec % 12) + 1
    notes = "do re mi fa so la ti".split()
    melody = " ".join(notes[i % len(notes)] for i in range(tempo))
    print("-" * min(w, 80))
    print(f"Tempo: {tempo}  Melody: {melody}")
    print("Tip: Resize your terminal and run again for a different layout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
