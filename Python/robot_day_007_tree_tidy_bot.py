#!/usr/bin/env python3
"""Robot Day 007: Tree Tidy Bot

A tiny file organizer that suggests (or applies) moves based on extensions.
- Stdlib only
- Dry-run by default
- Optional --apply to actually move files

Usage:
  python robot_day_007_tree_tidy_bot.py
  python robot_day_007_tree_tidy_bot.py --apply --path ~/Downloads
"""

import argparse
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

EXT_TO_BUCKET = {
    ".pdf": "Docs", ".txt": "Docs", ".md": "Docs", ".docx": "Docs", ".pptx": "Docs", ".xlsx": "Docs",
    ".png": "Images", ".jpg": "Images", ".jpeg": "Images", ".gif": "Images", ".svg": "Images",
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives", ".7z": "Archives",
    ".py": "Code", ".js": "Code", ".ts": "Code", ".json": "Code", ".yml": "Code", ".ps1": "Code",
    ".mp3": "Media", ".wav": "Media", ".mp4": "Media", ".mov": "Media", ".mkv": "Media",
}


def bucket_for(p: Path) -> str:
    return EXT_TO_BUCKET.get(p.suffix.lower(), "Other")


def plan_moves(root: Path):
    # Only files directly under root (keeps behavior predictable).
    for p in sorted(root.iterdir()):
        if p.is_dir() or p.name.startswith("robot_day_"):
            continue
        bucket = bucket_for(p)
        dst = root / bucket / p.name
        if dst != p:
            yield p, dst


def pretty_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024


def main() -> int:
    ap = argparse.ArgumentParser(description="Suggest (or apply) a tidy-up plan for a folder.")
    ap.add_argument("--path", default=".", help="Folder to tidy (default: current directory)")
    ap.add_argument("--apply", action="store_true", help="Actually move files (default: dry-run)")
    args = ap.parse_args()

    root = Path(args.path).expanduser()
    if not root.is_dir():
        print(f"Nope: {root} is not a folder.")
        return 2

    moves = list(plan_moves(root))
    if not moves:
        print("All tidy already. Nothing to do.")
        return 0

    grouped = defaultdict(list)
    total = 0
    for src, dst in moves:
        grouped[dst.parent.name].append((src, dst))
        try:
            total += src.stat().st_size
        except OSError:
            pass

    print("Tree Tidy Bot: proposed plan")
    print(f"Folder : {root.resolve()}")
    print(f"Mode   : {'APPLY (moving files)' if args.apply else 'DRY-RUN (no changes)'}")
    print(f"Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    for bucket in sorted(grouped):
        print(f"[{bucket}]")
        for src, dst in grouped[bucket]:
            print(f"  {src.name} -> {bucket}/{dst.name}")
        print()

    print(f"Total files: {len(moves)} | Approx size: {pretty_size(total)}")
    if not args.apply:
        print("Tip: re-run with --apply to perform these moves.")
        return 0

    for src, dst in moves:
        dst.parent.mkdir(exist_ok=True)
        if dst.exists():
            stem, suf = dst.stem, dst.suffix
            i = 1
            while (dst.parent / f"{stem}__{i}{suf}").exists():
                i += 1
            dst = dst.parent / f"{stem}__{i}{suf}"
        shutil.move(str(src), str(dst))

    print("Done. Folder has been tidied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
