"""robot_day_035_http_logbook_bot.py

A tiny terminal "logbook" that records notes and can optionally fetch a daily
prompt from a URL (using only the standard library's urllib).

Features
- Add timestamped entries to a local JSONL logbook file
- Search entries by keyword
- Show stats (entries per day, top tags)
- Optional daily prompt fetched over HTTP

Why it's robot-y:
- It turns quick human thoughts into a structured, searchable, append-only log.
- It can self-seed your day with a prompt fetched from the internet.

Stdlib only. Works on Python 3.9+.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator

DEFAULT_LOGBOOK = Path.home() / ".robot_logbook.jsonl"
DEFAULT_PROMPT_URL = "https://www.tronalddump.io/random/quote"  # fun, public JSON


def now_local_iso() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def parse_tags(text: str) -> list[str]:
    """Extract #tags from text."""
    return [t.lower() for t in re.findall(r"#([A-Za-z0-9_\-]{1,32})", text)]


def iter_entries(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # If a line is corrupted, skip it rather than crashing.
                continue


def append_entry(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_daily_prompt(url: str, timeout_s: float = 8.0) -> str:
    """Fetch a prompt from a URL.

    The default endpoint returns JSON. If the response isn't JSON, we'll show
    a truncated plain-text preview.
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "studious-palm-tree-robot/1.0 (+https://github.com/SavantAdmin/studious-palm-tree)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read(64_000)
        ctype = (resp.headers.get("Content-Type") or "").lower()

    # Try JSON first.
    try:
        data = json.loads(raw.decode("utf-8", errors="replace"))
        if isinstance(data, dict):
            # Try a few common "quote" shapes.
            for key in ("value", "quote", "text", "message"):
                if key in data and isinstance(data[key], str):
                    return data[key].strip()
            # tronalddump format: {"value": "..."}
        if isinstance(data, str):
            return data.strip()
    except Exception:
        pass

    # Fall back to plain text.
    preview = raw.decode("utf-8", errors="replace").strip()
    preview = re.sub(r"\s+", " ", preview)
    return preview[:240] + ("…" if len(preview) > 240 else "")


def cmd_prompt(args: argparse.Namespace) -> int:
    try:
        prompt = fetch_daily_prompt(args.url)
    except urllib.error.URLError as e:
        print(f"Could not fetch prompt: {e}")
        return 2

    print("Daily prompt:\n")
    print(textwrap.fill(prompt, width=78))
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    text = args.text
    if not text:
        # Interactive fallback (still non-blocking: user can Ctrl-D).
        print("Type your log entry. End with Ctrl-D (Unix/macOS) or Ctrl-Z then Enter (Windows).\n")
        try:
            text = sys.stdin.read().strip()
        except KeyboardInterrupt:
            return 130

    if not text:
        print("No text provided.")
        return 2

    entry = {
        "ts": now_local_iso(),
        "text": text.strip(),
        "tags": parse_tags(text),
        "meta": {
            "cwd": os.getcwd(),
            "host": os.uname().nodename if hasattr(os, "uname") else None,
        },
    }

    append_entry(args.logbook, entry)
    print(f"Added entry with {len(entry['tags'])} tag(s) to {args.logbook}.")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    q = args.query.lower().strip()
    if not q:
        print("Provide a search query.")
        return 2

    hits = []
    for e in iter_entries(args.logbook) or []:
        hay = (e.get("text") or "").lower()
        tags = " ".join(e.get("tags") or [])
        if q in hay or q in tags:
            hits.append(e)

    if not hits:
        print("No matches.")
        return 0

    # Show newest first
    hits = list(reversed(hits))
    for e in hits[: args.limit]:
        ts = e.get("ts", "?")
        tags = " ".join(f"#{t}" for t in (e.get("tags") or []))
        print(f"- {ts} {tags}\n  {textwrap.fill(e.get('text',''), width=76, subsequent_indent='  ')}\n")

    if len(hits) > args.limit:
        print(f"(Showing {args.limit} of {len(hits)} matches)")

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    per_day: dict[str, int] = defaultdict(int)
    tag_counts: Counter[str] = Counter()
    total = 0

    for e in iter_entries(args.logbook) or []:
        total += 1
        ts = e.get("ts") or ""
        day = ts.split("T")[0] if "T" in ts else "unknown"
        per_day[day] += 1
        tag_counts.update(e.get("tags") or [])

    if total == 0:
        print("No entries yet.")
        return 0

    print(f"Entries: {total}")

    # Show the last 10 days with activity (sorted).
    days_sorted = sorted(per_day.items())
    tail = days_sorted[-10:]
    print("\nRecent days:")
    for day, n in tail:
        bar = "#" * min(n, 40)
        print(f"  {day}: {n:3d} {bar}")

    if tag_counts:
        print("\nTop tags:")
        for tag, n in tag_counts.most_common(10):
            print(f"  #{tag}: {n}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="robot_logbook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Robot Logbook Bot

            Examples:
              python robot_day_035_http_logbook_bot.py prompt
              python robot_day_035_http_logbook_bot.py add "Shipped thing #work"
              python robot_day_035_http_logbook_bot.py search shipped --limit 5
              python robot_day_035_http_logbook_bot.py stats

            Tip: set LOGBOOK_PATH to keep multiple logbooks.
            """
        ).strip(),
    )

    default_path = Path(os.environ.get("LOGBOOK_PATH", str(DEFAULT_LOGBOOK))).expanduser()

    p.add_argument(
        "--logbook",
        type=Path,
        default=default_path,
        help=f"Path to JSONL logbook (default: {default_path})",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("prompt", help="Fetch and print a daily prompt from a URL")
    sp.add_argument("--url", default=DEFAULT_PROMPT_URL, help="Prompt URL (default: a random quote JSON)")
    sp.set_defaults(func=cmd_prompt)

    sa = sub.add_parser("add", help="Add a log entry (timestamped)")
    sa.add_argument("text", nargs="?", help="Entry text (if omitted, read from stdin)")
    sa.set_defaults(func=cmd_add)

    ss = sub.add_parser("search", help="Search entries by substring (text or tags)")
    ss.add_argument("query", help="Substring to match")
    ss.add_argument("--limit", type=int, default=10, help="Max results to show")
    ss.set_defaults(func=cmd_search)

    st = sub.add_parser("stats", help="Show basic stats about your logbook")
    st.set_defaults(func=cmd_stats)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
