"""Robot Day 013: ASCII Banner Maker

Theme: ASCII art generator (banner text, no external dependencies).

What it does:
- Prompts for text and prints a blocky, readable ASCII banner.
- Offers optional centering and a simple border.

Why it's "robot-y": it turns plain text into a terminal-friendly sign for your automations.

Run:
  python robot_day_013_ascii_banner_maker.py
"""

from __future__ import annotations

import shutil

# A tiny 5x5-ish font. Only includes common characters; unknowns become '?'.
FONT = {
    "A": [" ### ", "#   #", "#####", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#### ", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#### ", "#    ", "#####"],
    "F": ["#####", "#    ", "#### ", "#    ", "#    "],
    "G": [" ####", "#    ", "# ###", "#   #", " ####"],
    "H": ["#   #", "#   #", "#####", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["#####", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "###  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#### ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#  ##", " ####"],
    "R": ["#### ", "#   #", "#### ", "#  # ", "#   #"],
    "S": [" ####", "#    ", " ### ", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", " # # ", "  #  ", " # # ", "#   #"],
    "Y": ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "   # ", "  #  ", " #   ", "#####"],
    "0": [" ### ", "#  ##", "# # #", "##  #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "   # ", "  #  ", "#####"],
    "3": ["#### ", "    #", " ### ", "    #", "#### "],
    "4": ["#   #", "#   #", "#####", "    #", "    #"],
    "5": ["#####", "#    ", "#### ", "    #", "#### "],
    "6": [" ### ", "#    ", "#### ", "#   #", " ### "],
    "7": ["#####", "   # ", "  #  ", " #   ", "#    "],
    "8": [" ### ", "#   #", " ### ", "#   #", " ### "],
    "9": [" ### ", "#   #", " ####", "    #", " ### "],
    " ": ["  ", "  ", "  ", "  ", "  "],
    "-": ["     ", "     ", "#####", "     ", "     "],
    "!": ["  #  ", "  #  ", "  #  ", "     ", "  #  "],
    "?": [" ### ", "#   #", "  ## ", "     ", "  #  "],
    ".": ["     ", "     ", "     ", "     ", "  #  "],
    ":": ["     ", "  #  ", "     ", "  #  ", "     "],
}


def render(text: str) -> list[str]:
    text = text.upper()
    rows = ["" for _ in range(5)]
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for i in range(5):
            rows[i] += glyph[i] + " "  # spacing between letters
    return [r.rstrip() for r in rows]


def bordered(lines: list[str], pad: int = 1) -> list[str]:
    width = max((len(l) for l in lines), default=0)
    inner_w = width + pad * 2
    top = "+" + "-" * inner_w + "+"
    out = [top]
    for l in lines:
        out.append("|" + " " * pad + l.ljust(width) + " " * pad + "|")
    out.append(top)
    return out


def center_lines(lines: list[str], term_w: int) -> list[str]:
    centered = []
    for l in lines:
        if len(l) >= term_w:
            centered.append(l)
        else:
            left = (term_w - len(l)) // 2
            centered.append(" " * left + l)
    return centered


def main() -> None:
    term_w = shutil.get_terminal_size((80, 20)).columns
    print("ASCII Banner Maker (Robot Day 013)")
    text = input("Text to bannerize: ").strip()
    if not text:
        print("Nothing to do. Try again with some text.")
        return

    want_border = input("Add border? [y/N]: ").strip().lower().startswith("y")
    want_center = input("Center in terminal? [y/N]: ").strip().lower().startswith("y")

    lines = render(text)
    if want_border:
        lines = bordered(lines)
    if want_center:
        lines = center_lines(lines, term_w)

    print("\n".join(lines))


if __name__ == "__main__":
    main()
