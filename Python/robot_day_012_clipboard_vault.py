#!/usr/bin/env python3
"""Clipboard Vault (Day 012)

A tiny, stdlib-only clipboard history helper.
- watch: polls your clipboard and saves new entries to a small JSON file
- list: shows saved entries
- pick: copies a chosen entry back into the clipboard

Clipboard access uses platform tools (best-effort):
macOS pbpaste/pbcopy, Windows PowerShell Get/Set-Clipboard,
Linux wl-copy/wl-paste or xclip/xsel.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HISTORY_PATH = Path.home() / ".clipboard_vault_history.json"
MAX_ITEMS = 50


def _run(cmd: list[str], inp: str | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, input=inp, text=True, capture_output=True, check=False)
    return p.returncode, p.stdout


def get_clipboard() -> str | None:
    if sys.platform == "darwin":
        rc, out = _run(["pbpaste"])
        return out if rc == 0 else None
    if sys.platform.startswith("win"):
        rc, out = _run(["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"])
        return out if rc == 0 else None
    for cmd in (["wl-paste", "-n"], ["xclip", "-o", "-selection", "clipboard"], ["xsel", "--clipboard", "--output"]):
        rc, out = _run(cmd)
        if rc == 0:
            return out
    return None


def set_clipboard(text: str) -> bool:
    if sys.platform == "darwin":
        rc, _ = _run(["pbcopy"], text)
        return rc == 0
    if sys.platform.startswith("win"):
        rc, _ = _run(["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ([Console]::In.ReadToEnd())"], text)
        return rc == 0
    for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
        rc, _ = _run(cmd, text)
        if rc == 0:
            return True
    return False


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(items: list[dict]) -> None:
    tmp = HISTORY_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(items[-MAX_ITEMS:], ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, HISTORY_PATH)


def norm(text: str) -> str:
    t = text.replace("\r\n", "\n").rstrip()
    return (t[:2000] + "\n... (truncated)") if len(t) > 2000 else t


def watch(interval: float) -> int:
    items, last = load_history(), None
    print("Watching clipboard. Ctrl+C to stop.")
    print(f"History: {HISTORY_PATH} (max {MAX_ITEMS})")
    try:
        while True:
            cur = get_clipboard()
            if cur is not None:
                cur = norm(cur)
                if cur and cur != last and (not items or items[-1].get("text") != cur):
                    last = cur
                    items.append({"ts": datetime.now().isoformat(timespec="seconds"), "text": cur})
                    save_history(items)
                    print(f"saved [{len(items):02d}] ({len(cur)} chars)")
            time.sleep(interval)
    except KeyboardInterrupt:
        return 0


def list_items() -> int:
    items = load_history()
    if not items:
        print("No history yet. Try: watch")
        return 0
    for i, it in enumerate(items, 1):
        first = it.get("text", "").splitlines()[0][:70]
        print(f"{i:02d}  {it.get('ts','?')}  {first}")
    return 0


def pick(index: int) -> int:
    items = load_history()
    if not (1 <= index <= len(items)):
        print("Index out of range.")
        return 2
    text = items[index - 1].get("text", "")
    if set_clipboard(text):
        print(f"Copied item {index:02d} back to clipboard.")
        return 0
    print("Could not set clipboard (missing platform tool?).")
    return 3


def main() -> int:
    ap = argparse.ArgumentParser(description="Clipboard Vault (Day 012)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("watch")
    w.add_argument("--interval", type=float, default=1.0)

    sub.add_parser("list")

    p = sub.add_parser("pick")
    p.add_argument("index", type=int)

    args = ap.parse_args()
    return watch(args.interval) if args.cmd == "watch" else (list_items() if args.cmd == "list" else pick(args.index))


if __name__ == "__main__":
    raise SystemExit(main())
