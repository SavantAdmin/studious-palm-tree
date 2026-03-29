#!/usr/bin/env python3
"""robot_day_016_tiny_terminal_tetris.py

Tiny Terminal Tetris (single-file, stdlib-only).

Controls:
- Left/Right or A/D: move
- Down or S: soft drop
- Up or W: rotate
- Space: hard drop
- Q: quit

Intentionally small and hackable.
"""

import curses
import random
import time

W, H = 10, 20
TICK = 0.35

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}


def rotate(mat):
    """Rotate a matrix clockwise."""
    return [list(row) for row in zip(*mat[::-1])]


def collide(board, piece, px, py):
    """Return True if piece at (px, py) hits wall/floor/blocks."""
    for y, row in enumerate(piece):
        for x, v in enumerate(row):
            if not v:
                continue
            bx, by = px + x, py + y
            if bx < 0 or bx >= W or by >= H:
                return True
            if by >= 0 and board[by][bx]:
                return True
    return False


def stamp(board, piece, px, py):
    """Merge piece into the board."""
    for y, row in enumerate(piece):
        for x, v in enumerate(row):
            if v:
                by = py + y
                if by >= 0:
                    board[by][px + x] = 1


def clear_lines(board):
    kept = [r for r in board if not all(r)]
    cleared = H - len(kept)
    for _ in range(cleared):
        kept.insert(0, [0] * W)
    return kept, cleared


def draw(stdscr, board, piece, px, py, score, lines):
    stdscr.erase()
    stdscr.addstr(0, 0, "Tiny Terminal Tetris")
    stdscr.addstr(1, 0, f"Score: {score}   Lines: {lines}")
    stdscr.addstr(2, 0, "Arrows/WASD move, Up/W rotate, Space drop, Q quit")

    ox, oy = 2, 4  # top-left of playfield
    stdscr.addstr(oy - 1, ox - 2, "+" + "-" * (W * 2) + "+")
    for y in range(H):
        stdscr.addstr(oy + y, ox - 2, "|")
        stdscr.addstr(oy + y, ox + W * 2, "|")
    stdscr.addstr(oy + H, ox - 2, "+" + "-" * (W * 2) + "+")

    for y in range(H):
        for x in range(W):
            if board[y][x]:
                stdscr.addstr(oy + y, ox + x * 2, "[]")

    for y, row in enumerate(piece):
        for x, v in enumerate(row):
            if v:
                by, bx = py + y, px + x
                if by >= 0:
                    stdscr.addstr(oy + by, ox + bx * 2, "[]")

    stdscr.refresh()


def new_piece():
    name = random.choice(list(SHAPES))
    return [row[:] for row in SHAPES[name]]


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    board = [[0] * W for _ in range(H)]
    piece = new_piece()
    px, py = W // 2 - len(piece[0]) // 2, -2

    score = 0
    lines = 0
    last_tick = time.time()

    while True:
        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            return

        # Movement
        if ch in (curses.KEY_LEFT, ord("a"), ord("A")) and not collide(board, piece, px - 1, py):
            px -= 1
        elif ch in (curses.KEY_RIGHT, ord("d"), ord("D")) and not collide(board, piece, px + 1, py):
            px += 1
        elif ch in (curses.KEY_DOWN, ord("s"), ord("S")) and not collide(board, piece, px, py + 1):
            py += 1
        elif ch in (curses.KEY_UP, ord("w"), ord("W")):
            rp = rotate(piece)
            if not collide(board, rp, px, py):
                piece = rp
        elif ch == ord(" "):
            while not collide(board, piece, px, py + 1):
                py += 1
            last_tick = 0  # lock immediately on next tick

        # Gravity tick
        now = time.time()
        if now - last_tick >= TICK:
            last_tick = now
            if not collide(board, piece, px, py + 1):
                py += 1
            else:
                stamp(board, piece, px, py)
                board, cleared = clear_lines(board)
                if cleared:
                    lines += cleared
                    score += [0, 100, 300, 500, 800][cleared]

                piece = new_piece()
                px, py = W // 2 - len(piece[0]) // 2, -2
                if collide(board, piece, px, py):
                    draw(stdscr, board, piece, px, py, score, lines)
                    stdscr.nodelay(False)
                    stdscr.addstr(4 + H // 2, 2, "Game Over. Press any key to exit.")
                    stdscr.getch()
                    return

        draw(stdscr, board, piece, px, py, score, lines)
        time.sleep(0.01)


if __name__ == "__main__":
    curses.wrapper(main)
