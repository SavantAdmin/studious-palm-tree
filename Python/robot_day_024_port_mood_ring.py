#!/usr/bin/env python3
"""Robot Day 024: Port Mood Ring

A tiny network "mood ring" for your localhost: it checks a handful of common ports
and prints a colorless, terminal-friendly status board.

Why it's quirky:
- It assigns each port a "mood" (sleepy, busy, mysterious...).
- It can optionally suggest what might be listening (best-effort, heuristic only).

Stdlib only. Safe: it only attempts TCP connects to 127.0.0.1.
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class PortCheck:
    port: int
    label: str
    mood_open: str
    mood_closed: str
    hint: str


DEFAULT_PORTS: List[PortCheck] = [
    PortCheck(22, "SSH", "alert", "sleepy", "remote shell"),
    PortCheck(80, "HTTP", "chatty", "quiet", "web server"),
    PortCheck(443, "HTTPS", "polished", "plain", "secure web server"),
    PortCheck(3000, "Dev", "busy", "idle", "common dev server"),
    PortCheck(5432, "Postgres", "thoughtful", "daydreaming", "database"),
    PortCheck(6379, "Redis", "zippy", "napping", "cache"),
    PortCheck(8000, "HTTP-alt", "chatty", "quiet", "python server"),
    PortCheck(8080, "Proxy", "bubbly", "still", "alt web/proxy"),
]


def try_connect(host: str, port: int, timeout: float) -> Tuple[bool, float]:
    """Return (is_open, elapsed_ms)."""
    start = time.perf_counter()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True, (time.perf_counter() - start) * 1000
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False, (time.perf_counter() - start) * 1000
    finally:
        try:
            s.close()
        except Exception:
            pass


def parse_ports(text: str) -> List[int]:
    ports: List[int] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a), int(b)
            if lo > hi:
                lo, hi = hi, lo
            ports.extend(list(range(lo, hi + 1)))
        else:
            ports.append(int(part))
    # unique, preserve order
    seen = set()
    out: List[int] = []
    for p in ports:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def pad(s: str, w: int) -> str:
    return s + " " * max(0, w - len(s))


def build_checks(custom_ports: Iterable[int]) -> List[PortCheck]:
    known = {c.port: c for c in DEFAULT_PORTS}
    checks: List[PortCheck] = []
    for p in custom_ports:
        if p in known:
            checks.append(known[p])
        else:
            checks.append(
                PortCheck(p, f"Port {p}", "mysterious", "unbothered", "unknown service")
            )
    return checks


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Localhost port mood ring")
    ap.add_argument(
        "--ports",
        default="",
        help="Comma list like 22,80,443,3000 or ranges like 8000-8005",
    )
    ap.add_argument("--host", default="127.0.0.1", help="Host to check (default: 127.0.0.1)")
    ap.add_argument("--timeout", type=float, default=0.35, help="Connect timeout seconds")
    ap.add_argument("--suggest", action="store_true", help="Show a human hint per port")
    args = ap.parse_args(argv)

    ports = parse_ports(args.ports) if args.ports else [c.port for c in DEFAULT_PORTS]
    checks = build_checks(ports)

    rows = []
    for c in checks:
        is_open, ms = try_connect(args.host, c.port, args.timeout)
        mood = c.mood_open if is_open else c.mood_closed
        state = "OPEN" if is_open else "closed"
        hint = f" — {c.hint}" if args.suggest else ""
        rows.append((c.port, c.label, state, mood, ms, hint))

    # Pretty-print
    w_label = max(len(r[1]) for r in rows)
    print("Port Mood Ring (localhost edition)")
    print("=" * 34)
    for port, label, state, mood, ms, hint in rows:
        print(
            f"{port:>5}  {pad(label, w_label)}  {pad(state, 6)}  mood:{pad(mood, 12)}  {ms:6.1f}ms{hint}"
        )

    open_count = sum(1 for r in rows if r[2] == "OPEN")
    print("-")
    if open_count == 0:
        print("Overall aura: tranquil (no open ports found)")
    elif open_count <= 2:
        print("Overall aura: focused (a couple of listeners)")
    else:
        print("Overall aura: bustling (several services are awake)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
