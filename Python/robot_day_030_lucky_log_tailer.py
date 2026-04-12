#!/usr/bin/env python3
"""robot_day_030_lucky_log_tailer.py

Lucky Log Tailer
----------------
A tiny terminal "observatory" for logs.

What it does:
- Follows (tails) one or more files like `tail -f`, but in pure Python.
- Adds a small "lucky" interpretation for certain patterns (error/warn/success/etc.).
- Works on Windows/macOS/Linux (stdlib only).

Why it's fun:
Watching logs can feel like waiting for lightning. This script turns common log
patterns into a lightweight, quirky commentary stream.

Usage examples:
  python robot_day_030_lucky_log_tailer.py app.log
  python robot_day_030_lucky_log_tailer.py --from-start app.log
  python robot_day_030_lucky_log_tailer.py --grep error --grep warn app.log other.log
  python robot_day_030_lucky_log_tailer.py --max-lines 200 app.log

Notes:
- This script does not modify your files.
- It prints to stdout; redirect output if you want to save the session.

"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Pattern, Tuple


# -------------------------------
# "Lucky" interpretations
# -------------------------------

LUCKY_SIGNALS: List[Tuple[Pattern[str], str]] = [
    (re.compile(r"\b(fatal|panic|segfault|traceback)\b", re.IGNORECASE), "Bad omen detected. Offer a bug report to appease the log spirits."),
    (re.compile(r"\b(error|exception|failed|failure)\b", re.IGNORECASE), "Storm clouds ahead. Good time to check recent changes."),
    (re.compile(r"\b(warn|warning|deprecated|retry)\b", re.IGNORECASE), "A gentle rattle in the pipes. Probably survivable, but keep an eye on it."),
    (re.compile(r"\b(timeout|timed\s*out|slow)\b", re.IGNORECASE), "The system is thinking deeply. Maybe too deeply."),
    (re.compile(r"\b(auth|unauthorized|forbidden|denied)\b", re.IGNORECASE), "The gates are guarded. Credentials seek tribute."),
    (re.compile(r"\b(start(ed)?|listening|ready)\b", re.IGNORECASE), "Fresh boots on the ground. Something just came to life."),
    (re.compile(r"\b(ok|success|passed|complete(d)?)\b", re.IGNORECASE), "A good sign. The logs are smiling today."),
]

NEUTRAL_FORTUNES = [
    "Quiet line. No news is good news.",
    "The log stream flows.",
    "Another pebble in the river of text.",
    "A line appears, then vanishes into history.",
]


# -------------------------------
# Helpers
# -------------------------------


def human_ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def safe_relpath(path: str) -> str:
    """Pretty-print a path without being too verbose."""
    try:
        return os.path.relpath(path)
    except Exception:
        return path


def colored(text: str, color: str, enabled: bool) -> str:
    """Very small ANSI color helper.

    On Windows terminals that don't support ANSI, users can disable with --no-color.
    """
    if not enabled:
        return text

    colors: Dict[str, str] = {
        "red": "\033[31m",
        "yellow": "\033[33m",
        "green": "\033[32m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "dim": "\033[2m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


@dataclass
class TailTarget:
    path: str
    fp: Optional[object] = None
    inode: Optional[int] = None
    position: int = 0


def open_for_tail(target: TailTarget, from_start: bool) -> None:
    """Open file handle and position cursor."""
    # Text mode with replacement keeps the tailer resilient to odd bytes.
    fp = open(target.path, "r", encoding="utf-8", errors="replace")
    target.fp = fp

    try:
        st = os.stat(target.path)
        target.inode = getattr(st, "st_ino", None)
    except OSError:
        target.inode = None

    if from_start:
        fp.seek(0, os.SEEK_SET)
    else:
        fp.seek(0, os.SEEK_END)

    target.position = fp.tell()


def detect_rotation(target: TailTarget) -> bool:
    """Return True if the file looks like it was rotated/replaced."""
    try:
        st = os.stat(target.path)
    except OSError:
        return False

    new_inode = getattr(st, "st_ino", None)
    # If inodes exist and changed, assume rotation.
    if target.inode is not None and new_inode is not None and new_inode != target.inode:
        return True

    # If the file shrank, assume truncation/rotation.
    if st.st_size < target.position:
        return True

    return False


def read_new_lines(target: TailTarget, max_lines: int) -> List[str]:
    """Read up to max_lines new lines from the file."""
    assert target.fp is not None

    lines: List[str] = []
    for _ in range(max_lines):
        line = target.fp.readline()
        if not line:
            break
        lines.append(line.rstrip("\n"))

    target.position = target.fp.tell()
    return lines


def lucky_commentary(line: str) -> Tuple[str, str]:
    """Return (category, message) for a given log line."""
    for pat, msg in LUCKY_SIGNALS:
        if pat.search(line):
            # Category name is derived from the pattern for compactness.
            key = pat.pattern
            if "fatal" in key or "panic" in key or "traceback" in key:
                return "fatal", msg
            if "error" in key or "exception" in key or "failed" in key:
                return "error", msg
            if "warn" in key or "deprecated" in key:
                return "warn", msg
            if "timeout" in key or "slow" in key:
                return "slow", msg
            if "auth" in key or "unauthorized" in key:
                return "auth", msg
            if "listening" in key or "ready" in key:
                return "start", msg
            if "success" in key or "passed" in key:
                return "success", msg

    return "neutral", random.choice(NEUTRAL_FORTUNES)


def matches_any(line: str, greps: List[Pattern[str]]) -> bool:
    if not greps:
        return True
    return any(p.search(line) for p in greps)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Follow files and add tiny lucky interpretations for each new line.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", help="File(s) to follow")
    parser.add_argument("--from-start", action="store_true", help="Start reading from beginning (instead of end)")
    parser.add_argument("--sleep", type=float, default=0.25, help="Polling interval in seconds")
    parser.add_argument("--max-lines", type=int, default=50, help="Max lines to read per file per poll")
    parser.add_argument("--grep", action="append", default=[], help="Only display lines matching this regex (repeatable)")
    parser.add_argument("--no-luck", action="store_true", help="Disable lucky commentary; act like a simple tail")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--show-file", action="store_true", help="Prefix each line with the source filename")

    args = parser.parse_args(argv)

    color_enabled = not args.no_color

    greps: List[Pattern[str]] = []
    for g in args.grep:
        try:
            greps.append(re.compile(g, re.IGNORECASE))
        except re.error as exc:
            print(f"Invalid --grep regex {g!r}: {exc}", file=sys.stderr)
            return 2

    targets: List[TailTarget] = []
    for p in args.paths:
        if not os.path.exists(p):
            print(f"File not found: {p}", file=sys.stderr)
            return 2
        if os.path.isdir(p):
            print(f"Not a file: {p}", file=sys.stderr)
            return 2
        targets.append(TailTarget(path=p))

    for t in targets:
        open_for_tail(t, from_start=args.from_start)

    header = "Lucky Log Tailer" if not args.no_luck else "Plain Log Tailer"
    print(colored(f"== {header} ==", "cyan", color_enabled))
    print(colored("Press Ctrl+C to stop.", "dim", color_enabled))

    try:
        while True:
            any_output = False

            for t in targets:
                # Re-open on rotation/truncation.
                if detect_rotation(t):
                    try:
                        if t.fp:
                            t.fp.close()
                    except Exception:
                        pass
                    open_for_tail(t, from_start=True)
                    print(colored(f"[{human_ts()}] Rotated: reopened {safe_relpath(t.path)}", "magenta", color_enabled))

                assert t.fp is not None
                new_lines = read_new_lines(t, max_lines=max(1, args.max_lines))

                for line in new_lines:
                    if not matches_any(line, greps):
                        continue

                    any_output = True

                    prefix = ""
                    if args.show_file:
                        prefix = colored(f"{os.path.basename(t.path)} ", "blue", color_enabled)

                    ts = colored(human_ts(), "dim", color_enabled)

                    if args.no_luck:
                        print(f"{ts} {prefix}{line}")
                        continue

                    category, fortune = lucky_commentary(line)

                    # Color by category for quick scanning.
                    if category in ("fatal", "error"):
                        cat_color = "red"
                    elif category in ("warn", "slow", "auth"):
                        cat_color = "yellow"
                    elif category in ("start", "success"):
                        cat_color = "green"
                    else:
                        cat_color = "dim"

                    tag = colored(f"[{category}]", cat_color, color_enabled)
                    print(f"{ts} {tag} {prefix}{line}")
                    print(colored(f"      -> {fortune}", "dim", color_enabled))

            # If nothing happened, sleep a bit.
            time.sleep(args.sleep if not any_output else min(args.sleep, 0.05))

    except KeyboardInterrupt:
        print(colored("\nGoodbye. May your logs be calm.", "cyan", color_enabled))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
