#!/usr/bin/env python3
"""Motivational Boss Bot — your daily dose of absurd encouragement."""

import random
import sys
import time
from datetime import datetime

# ANSI color codes
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

ROBOT_FACE = f"""{CYAN}
    ╔══════════╗
    ║ ■■    ■■ ║
    ║    <>    ║
    ║  ╰════╯  ║
    ╚══════════╝
      │║║║║║│
   ╔══╧══════╧══╗
   ║  BOSS  BOT  ║
   ╚═════════════╝{RESET}
"""

SPEECHES = {
    "Monday": [
        "RISE AND GRIND, WARRIOR! Monday isn't a curse — it's your ORIGIN STORY!",
        "Monday called. I told it you're UNSTOPPABLE. It hung up in fear.",
        "Other people dread Mondays. YOU? You eat Mondays for BREAKFAST!",
    ],
    "Tuesday": [
        "Tuesday is Monday's cooler sibling and YOU are its favorite person!",
        "You showed up on a TUESDAY?! That's ELITE commitment right there!",
        "Tuesday tip: you're already 100% better than yesterday's version of you!",
    ],
    "Wednesday": [
        "HUMP DAY HERO! You've climbed the hill — now SURF down the other side!",
        "It's Wednesday, my dude. The week BOWS before your greatness!",
        "Midweek energy CHECK! You are the engine that COULD and DID!",
    ],
    "Thursday": [
        "Thursday is just Friday in DISGUISE and you cracked the code!",
        "Almost-Friday energy ACTIVATED. You are a MACHINE of productivity!",
        "Fun fact: Thursday was named after Thor. Coincidence? YOU ARE THUNDER!",
    ],
    "Friday": [
        "YOU SURVIVED THE WEEK, LEGEND! Friday salutes your magnificence!",
        "Friday called — it said you're the reason weekends were invented!",
        "TGIF? No. Thank GOD It's YOU! Friday is lucky to have you!",
    ],
    "Saturday": [
        "Working on a SATURDAY?! You absolute GALAXY-BRAINED overachiever!",
        "Saturday grind? Your dedication could power a SMALL CITY!",
        "Even weekends can't contain your AMBITION. Respect!",
    ],
    "Sunday": [
        "Sunday warrior! While others rest, you PREPARE FOR GREATNESS!",
        "A wild Sunday coder appears! Effectiveness level: OVER 9000!",
        "Sunday is for reflection… and you're reflecting PURE BRILLIANCE!",
    ],
}

CHALLENGES = [
    "Reply to every email with 'as per my last carrier pigeon'.",
    "Narrate your lunch break like a nature documentary.",
    "Give finger guns to three coworkers. Minimum.",
    "Refer to your desk as 'the command center' all day.",
    "End every sentence in a meeting with '…and that's the MAGIC.'",
    "Walk into a room like an action hero in slow motion (at least once).",
    "Compliment someone's font choice. Mean it.",
    "Drink water like you're in a sports drink commercial.",
    "Type aggressively on purpose so people think you're a hacker.",
    "Start one conversation with 'Listen, I've been thinking…' dramatically.",
]


def charging_bar():
    """Animated 'charging up' progress bar."""
    label = f"{YELLOW}{BOLD}⚡ CHARGING MOTIVATION BEAM{RESET} "
    bar_len = 25
    for i in range(bar_len + 1):
        filled = "█" * i
        empty = "░" * (bar_len - i)
        pct = int(i / bar_len * 100)
        sys.stdout.write(f"\r  {label}[{GREEN}{filled}{empty}{RESET}] {pct}%")
        sys.stdout.flush()
        time.sleep(0.04)
    print(f"  {GREEN}{BOLD}FULLY CHARGED!{RESET}\n")


def main():
    now = datetime.now()
    day = now.strftime("%A")
    hour = now.hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    print(ROBOT_FACE)
    print(f"  {BOLD}{MAGENTA}🤖 BOSS BOT v1.0 — {greeting}!{RESET}")
    print(f"  {CYAN}📅 It's {day}, {now.strftime('%B %d, %Y')} — {now.strftime('%I:%M %p')}{RESET}\n")

    charging_bar()

    speech = random.choice(SPEECHES.get(day, SPEECHES["Monday"]))
    print(f"  {BOLD}{YELLOW}💬 {speech}{RESET}\n")

    time.sleep(0.3)

    challenge = random.choice(CHALLENGES)
    print(f"  {GREEN}🎯 Today's challenge:{RESET} {BOLD}{challenge}{RESET}\n")

    print(f"  {CYAN}Now go out there and be UNREASONABLY GREAT.{RESET}")
    print(f"  {MAGENTA}— Boss Bot 🤖{RESET}\n")


if __name__ == "__main__":
    main()
