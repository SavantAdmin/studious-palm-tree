#!/usr/bin/env python3
"""Robot Day 006: Mini Quiz Bot

A tiny terminal trivia bot with a built-in question bank.

Features:
- Picks random questions (no network needed)
- Accepts flexible answers (case/whitespace-insensitive)
- Gives a final score and a short "robot verdict"

Usage:
  python robot_day_006_mini_quiz_bot.py
"""

from __future__ import annotations

import random
import re


QUESTIONS = [
    {
        "q": "What is the only even prime number?",
        "a": ["2", "two"],
        "hint": "It is the smallest prime.",
    },
    {
        "q": "In computing, what does CPU stand for?",
        "a": ["central processing unit"],
        "hint": "Three words: Central ____ Unit.",
    },
    {
        "q": "What planet is nicknamed the Red Planet?",
        "a": ["mars"],
        "hint": "It is the fourth planet from the Sun.",
    },
    {
        "q": "Which protocol is used to securely browse websites (starts with H)?",
        "a": ["https"],
        "hint": "HTTP plus one important letter.",
    },
    {
        "q": "What is the name of the file that Python commonly uses for dependencies?",
        "a": ["requirements.txt", "requirements"],
        "hint": "It ends with .txt.",
    },
    {
        "q": "What is the result of 2**3 in Python?",
        "a": ["8", "eight"],
        "hint": "It is 2 multiplied by itself 3 times.",
    },
    {
        "q": "What is the capital of Colombia?",
        "a": ["bogota", "bogotá"],
        "hint": "Starts with B.",
    },
    {
        "q": "In Git, what command is used to create a new branch (two words)?",
        "a": ["git branch"],
        "hint": "It starts with 'git'.",
    },
    {
        "q": "What does RAM stand for?",
        "a": ["random access memory"],
        "hint": "Three words: Random ____ Memory.",
    },
    {
        "q": "Which language is this script written in?",
        "a": ["python"],
        "hint": "It starts with P.",
    },
]


def norm(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def safe_input(prompt: str) -> str:
    """input() wrapper that returns an empty string if stdin ends."""
    try:
        return input(prompt)
    except EOFError:
        return ""


def ask_count() -> int:
    while True:
        raw = safe_input("How many questions (1-10) [5]: ").strip()
        if not raw:
            return 5
        if raw.isdigit() and 1 <= int(raw) <= 10:
            return int(raw)
        print("Please enter a number from 1 to 10.")


def verdict(score: int, total: int) -> str:
    if score == total:
        return "Flawless run. Your brain firmware is up to date."
    if score >= max(1, total - 1):
        return "Nearly perfect. Minor cosmic radiation detected."
    if score >= (total // 2):
        return "Solid effort. The robot approves of your persistence."
    return "Diagnostics: more snacks and practice recommended."


def main() -> int:
    print("\nMini Quiz Bot")
    print("-------------")
    total = ask_count()

    bank = QUESTIONS[:]  # copy
    random.shuffle(bank)
    chosen = bank[:total]

    score = 0
    for i, item in enumerate(chosen, start=1):
        print(f"\nQ{i}/{total}: {item['q']}")
        user = safe_input("> ")

        if norm(user) in {norm(a) for a in item["a"]}:
            print("Correct.")
            score += 1
            continue

        if safe_input("Hint? (y/N): ").strip().lower() in ("y", "yes"):
            print(f"Hint: {item['hint']}")
            user2 = safe_input("> ")
            if norm(user2) in {norm(a) for a in item["a"]}:
                print("Correct (with hint).")
                score += 1
            else:
                print(f"Nope. Answer: {item['a'][0]}")
        else:
            print(f"Answer: {item['a'][0]}")

    print("\nResults")
    print("-------")
    print(f"Score: {score}/{total}")
    print(verdict(score, total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
