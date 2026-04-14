#!/usr/bin/env python3
"""robot_day_032_env_haiku_bot.py

Env Haiku Bot
-------------
A tiny robot that turns your environment variables into short, slightly dramatic haikus.

It works completely offline (stdlib only):
- Reads selected environment variables (or all, if you ask)
- Picks a "mood" based on variable names
- Generates one or more 3-line haikus (5-7-5 syllable-ish), plus a small banner

This is intentionally *approximate* "syllable counting" (English is hard), but it's
surprisingly fun.

Usage examples:
  python robot_day_032_env_haiku_bot.py
  python robot_day_032_env_haiku_bot.py --all
  python robot_day_032_env_haiku_bot.py --count 3
  python robot_day_032_env_haiku_bot.py --include PATH HOME SHELL
  python robot_day_032_env_haiku_bot.py --seed 123

Tip: Try it after opening a new terminal, or inside a CI run, and compare haikus.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import shutil
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Mood:
    name: str
    keywords: tuple[str, ...]
    lexicon: tuple[str, ...]


MOODS: tuple[Mood, ...] = (
    Mood(
        name="cosmic",
        keywords=("PATH", "PYTHON", "NODE", "JAVA", "RUST", "GO", "SDK", "HOME"),
        lexicon=(
            "starlight", "orbit", "comet", "quiet void", "nebula", "signal", "binary dawn",
            "distant hum", "thin air", "celestial", "soft gravity",
        ),
    ),
    Mood(
        name="bureaucratic",
        keywords=("USER", "USERNAME", "LOGNAME", "DOMAIN", "HOST", "COMPUTER"),
        lexicon=(
            "forms", "rubber stamp", "paper trail", "policy", "signature", "ledger",
            "approved", "denied", "pending", "compliance", "queue",
        ),
    ),
    Mood(
        name="garden",
        keywords=("TERM", "SHELL", "EDITOR", "PROMPT", "HIST", "LESS", "LANG"),
        lexicon=(
            "moss", "fern", "quiet soil", "morning dew", "root", "green hush",
            "soft wind", "pollen", "shade", "leaf", "birdsong",
        ),
    ),
    Mood(
        name="storm",
        keywords=("HTTP", "HTTPS", "PROXY", "SSL", "TLS", "CERT", "AWS", "GCP"),
        lexicon=(
            "thunder", "static", "rainline", "dark cloud", "surge", "wire", "tempest",
            "salt air", "wave", "black sky", "flicker",
        ),
    ),
    Mood(
        name="midnight",
        keywords=("TOKEN", "KEY", "SECRET", "PASS", "AUTH"),
        lexicon=(
            "locked door", "hushed code", "cipher", "hidden note", "keyhole",
            "shadow", "whisper", "sealed", "safe", "velvet dark",
        ),
    ),
)

FALLBACK_LEXICON: tuple[str, ...] = (
    "small machine", "paper moon", "soft beep", "tiny clock", "quiet loop", "warm circuit",
    "dusty window", "late coffee", "gentle error", "bright cursor", "slow sunrise",
)


def banner(title: str) -> str:
    width = min(72, shutil.get_terminal_size((72, 20)).columns)
    line = "=" * width
    centered = title.center(width)
    return f"{line}\n{centered}\n{line}"


def split_words(s: str) -> list[str]:
    # Split on underscores and case changes: FOO_BAR -> [FOO, BAR], MyVar -> [My, Var]
    s = s.strip()
    if not s:
        return []
    parts = re.split(r"[_\-\s]+", s)
    words: list[str] = []
    for p in parts:
        if not p:
            continue
        # CamelCase boundary splitting
        words.extend(re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+", p))
    return [w.lower() for w in words if w]


def approx_syllables(word: str) -> int:
    """Very small heuristic syllable counter.

    - Counts groups of vowels as syllables
    - Handles silent trailing 'e' roughly
    - Never returns 0
    """
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 1
    vowels = "aeiouy"
    groups = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            groups += 1
        prev_vowel = is_vowel

    # Heuristic: silent trailing 'e'
    if w.endswith("e") and groups > 1 and not w.endswith(("le", "ye")):
        groups -= 1

    return max(1, groups)


def approx_syllables_in_phrase(phrase: str) -> int:
    return sum(approx_syllables(w) for w in split_words(phrase))


def choose_mood(var_names: list[str]) -> Mood | None:
    upper = {n.upper() for n in var_names}
    best: tuple[int, Mood] | None = None
    for m in MOODS:
        score = sum(1 for k in m.keywords if k in upper)
        if score <= 0:
            continue
        if best is None or score > best[0]:
            best = (score, m)
    return best[1] if best else None


def choose_vars(include: list[str] | None, use_all: bool) -> dict[str, str]:
    env = dict(os.environ)

    if include:
        chosen = {}
        for key in include:
            if key in env:
                chosen[key] = env[key]
        return chosen

    if use_all:
        return env

    # Default: a small selection that tends to exist everywhere
    defaults = [
        "USER",
        "USERNAME",
        "LOGNAME",
        "HOME",
        "SHELL",
        "TERM",
        "LANG",
        "PATH",
        "PWD",
    ]
    chosen = {}
    for k in defaults:
        if k in env:
            chosen[k] = env[k]
    # If none of the defaults exist, fall back to a few arbitrary ones.
    if not chosen:
        for k in sorted(env)[:8]:
            chosen[k] = env[k]
    return chosen


def sanitize_value(value: str) -> str:
    # Keep it safe-ish for printing: show only a short, non-sensitive hint.
    # If it looks like a secret, redact.
    if re.search(r"(?i)(token|secret|password|passwd|api[_-]?key|private)", value):
        return "[redacted]"

    v = value.strip().replace("\n", " ")
    if len(v) > 32:
        return v[:29] + "..."
    return v


def line_from_var(key: str, value: str, lexicon: tuple[str, ...], rng: random.Random) -> str:
    """Create a poetic phrase seeded by key/value."""
    key_words = split_words(key)
    value_words = split_words(value)

    spice = rng.choice(lexicon)

    # Use pieces of the variable name as "anchors".
    anchors = [w for w in key_words if w not in ("env", "var", "path")]
    if not anchors:
        anchors = key_words[:]

    hint = (value_words[0] if value_words else "")

    fragments = []
    if anchors:
        fragments.append(rng.choice(anchors))
    if hint and rng.random() < 0.5:
        fragments.append(hint)
    if rng.random() < 0.75:
        fragments.append(spice)

    phrase = " ".join(fragments).strip()
    if not phrase:
        phrase = spice

    # Light punctuation variety
    if rng.random() < 0.2:
        phrase += ","
    elif rng.random() < 0.2:
        phrase += "."

    return phrase


def fit_line(target_syllables: int, candidates: list[str], rng: random.Random) -> str:
    """Pick / stitch candidates until we hit (approximately) the target syllable count."""
    rng.shuffle(candidates)

    chosen: list[str] = []
    sylls = 0

    for c in candidates:
        c_s = approx_syllables_in_phrase(c)
        if sylls + c_s > target_syllables + 1:
            continue
        chosen.append(c)
        sylls += c_s
        if sylls >= target_syllables - 1:
            break

    if not chosen:
        chosen = [rng.choice(FALLBACK_LEXICON)]

    line = " ".join(chosen)

    # If we're short, pad with tiny filler words.
    fillers = ["in", "the", "of", "and", "near", "under", "over", "with"]
    while approx_syllables_in_phrase(line) < target_syllables - 1 and len(line) < 64:
        line = line + " " + rng.choice(fillers)

    return line.strip()


def make_haiku(var_items: list[tuple[str, str]], mood: Mood | None, rng: random.Random) -> str:
    lexicon = mood.lexicon if mood else FALLBACK_LEXICON

    # Build a pool of candidate phrases from env vars.
    phrases: list[str] = []
    for k, v in var_items:
        phrases.append(line_from_var(k, v, lexicon, rng))

    # Add a few purely atmospheric phrases.
    phrases.extend(rng.sample(list(lexicon), k=min(4, len(lexicon))))

    l1 = fit_line(5, phrases[:], rng)
    l2 = fit_line(7, phrases[:], rng)
    l3 = fit_line(5, phrases[:], rng)

    # Add a small signature based on mood.
    tag = f"mood:{mood.name}" if mood else "mood:unknown"
    return f"{l1}\n{l2}\n{l3}\n({tag})"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description="Turn environment variables into tiny haikus (offline, stdlib-only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Notes:
              - Values are truncated and lightly redacted when they look secret-ish.
              - Syllable counts are approximate and intentionally whimsical.
            """
        ),
    )
    p.add_argument("--all", action="store_true", help="Use all environment variables")
    p.add_argument("--include", nargs="+", help="Only include these variables")
    p.add_argument("--count", type=int, default=1, help="Number of haikus to print")
    p.add_argument("--seed", type=int, help="Random seed (for repeatable haikus)")
    args = p.parse_args(argv)

    chosen = choose_vars(args.include, args.all)
    var_items = sorted((k, sanitize_value(v)) for k, v in chosen.items())

    if args.seed is None:
        # Seed with date + a touch of local entropy for daily variety.
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        seed = int(day) ^ (os.getpid() << 8)
    else:
        seed = args.seed

    rng = random.Random(seed)

    mood = choose_mood([k for k, _ in var_items])

    title = "Env Haiku Bot"
    print(banner(title))
    print(f"seed: {seed}")
    print(f"vars: {len(var_items)}")
    print(f"mood: {(mood.name if mood else 'unknown')}")
    print()

    # Preview the chosen variables (keys + sanitized values)
    print("Selected env hints:")
    for k, v in var_items[:20]:
        print(f"  {k}={v}")
    if len(var_items) > 20:
        print(f"  ... ({len(var_items) - 20} more)")
    print()

    for i in range(max(1, args.count)):
        if args.count > 1:
            print(f"Haiku {i + 1}/{args.count}:")
        # Vary selection per haiku so multiple prints aren't identical.
        sample = rng.sample(var_items, k=min(len(var_items), rng.randint(4, 10)))
        print(make_haiku(sample, mood, rng))
        if i != args.count - 1:
            print("\n---\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
