#!/usr/bin/env python3
"""Day 027 — DNS Haunt Detector

Resolves a hostname (via your system DNS) and prints a playful "haunt report":
IPv4/IPv6 results plus a small vibe meter.

Usage:
  python robot_day_027_dns_haunt_detector.py example.com
"""

import argparse
import random
import socket
import sys
import time

BANNERS = [
    "DNS Haunt Detector\n(quietly interrogating the ether)",
    "DNS Haunt Detector\n(listening for whispering packets)",
]
ADJECTIVES = [
    "restless",
    "quiet",
    "curious",
    "well-behaved",
    "mischievous",
    "dramatically silent",
    "surprisingly cooperative",
]


def _unique(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def resolve(host: str):
    ipv4, ipv6 = [], []
    infos = socket.getaddrinfo(host, None)
    for fam, _, _, _, sockaddr in infos:
        if fam == socket.AF_INET:
            ipv4.append(sockaddr[0])
        elif fam == socket.AF_INET6:
            ipv6.append(sockaddr[0])
    note = None
    fqdn = socket.getfqdn(host)
    if fqdn and fqdn.lower().rstrip(".") != host.lower().rstrip("."):
        note = fqdn
    return _unique(ipv4), _unique(ipv6), note


def bar(n: int, width: int = 18) -> str:
    n = max(0, min(n, width))
    return "[" + "#" * n + "-" * (width - n) + "]"


def score(ipv4, ipv6, note) -> int:
    # Fun, not scientific: reward answers (IPv6 slightly more, plus alias hint).
    s = 2 * len(ipv4) + 3 * len(ipv6) + (2 if note else 0)
    return min(18, s)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Resolve a hostname and print a playful haunt report.")
    ap.add_argument("host", help="Hostname to interrogate")
    ap.add_argument("--seed", type=int, default=None, help="Random seed for repeatable vibes")
    a = ap.parse_args(argv)
    if a.seed is not None:
        random.seed(a.seed)

    print(random.choice(BANNERS))
    for step in ("tuning antenna", "listening", "asking politely", "taking notes"):
        print(f"- {step}...", end="", flush=True)
        time.sleep(0.12)
        print(" ok")

    try:
        ipv4, ipv6, note = resolve(a.host.strip())
    except socket.gaierror as e:
        print("\nResult: no response from the ether.")
        print(f"Resolver said: {e}")
        return 2

    s = score(ipv4, ipv6, note)
    print("\nHaunt report\n============")
    print(f"Host: {a.host}")
    if note:
        print(f"Also answers to: {note}")
    print(f"Presence level: {bar(s)}  {s}/18")
    print(f"Vibe: {random.choice(ADJECTIVES)}")

    if ipv4:
        print("\nIPv4 footprints")
        for ip in ipv4:
            print(f"  - {ip}")
    if ipv6:
        print("\nIPv6 footprints")
        for ip in ipv6:
            print(f"  - {ip}")
    if not ipv4 and not ipv6:
        print("\nNo IPs returned. Either the host is shy, or DNS is having a nap.")

    print("\nNext moves")
    print("- Try ping/traceroute/nslookup (outside this bot)")
    print("- If this is your domain, confirm your DNS records at the provider")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
