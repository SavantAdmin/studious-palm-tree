#!/usr/bin/env python3
"""Robot Day 018 - Markdown Quest

A tiny, offline terminal adventure that builds a Markdown journal.
- Choose a short quest theme
- Answer a few prompts
- Writes/updates a Markdown file with a timestamped entry

Stdlib only. Works on Windows/macOS/Linux.
"""

from __future__ import annotations

import datetime as _dt
import os
import random
import textwrap


QUESTS = [
    "Catalog the library of lost brackets",
    "Map the tunnels beneath the coffee machine",
    "Negotiate peace with the rogue semicolons",
    "Recover the sacred README from the void",
    "Investigate the mysterious blinking cursor",
]

NPCS = [
    "a friendly lint spirit",
    "the terminal gremlin",
    "an overworked build server",
    "a sarcastic rubber duck",
    "the ancient sysadmin",
]

REWARDS = [
    "one (1) bonus tab",
    "a freshly cached dependency",
    "an impeccable commit message",
    "a typo that fixes itself",
    "the rarest artifact: focus",
]


def _hr(char: str = "-") -> str:
    return char * 60


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    ans = input(f"{prompt}{suffix}: ").strip()
    return ans if ans else (default or "")


def _pick(items: list[str], seed: int | None = None) -> str:
    rng = random.Random(seed)
    return rng.choice(items)


def build_story(seed: int | None = None) -> dict:
    quest = _pick(QUESTS, seed)
    npc = _pick(NPCS, None if seed is None else seed + 1)
    reward = _pick(REWARDS, None if seed is None else seed + 2)
    return {"quest": quest, "npc": npc, "reward": reward}


def render_story(story: dict, player: str, mood: str) -> str:
    lines = [
        f"Player: {player}",
        f"Mood: {mood}",
        f"Quest: {story['quest']}",
        f"Met: {story['npc']}",
        f"Reward: {story['reward']}",
    ]
    return "\n".join(lines)


def append_markdown(path: str, title: str, body: str) -> None:
    ts = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    entry = [
        f"## {title}",
        "",
        f"Timestamp: `{ts}`",
        "",
        "```",
        body,
        "```",
        "",
    ]

    new_file = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new_file:
            f.write("# Markdown Quest Journal\n\n")
            f.write("A tiny log of daily micro-adventures.\n\n")
        f.write("\n".join(entry))


def main() -> int:
    print(_hr("="))
    print("Markdown Quest (Robot Day 018)")
    print(_hr("="))

    default_player = os.environ.get("USER") or os.environ.get("USERNAME") or "Traveler"
    player = _ask("Name your adventurer", default_player)
    mood = _ask("Current mood", "curious")

    # Stable daily randomness: same date -> same quest (unless you provide a custom seed)
    today = _dt.date.today().isoformat()
    seed_str = _ask("Seed (optional, blank = daily)", "")
    seed = int(seed_str) if seed_str.isdigit() else sum(map(ord, today))

    story = build_story(seed)
    print("\n" + _hr())
    print(textwrap.fill(f"You set out to: {story['quest']}", width=60))
    print(textwrap.fill(f"Along the way you encounter {story['npc']}.", width=60))
    print(textwrap.fill(f"Against all odds, you earn {story['reward']}.", width=60))
    print(_hr() + "\n")

    highlight = _ask("One-line highlight from this quest")
    lesson = _ask("One tiny lesson learned")

    title = f"{today} - {player}'s quest"
    body = render_story(story, player=player, mood=mood)
    if highlight:
        body += f"\nHighlight: {highlight}"
    if lesson:
        body += f"\nLesson: {lesson}"

    out_path = os.path.join(os.getcwd(), "markdown_quest_journal.md")
    append_markdown(out_path, title=title, body=body)

    print(f"Wrote journal entry to: {out_path}")
    print("Tip: Commit the journal if you want to keep the saga in version control.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
