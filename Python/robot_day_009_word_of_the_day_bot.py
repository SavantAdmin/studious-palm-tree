#!/usr/bin/env python3
"""Robot Day 009: Word Of The Day Bot

A tiny terminal bot that fetches a random word + definition from a free API
and prints it like a little robot "bulletin".

- Stdlib only (urllib + json)
- If the network is unavailable, it falls back to a built-in mini word bank.

Usage:
  python robot_day_009_word_of_the_day_bot.py
  python robot_day_009_word_of_the_day_bot.py --history  # prints recent words

Notes:
- This script keeps a small local history file next to itself.
"""

from __future__ import annotations

import argparse
import json
import random
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path

HISTORY_LIMIT = 25
HISTORY_FILE = Path(__file__).with_suffix(".history.json")

FALLBACK = [
    {"word": "sonder", "definition": "The realization that each random passerby has a life as vivid and complex as your own."},
    {"word": "laconic", "definition": "Using very few words."},
    {"word": "susurrus", "definition": "A soft murmuring or rustling sound."},
    {"word": "mellifluous", "definition": "Sweet or musical; pleasant to hear."},
    {"word": "ephemeral", "definition": "Lasting for a very short time."},
]


def fetch_random_word() -> dict:
    """Fetch a word + definition using a public dictionary API."""
    url = "https://random-word-api.herokuapp.com/word?number=1"
    with urllib.request.urlopen(url, timeout=10) as r:
        word = json.loads(r.read().decode("utf-8"))[0]

    durl = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    with urllib.request.urlopen(durl, timeout=10) as r:
        data = json.loads(r.read().decode("utf-8"))

    # Try to pull the first definition we can find.
    meanings = data[0].get("meanings", [])
    for m in meanings:
        defs = m.get("definitions", [])
        if defs and defs[0].get("definition"):
            return {"word": word, "definition": defs[0]["definition"]}

    return {"word": word, "definition": "(No definition found.)"}


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(items: list[dict]) -> None:
    HISTORY_FILE.write_text(
        json.dumps(items[-HISTORY_LIMIT:], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def robot_panel(title: str, body: str) -> str:
    lines = textwrap.wrap(body, width=60) or [""]
    width = max(len(title), *(len(x) for x in lines)) + 4

    top = "+" + "-" * (width - 2) + "+"
    mid = f"| {title.ljust(width - 4)} |"
    sep = "+" + "-" * (width - 2) + "+"
    payload = "\n".join(f"| {x.ljust(width - 4)} |" for x in lines)
    bot = "+" + "-" * (width - 2) + "+"
    return "\n".join([top, mid, sep, payload, bot])


def main() -> int:
    ap = argparse.ArgumentParser(description="Word Of The Day Bot")
    ap.add_argument("--history", action="store_true", help="Print recent words")
    args = ap.parse_args()

    history = load_history()

    if args.history:
        if not history:
            print("No history yet. Run without --history to collect a word.")
            return 0
        print(robot_panel("Recent robot words", ", ".join(x["word"] for x in history[-10:])))
        return 0

    try:
        item = fetch_random_word()
        item["source"] = "dictionaryapi.dev"
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError):
        item = dict(random.choice(FALLBACK))
        item["source"] = "fallback"

    history.append({"word": item["word"], "ts": int(time.time())})
    save_history(history)

    title = f"Robot Bulletin: {item['word']}"
    body = f"Definition: {item['definition']}\n(From: {item['source']})"
    print(robot_panel(title, body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
