#!/usr/bin/env python3
"""robot_day_020_git_commit_fortune.py

A tiny robot that turns your current Git repo state into a fortune-cookie style
commit message suggestion.

- Stdlib-only
- Works best inside a Git repository

Usage:
  python robot_day_020_git_commit_fortune.py
  python robot_day_020_git_commit_fortune.py --apply   # writes message to .git/COMMIT_EDITMSG
"""

from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys
from datetime import datetime


FORTUNES = [
    "Ship it with calm confidence.",
    "Refactor gently; your future self is listening.",
    "A small commit today prevents a giant headache tomorrow.",
    "Name things well and the code will name you back.",
    "Tests are tiny lanterns in dark repos.",
    "Delete the unused; make room for the new.",
    "If it feels complex, it probably is. Simplify.",
    "Document the sharp edges before they cut someone.",
]

def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()

def in_git_repo() -> bool:
    try:
        sh(["git", "rev-parse", "--is-inside-work-tree"])
        return True
    except Exception:
        return False

def summarize_status() -> tuple[int, int, int]:
    """Return (staged, unstaged, untracked) counts."""
    out = sh(["git", "status", "--porcelain"])
    staged = unstaged = untracked = 0
    for line in out.splitlines():
        if line.startswith("??"):
            untracked += 1
            continue
        if len(line) >= 2:
            x, y = line[0], line[1]
            if x != " ":
                staged += 1
            if y != " ":
                unstaged += 1
    return staged, unstaged, untracked

def guess_scope() -> str:
    """Try to infer a scope from changed top-level folders."""
    out = sh(["git", "diff", "--name-only"])
    tops = []
    for p in out.splitlines():
        p = p.strip()
        if not p:
            continue
        top = p.split("/", 1)[0]
        if top and top not in tops:
            tops.append(top)
    if not tops:
        return "repo"
    if len(tops) == 1:
        return tops[0].lower()
    return "mixed"

def pick_verb(staged: int, unstaged: int, untracked: int) -> str:
    if untracked and not (staged or unstaged):
        return "add"
    if staged and not unstaged:
        return random.choice(["ship", "merge", "polish", "finalize"])
    if unstaged and not staged:
        return random.choice(["wip", "sketch", "draft"])
    return random.choice(["update", "tune", "adjust", "improve"])

def pick_object() -> str:
    return random.choice([
        "edges",
        "details",
        "flow",
        "logic",
        "docs",
        "defaults",
        "paths",
        "naming",
    ])

def format_message(scope: str, verb: str, obj: str, staged: int, unstaged: int, untracked: int) -> str:
    hint = f"{staged} staged, {unstaged} unstaged, {untracked} untracked"
    fortune = random.choice(FORTUNES)
    stamp = datetime.now().strftime("%Y-%m-%d")
    title = f"{verb}({scope}): {obj}"
    body = f"\nRepo omen: {hint}.\nFortune: {fortune}\nDate: {stamp}\n"
    return title + body

def write_commit_editmsg(msg: str) -> str:
    git_dir = sh(["git", "rev-parse", "--git-dir"])
    path = os.path.join(git_dir, "COMMIT_EDITMSG")
    with open(path, "w", encoding="utf-8") as f:
        f.write(msg)
    return path

def main() -> int:
    p = argparse.ArgumentParser(description="Generate a fortune-style commit message suggestion.")
    p.add_argument("--apply", action="store_true", help="Write message into .git/COMMIT_EDITMSG")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if not in_git_repo():
        print("Not inside a Git repository. Tip: cd into your repo and try again.")
        return 2

    staged, unstaged, untracked = summarize_status()
    scope = guess_scope()
    verb = pick_verb(staged, unstaged, untracked)
    obj = pick_object()

    # Nudge the verb when the repo is perfectly clean.
    if staged == 0 and unstaged == 0 and untracked == 0:
        verb = random.choice(["chore", "admire", "audit", "contemplate"])
        obj = random.choice(["cleanliness", "nothingness", "serenity"])  # fun on purpose

    msg = format_message(scope, verb, obj, staged, unstaged, untracked)
    print(msg)

    if args.apply:
        path = write_commit_editmsg(msg)
        print(f"\nWrote commit message to: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
