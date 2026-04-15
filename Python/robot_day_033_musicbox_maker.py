"""robot_day_033_musicbox_maker.py

Day 033 Robot Script: Musicbox Maker

A tiny terminal "music box" that composes and plays simple melodies.

Features
- Two built-in scales (major + minor) and a few preset riffs
- Random melody generation with a configurable seed
- Plays tones using only the Python standard library:
  - Windows: winsound.Beep
  - macOS/Linux: prints a time-synced note stream (no speaker control)
- Exports your melody to a compact text format you can re-play later

Why this exists
Sometimes automation should be a little whimsical: generate a melody in
seconds, save it as a tiny text file, and play it back when you need a
break.

Usage
  python robot_day_033_musicbox_maker.py --help

Notes
- On non-Windows platforms, the script cannot reliably produce audio with
  stdlib alone, so it uses a visual "player". The exported format still
  works everywhere.

No third-party packages required.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ------------------------------
# Music theory (tiny edition)
# ------------------------------

NOTE_OFFSETS: Dict[str, int] = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

SCALES: Dict[str, Sequence[int]] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
}

PRESETS: Dict[str, Dict[str, object]] = {
    "clockwork": {
        "scale": "minor",
        "steps": [0, 2, 4, 5, 4, 2, 0, 2, 4, 7, 4, 2],
        "durations": [1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 2],
        "bpm": 132,
    },
    "sunbeam": {
        "scale": "major",
        "steps": [0, 2, 4, 7, 4, 2, 0, 4, 5, 7, 9, 7, 5, 4],
        "durations": [1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2],
        "bpm": 120,
    },
    "morse": {
        "scale": "minor",
        "steps": [0, 0, 3, 0, 0, 3, 0, 5, 0],
        "durations": [1, 1, 2, 1, 1, 2, 1, 3, 4],
        "bpm": 160,
    },
}


@dataclass(frozen=True)
class Note:
    name: str
    freq_hz: int
    beats: float


def midi_to_freq_hz(midi_note: int) -> int:
    """Convert MIDI note number to frequency in Hz (rounded)."""
    return int(round(440.0 * (2.0 ** ((midi_note - 69) / 12.0))))


def note_name(root: str, octave: int) -> str:
    return f"{root}{octave}"


def build_scale_notes(root: str, octave: int, scale: str) -> List[Tuple[str, int]]:
    if root not in NOTE_OFFSETS:
        raise ValueError(f"Unknown root note: {root!r}. Try C, D#, Bb, etc.")
    if scale not in SCALES:
        raise ValueError(f"Unknown scale: {scale!r}. Try: {', '.join(SCALES)}")

    root_midi = 12 * (octave + 1) + NOTE_OFFSETS[root]  # MIDI C4 = 60
    notes: List[Tuple[str, int]] = []
    for step in SCALES[scale]:
        midi = root_midi + int(step)
        notes.append((note_name(root, octave) + f"+{step}", midi_to_freq_hz(midi)))
    return notes


# ------------------------------
# Melody generation + export
# ------------------------------


def generate_melody(
    root: str,
    octave: int,
    scale: str,
    length: int,
    seed: Optional[int],
    leaps: int,
) -> List[int]:
    """Return a list of scale indices (0..len(scale)-1)."""
    rng = random.Random(seed)
    degrees = list(range(len(SCALES[scale])))

    # Start somewhere musical (root, third, fifth).
    start_choices = [0, 2, 4] if len(degrees) >= 5 else degrees
    cur = rng.choice(start_choices)

    melody = [cur]
    for _ in range(length - 1):
        # Mostly move by step; sometimes leap.
        if rng.randint(1, 100) <= leaps:
            nxt = rng.choice(degrees)
        else:
            nxt = cur + rng.choice([-1, 1])
            nxt = max(0, min(nxt, len(degrees) - 1))
        melody.append(nxt)
        cur = nxt

    return melody


def durations_for_length(length: int, rng: random.Random) -> List[float]:
    """Generate durations in beats (1=quarter note-ish)."""
    choices = [0.5, 1.0, 1.0, 1.0, 1.5, 2.0]
    return [rng.choice(choices) for _ in range(length)]


def pack_song(
    root: str,
    octave: int,
    scale: str,
    bpm: int,
    degrees: Sequence[int],
    beats: Sequence[float],
) -> Dict[str, object]:
    return {
        "v": 1,
        "root": root,
        "octave": octave,
        "scale": scale,
        "bpm": bpm,
        "degrees": list(map(int, degrees)),
        "beats": list(map(float, beats)),
    }


def unpack_song(payload: Dict[str, object]) -> Tuple[str, int, str, int, List[int], List[float]]:
    return (
        str(payload["root"]),
        int(payload["octave"]),
        str(payload["scale"]),
        int(payload["bpm"]),
        list(map(int, payload["degrees"])),
        list(map(float, payload["beats"])),
    )


# ------------------------------
# Playback
# ------------------------------


def beat_seconds(bpm: int) -> float:
    return 60.0 / float(bpm)


def is_windows() -> bool:
    return os.name == "nt"


def play_windows(notes: Sequence[Note], bpm: int) -> None:
    import winsound  # Windows only

    spb = beat_seconds(bpm)
    for n in notes:
        ms = int(round(n.beats * spb * 1000.0))
        # winsound.Beep requires frequency in 37..32767
        freq = max(37, min(int(n.freq_hz), 32767))
        winsound.Beep(freq, max(ms, 30))


def play_visual(notes: Sequence[Note], bpm: int) -> None:
    spb = beat_seconds(bpm)
    print("\nVisual player (no audio available on this OS with stdlib only):")
    print("Press Ctrl+C to stop.\n")

    t0 = time.time()
    elapsed_beats = 0.0
    for n in notes:
        elapsed_beats += n.beats
        target = t0 + elapsed_beats * spb
        bar = "=" * max(1, int(n.freq_hz / 50))
        line = f"{n.name:<10} {n.freq_hz:>5} Hz |{bar}"
        print(line)
        # Sleep until the scheduled time for the end of this note.
        while True:
            now = time.time()
            remaining = target - now
            if remaining <= 0:
                break
            time.sleep(min(0.05, remaining))


def build_notes(root: str, octave: int, scale: str, degrees: Sequence[int], beats: Sequence[float]) -> List[Note]:
    scale_notes = build_scale_notes(root, octave, scale)
    out: List[Note] = []
    for d, b in zip(degrees, beats):
        d2 = max(0, min(int(d), len(scale_notes) - 1))
        name, freq = scale_notes[d2]
        out.append(Note(name=name, freq_hz=freq, beats=float(b)))
    return out


# ------------------------------
# CLI
# ------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Compose and play tiny terminal melodies using only the Python standard library.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--preset", choices=sorted(PRESETS), help="Play a built-in riff")
    mode.add_argument("--load", metavar="FILE", help="Load a previously exported song JSON")

    p.add_argument("--root", default="C", help="Root note (e.g., C, D#, Bb)")
    p.add_argument("--octave", type=int, default=4, help="Octave number (C4 is middle C)")
    p.add_argument("--scale", choices=sorted(SCALES), default="major", help="Scale flavor")

    p.add_argument("--bpm", type=int, default=128, help="Tempo")
    p.add_argument("--length", type=int, default=16, help="Notes to generate (when not using --preset/--load)")
    p.add_argument("--seed", type=int, default=None, help="Random seed for repeatable melodies")
    p.add_argument(
        "--leaps",
        type=int,
        default=20,
        help="Chance (percent) a note will jump to a random degree instead of stepwise motion",
    )

    p.add_argument("--export", metavar="FILE", help="Write the song JSON to a file")
    p.add_argument("--print", dest="do_print", action="store_true", help="Print the song JSON to stdout")
    p.add_argument("--dry-run", action="store_true", help="Do everything except play")

    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    if args.load:
        with open(args.load, "r", encoding="utf-8") as f:
            payload = json.load(f)
        root, octave, scale, bpm, degrees, beats = unpack_song(payload)
        title = os.path.basename(args.load)
    elif args.preset:
        preset = PRESETS[args.preset]
        root, octave = args.root, args.octave
        scale = str(preset["scale"])
        bpm = int(preset["bpm"])
        degrees = list(map(int, preset["steps"]))
        beats = list(map(float, preset["durations"]))
        title = f"preset:{args.preset}"
    else:
        root, octave, scale, bpm = args.root, args.octave, args.scale, args.bpm
        rng = random.Random(args.seed)
        degrees = generate_melody(root, octave, scale, args.length, args.seed, args.leaps)
        beats = durations_for_length(args.length, rng)
        title = "generated"

    song = pack_song(root, octave, scale, bpm, degrees, beats)
    notes = build_notes(root, octave, scale, degrees, beats)

    total_beats = sum(n.beats for n in notes)
    total_seconds = total_beats * beat_seconds(bpm)

    print("\nMusicbox Maker")
    print("-" * 40)
    print(f"Title:   {title}")
    print(f"Key:     {root}{octave} {scale}")
    print(f"Tempo:   {bpm} bpm")
    print(f"Notes:   {len(notes)}")
    print(f"Length:  {total_seconds:.1f} seconds")

    if args.do_print:
        print("\nSong JSON:")
        print(json.dumps(song, indent=2, sort_keys=True))

    if args.export:
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(song, f, indent=2, sort_keys=True)
        print(f"\nExported to: {args.export}")

    if args.dry_run:
        print("\nDry run enabled; not playing.")
        return 0

    try:
        if is_windows():
            play_windows(notes, bpm)
        else:
            play_visual(notes, bpm)
    except KeyboardInterrupt:
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
