#!/usr/bin/env python3
"""Robot Day 023: Fortune Cookie Factory

A tiny terminal "fortune cookie" that can:
- print a random fortune
- add your own fortunes
- export them to a text file

It stores data in a small JSON file next to the script.
Stdlib only.
"""

from __future__ import annotations

import json
import os
import random
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "robot_day_023_fortunes.json")

DEFAULT_FORTUNES = [
    "A bug is just an undocumented feature with stage fright.",
    "Today you will refactor something you didn't write. Be brave.",
    "Your next cup of tea contains a surprisingly good idea.",
    "The robot approves of your folder structure.",
    "A small script will save you a large amount of time.",
    "You will find the missing semicolon in a place with no semicolons.",
    "A mysterious TODO will resolve itself once you name it properly.",
    "Your future self sends thanks (and requests more comments).",
]


def _load_fortunes() -> list[str]:
    if not os.path.exists(DATA_PATH):
        return DEFAULT_FORTUNES[:]
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("fortunes", [])
        return [str(x).strip() for x in items if str(x).strip()] or DEFAULT_FORTUNES[:]
    except Exception:
        # If the file is corrupted, don't punish the user. Start fresh.
        return DEFAULT_FORTUNES[:]


def _save_fortunes(fortunes: list[str]) -> None:
    payload = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "fortunes": fortunes,
    }
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _cookie_box(msg: str) -> str:
    # Build a cute ASCII cookie wrapper.
    lines = [line.rstrip() for line in msg.splitlines()] or [""]
    width = max(len(x) for x in lines)
    top = " ." + "-" * (width + 2) + "."
    bot = " '" + "-" * (width + 2) + "'"
    body = "\n".join(f" | {x.ljust(width)} |" for x in lines)
    return f"{top}\n{body}\n{bot}\n   \\   ^__^\n    \\  (oo)\\_______\n       (__)\\       )\\/\\\n           ||----w |\n           ||     ||"


def cmd_pick() -> int:
    fortunes = _load_fortunes()
    fortune = random.choice(fortunes)
    print(_cookie_box(fortune))
    return 0


def cmd_add(text: str) -> int:
    text = text.strip()
    if not text:
        print("Nothing to add. Try: add \"Your fortune here\"", file=sys.stderr)
        return 2

    fortunes = _load_fortunes()
    fortunes.append(text)
    # Keep it small and tidy.
    fortunes = fortunes[-200:]
    _save_fortunes(fortunes)
    print("Added. Your cookie jar now has", len(fortunes), "fortunes.")
    return 0


def cmd_export(path: str) -> int:
    fortunes = _load_fortunes()
    with open(path, "w", encoding="utf-8") as f:
        for i, ft in enumerate(fortunes, 1):
            f.write(f"{i:03d}. {ft}\n")
    print(f"Exported {len(fortunes)} fortunes to {path}")
    return 0


def cmd_list() -> int:
    fortunes = _load_fortunes()
    for i, ft in enumerate(fortunes, 1):
        print(f"{i:03d}. {ft}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) <= 1 or argv[1] in {"pick", "open"}:
        return cmd_pick()

    cmd = argv[1]
    if cmd == "add":
        if len(argv) < 3:
            print("Usage: add <fortune text>")
            return 2
        return cmd_add(" ".join(argv[2:]))

    if cmd == "export":
        out = argv[2] if len(argv) >= 3 else "fortunes.txt"
        return cmd_export(out)

    if cmd == "list":
        return cmd_list()

    print(
        "Fortune Cookie Factory\n"
        "\n"
        "Usage:\n"
        "  python robot_day_023_fortune_cookie_factory.py            # pick a random fortune\n"
        "  python robot_day_023_fortune_cookie_factory.py add <txt>  # add a fortune\n"
        "  python robot_day_023_fortune_cookie_factory.py list       # list all fortunes\n"
        "  python robot_day_023_fortune_cookie_factory.py export [file]  # export to text\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
