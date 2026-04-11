#!/usr/bin/env python3
"""Robot Day 029: Snippet Smith

A tiny interactive snippet organizer (stdlib only).

Commands:
  a add, l list, s show, f find, d delete, m export markdown, q quit

Storage: JSON file next to this script.
"""

import json
import os
import re
import sys
from datetime import datetime

DB = os.path.splitext(os.path.basename(__file__))[0] + ".json"


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load(path: str) -> dict:
    if not os.path.exists(path):
        return {"snippets": []}
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except json.JSONDecodeError:
        print("Database is corrupted. Rename and retry:", path)
        sys.exit(2)


def save(path: str, db: dict) -> None:
    tmp = path + ".tmp"
    json.dump(db, open(tmp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def multiline(hint: str) -> str:
    print(hint + "  (end with .done)")
    out = []
    while True:
        line = input()
        if line.strip() == ".done":
            return "\n".join(out).rstrip()
        out.append(line)


def tags(tag_text: str) -> list[str]:
    out = []
    for t in re.split(r"[, ]+", tag_text.strip()):
        t = t.strip().lower()
        if t and t not in out:
            out.append(t)
    return out


def add(db: dict) -> None:
    title = input("Title: ").strip()
    if not title:
        print("Cancelled.")
        return
    body = multiline("Paste snippet")
    if not body:
        print("Empty snippet; cancelled.")
        return
    ts = tags(input("Tags: "))
    nid = max([s["id"] for s in db["snippets"]] or [0]) + 1
    db["snippets"].append({"id": nid, "title": title, "tags": ts, "body": body, "created": now()})
    print(f"Added #{nid}.")


def listing(db: dict) -> None:
    if not db["snippets"]:
        print("No snippets.")
        return
    for s in sorted(db["snippets"], key=lambda x: x["id"]):
        t = ", ".join(s["tags"]) if s["tags"] else "-"
        print(f"#{s['id']:03d} {s['title']} [{t}] ({s['created']})")


def show(db: dict) -> None:
    try:
        sid = int(input("Id: ").strip())
    except ValueError:
        print("Not a number.")
        return
    s = next((x for x in db["snippets"] if x["id"] == sid), None)
    if not s:
        print("Not found.")
        return
    print("-" * 72)
    print(f"#{s['id']:03d} {s['title']}  Tags: {', '.join(s['tags']) if s['tags'] else '-'}")
    print(f"Created: {s['created']}")
    print("-" * 72)
    print(s["body"])
    print("-" * 72)


def find(db: dict) -> None:
    q = input("Keyword/tag: ").strip().lower()
    if not q:
        return
    hits = []
    for s in db["snippets"]:
        hay = (s["title"] + "\n" + s["body"]).lower()
        if q in hay or q in (t.lower() for t in s["tags"]):
            hits.append(s)
    if not hits:
        print("No matches.")
        return
    for s in hits:
        t = ", ".join(s["tags"]) if s["tags"] else "-"
        print(f"#{s['id']:03d} {s['title']} [{t}]")


def delete(db: dict) -> None:
    try:
        sid = int(input("Delete id: ").strip())
    except ValueError:
        print("Not a number.")
        return
    n0 = len(db["snippets"])
    db["snippets"] = [s for s in db["snippets"] if s["id"] != sid]
    print("Deleted." if len(db["snippets"]) != n0 else "Not found.")


def export_md(db: dict) -> None:
    out = input("Output (default snippets.md): ").strip() or "snippets.md"
    lines = ["# Snippet Smith Cheatsheet", "", f"Exported: {now()}", ""]
    for s in sorted(db["snippets"], key=lambda x: x["id"]):
        lines += [f"## #{s['id']:03d} {s['title']}"]
        if s["tags"]:
            lines += [f"Tags: {', '.join(s['tags'])}"]
        lines += [f"Created: {s['created']}", "", "```", s["body"], "```", ""]
    open(out, "w", encoding="utf-8").write("\n".join(lines).rstrip() + "\n")
    print("Wrote", out)


def main() -> int:
    path = os.path.join(os.path.dirname(__file__), DB)
    db = load(path)
    actions = {"a": add, "l": listing, "s": show, "f": find, "d": delete, "m": export_md}
    print("Snippet Smith: tiny terminal snippet organizer")
    print("DB:", path)
    while True:
        c = input("a/l/s/f/d/m/q > ").strip().lower()[:1]
        if c == "q":
            save(path, db)
            return 0
        fn = actions.get(c)
        if not fn:
            print("Unknown.")
            continue
        fn(db)
        save(path, db)


if __name__ == "__main__":
    raise SystemExit(main())
