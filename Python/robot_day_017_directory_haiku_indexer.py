#!/usr/bin/env python3
"""Robot Day 017: Directory Haiku Indexer

A tiny, quirky automation helper that:
- Walks a folder and builds a small index of files (name, size, mtime)
- For each file, generates a three-line "haiku" from the filename
- Writes the report to a timestamped .txt file

Stdlib only. Works on Windows/macOS/Linux.
"""

from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime

VOWELS = set("aeiouy")


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def rough_syllables(word: str) -> int:
    """Very rough syllable estimate: vowel-group counting with a few tweaks."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    s = len(groups)
    # Common silent-e tweak.
    if w.endswith("e") and not w.endswith(("le", "ye")) and s > 1:
        s -= 1
    return max(1, s)


def split_words(name: str) -> list[str]:
    base = os.path.splitext(os.path.basename(name))[0]
    base = base.replace("-", " ").replace("_", " ")
    # Split camelCase-ish.
    base = re.sub(r"([a-z])([A-Z])", r"\1 \2", base)
    words = [w for w in re.split(r"\s+", base) if w]
    if not words:
        return ["mystery"]
    return words


def pick_words_to_fit(words: list[str], target: int) -> str:
    """Pick words in order until we meet or slightly exceed target syllables."""
    out, s = [], 0
    for w in words:
        out.append(w)
        s += rough_syllables(w)
        if s >= target:
            break
    if not out:
        out = ["mystery"]
    return " ".join(out)


def haiku_for(filename: str) -> tuple[str, str, str]:
    words = split_words(filename)
    # Shuffle-ish without random: rotate by a small amount based on vowel count.
    rot = sum(c in VOWELS for c in "".join(words).lower()) % max(1, len(words))
    words = words[rot:] + words[:rot]

    l1 = pick_words_to_fit(words, 5)
    l2 = pick_words_to_fit(words[1:] + words[:1], 7)
    l3 = pick_words_to_fit(words[2:] + words[:2], 5)
    return (l1, l2, l3)


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    f = float(n)
    for u in units:
        if f < 1024.0 or u == units[-1]:
            return f"{f:.1f}{u}" if u != "B" else f"{int(f)}B"
        f /= 1024.0


def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common noise folders.
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", ".venv", "venv", "node_modules"}]
        for fn in sorted(filenames):
            yield os.path.join(dirpath, fn)


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print(f"Not a folder: {root}")
        return 2

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"directory_haiku_index_{stamp}.txt"
    out_path = os.path.join(os.getcwd(), out_name)

    files = list(iter_files(root))
    files = [p for p in files if os.path.abspath(p) != os.path.abspath(out_path)]

    lines = []
    lines.append(f"Directory Haiku Indexer")
    lines.append(f"Root: {root}")
    lines.append(f"When: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Files: {len(files)}")
    lines.append("" )

    for p in files[:200]:  # keep output small and readable
        try:
            st = os.stat(p)
        except OSError:
            continue
        rel = os.path.relpath(p, root)
        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
        l1, l2, l3 = haiku_for(rel)
        lines.append(f"- {rel}  ({human_bytes(st.st_size)}, {mtime})")
        lines.append(f"  {l1}")
        lines.append(f"  {l2}")
        lines.append(f"  {l3}")
        lines.append("")

    if len(files) > 200:
        lines.append(f"(Note: showing first 200 files; total is {len(files)}.)")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    print(f"Wrote: {out_path}")
    print("Tip: pass a folder path, e.g.:")
    print("  python robot_day_017_directory_haiku_indexer.py ~/Projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
