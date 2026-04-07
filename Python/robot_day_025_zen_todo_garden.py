#!/usr/bin/env python3
"""Robot Day 025: Zen To-Do Garden

Tiny terminal to-do list: finish tasks to earn seeds; 3 seeds grow an ASCII plant.
State is stored in a JSON file next to this script. Stdlib only.
"""

import json, random, time
from datetime import datetime
from pathlib import Path

F = Path(__file__).with_suffix(".json")
PLANTS = [("sprout","  .\n _|_\n"),("cactus"," _\n|_|\n | \n"),("tulip"," .-.\n(   )\n `-'\n  |\n"),
          ("bonsai","  _\n / )\n/ /\n\/\n"),("mushroom"," ___\n(___)\n  |\n")]
NAMES = ["Calm Fern","Brave Bean","Quiet Ivy","Neat Nettle","Stoic Sprout"]

now = lambda: datetime.now().replace(microsecond=0).isoformat()

def load():
    if not F.exists(): return {"tasks":[],"seeds":0,"plants":[]}
    try: return json.loads(F.read_text(encoding="utf-8"))
    except Exception:
        F.replace(F.with_suffix(f".broken.{int(time.time())}.json"))
        return {"tasks":[],"seeds":0,"plants":[]}

def save(s): F.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")

def garden(s):
    plants, seeds = s.get("plants", [])[-12:], int(s.get("seeds", 0))
    print("Your garden:")
    if not plants: print("  (empty plot)")
    for i,p in enumerate(plants,1):
        art = next((a for n,a in PLANTS if n==p.get("kind")), "?")
        print(f"  {i:02d}. {p.get('name','(nameless)')} [{p.get('kind','?')}]\n" + "\n".join("      "+ln for ln in art.splitlines()))
    print(f"\nSeeds in pocket: {seeds}" + (" (enough to grow a plant!)" if seeds>=3 else "") + "\n")

def tasks(s):
    t = s.get("tasks", [])
    if not t: print("No tasks yet. Add one.\n"); return
    print("Tasks:")
    for i,x in enumerate(t,1):
        print(f"  {i:02d}. [{'x' if x.get('done') else ' '}] {x.get('text','')}")
    print()

def add(s):
    text = input("New task: ").strip()
    if not text: print("No task added.\n"); return
    s.setdefault("tasks", []).append({"text":text,"created":now(),"done":False,"done_at":None}); save(s)
    print("Added.\n")

def done(s):
    if not s.get("tasks"): print("No tasks to complete.\n"); return
    tasks(s)
    raw = input("Complete which task number? ").strip()
    if not raw.isdigit(): print("Not a number.\n"); return
    i = int(raw)-1
    if i<0 or i>=len(s["tasks"]): print("Out of range.\n"); return
    if s["tasks"][i].get("done"): print("Already complete.\n"); return
    s["tasks"][i]["done"] = True; s["tasks"][i]["done_at"] = now(); s["seeds"] = int(s.get("seeds",0))+1
    save(s); print("Completed! You earned a seed (+1).\n")

def grow(s):
    seeds = int(s.get("seeds",0))
    if seeds<3: print("You need 3 seeds to grow a plant.\n"); return
    kind, art = random.choice(PLANTS)
    default = random.choice(NAMES)
    name = input(f"Name your new {kind} (Enter for '{default}'): ").strip() or default
    s["seeds"] = seeds-3; s.setdefault("plants", []).append({"kind":kind,"name":name,"grown_at":now()}); save(s)
    print("\nIt grows..."); time.sleep(0.15)
    for ln in art.splitlines(): print("  "+ln); time.sleep(0.05)
    print(f"\nWelcome, {name}.\n")

def prune(s):
    before = len(s.get("tasks", []))
    s["tasks"] = [t for t in s.get("tasks", []) if not t.get("done")]; save(s)
    print(f"Pruned {before-len(s['tasks'])} completed task(s).\n")

def pause(): input("Press Enter to continue...")

def main():
    while True:
        s = load()
        print("\n=== Zen To-Do Garden ===\nComplete tasks -> earn seeds -> grow plants.\n")
        garden(s)
        print("Menu: 1) list  2) add  3) complete  4) grow  5) prune  0) exit")
        c = input("Choose: ").strip(); print()
        if c=="1": tasks(s)
        elif c=="2": add(s)
        elif c=="3": done(s)
        elif c=="4": grow(s)
        elif c=="5": prune(s)
        elif c=="0": print("Goodbye. Your garden remains in the JSON file.\n"); return
        else: print("Unknown choice.\n")
        pause()

if __name__ == "__main__": main()
