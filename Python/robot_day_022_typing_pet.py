#!/usr/bin/env python3
"""robot_day_022_typing_pet.py

A tiny terminal "pet" that reacts to your typing speed.

Type a passage (or your own thoughts), then press Enter on an empty line.
The robot measures your WPM and prints a mood + a small ASCII critter.
Optionally saves your sessions to a local JSONL log.

Stdlib-only.

Usage:
  python robot_day_022_typing_pet.py
  python robot_day_022_typing_pet.py --save
  python robot_day_022_typing_pet.py --log typing_pet_log.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime

PETS = {
    "sleepy": [
        r" ( -_-) zZ ",
        r" /|_|\\    ",
        r"  / \\     ",
    ],
    "curious": [
        r" (o_o) ?  ",
        r" /|_|\\   ",
        r"  / \\    ",
    ],
    "happy": [
        r" (^_^)    ",
        r" /|_|\\   ",
        r"  / \\    ",
    ],
    "hyper": [
        r" (O_O)!   ",
        r" /|_|\\   ",
        r"  / \\    ",
    ],
}


def mood_for_wpm(wpm: float) -> str:
    if wpm < 20:
        return "sleepy"
    if wpm < 40:
        return "curious"
    if wpm < 70:
        return "happy"
    return "hyper"


def read_multiline(prompt: str) -> tuple[str, float]:
    print(prompt)
    print("(Press Enter on an empty line to finish.)\n")

    lines: list[str] = []
    started = False
    t0 = 0.0

    while True:
        try:
            s = input("> ")
        except EOFError:
            break
        if not started:
            started = True
            t0 = time.time()
        if s.strip() == "":
            break
        lines.append(s)

    text = "\n".join(lines).strip()
    elapsed = max(0.001, time.time() - t0) if started else 0.0
    return text, elapsed


def count_words(text: str) -> int:
    # Simple, friendly word count: split on whitespace.
    return len([w for w in text.split() if w.strip()])


def print_pet(mood: str, wpm: float, words: int, secs: float) -> None:
    title = {
        "sleepy": "Slow and steady.",
        "curious": "Warming up!",
        "happy": "Nice pace!",
        "hyper": "Zoom!",
    }[mood]

    print("\nYour typing pet report")
    print("-" * 24)
    print(f"Words:   {words}")
    print(f"Time:    {secs:0.1f}s")
    print(f"Speed:   {wpm:0.1f} WPM")
    print(f"Mood:    {mood}  ({title})\n")
    for line in PETS[mood]:
        print(line)


def append_log(path: str, record: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="A terminal pet that reacts to your typing speed.")
    ap.add_argument("--save", action="store_true", help="Save session to a local JSONL log")
    ap.add_argument("--log", default="typing_pet_log.jsonl", help="Log file path (JSONL)")
    args = ap.parse_args()

    text, secs = read_multiline("Type something for your pet...")
    if not text:
        print("No text received. Your pet remains politely idle.")
        return 0

    words = count_words(text)
    minutes = max(1e-6, secs / 60.0)
    wpm = words / minutes
    mood = mood_for_wpm(wpm)

    print_pet(mood, wpm, words, secs)

    if args.save:
        rec = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "words": words,
            "seconds": round(secs, 3),
            "wpm": round(wpm, 2),
            "mood": mood,
        }
        append_log(args.log, rec)
        print(f"\nSaved to {args.log}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
