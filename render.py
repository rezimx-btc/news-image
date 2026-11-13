#!/usr/bin/env python3
"""news-image-01 v3 entry: a bold red tabloid front page for 13 November 2026.

Design (new for v3, different from v1's plain newspaper and v2's navy
3-column broadsheet): a tabloid front page. A solid red masthead band
carries THE WORLD in big white letters; below it a huge HORMUZ ON FIRE
headline, a two-line sub-head, and a drawn lead scene - the Strait of
Hormuz at dusk with four tankers on a navy sea, two of them burning under
starburst explosions, dotted missile arcs overhead, and a radar station on
the Bahrain coast crossed out in red. Six more stories fill a two-column
grid, an ALSO strip carries the three short items, and the footer cites the
wire sources. Everything is drawn with the standard library only: a tiny
5x7 bitmap font, rectangles, lines and discs, packed into a PNG by hand.

Run: python3 render.py   -> writes news.png (1024x1024, under 1 MiB).
"""

import binascii
import hashlib
import math
import os
import struct
import zlib

W = 1024
H = 1024

WHITE = (255, 255, 255)
BLACK = (17, 17, 17)
RED = (200, 16, 46)
NAVY = (11, 42, 74)
SKY = (191, 227, 242)
YELLOW = (255, 210, 63)
ORANGE = (255, 122, 26)
GREY = (85, 85, 85)
LAND = (47, 79, 79)
SMOKE = (120, 120, 120)
SEA_LIGHT = (70, 110, 150)

BLANK = ("00000",) * 7

# 5x7 bitmap font: each glyph is 7 rows of 5 bits ("1" = ink).
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10011", "10101", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "00100", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": BLANK,
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "%": ("01100", "01100", "00010", "00100", "01000", "01100", "01100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "\u2022": ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
}


class Canvas:
    """An RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i], self.pix[i + 1], self.pix[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        span = x1 - x0
        row = bytes(color) * span
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.pix[base:base + span * 3] = row

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        r2 = r * r
        for dy in range(-r, r + 1):
            dx = math.isqrt(r2 - dy * dy)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            self.px(cx - dx, cy + dy, color)
            self.px(cx + dx, cy + dy, color)

    def burst(self, cx, cy, r, color):
        for k in range(12):
            ang = math.pi * k / 6.0
            self.line(cx, cy,
                      int(cx + r * math.cos(ang)),
                      int(cy + r * math.sin(ang)), color)
        self.disc(cx, cy, max(2, r // 4), color)

    def dotted_arc(self, x0, y0, x1, y1, lift, color):
        mx = (x0 + x1) // 2
        my = min(y0, y1) - lift
        for t in range(0, 101, 5):
            u = t / 100.0
            x = int((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1)
            y = int((1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1)
            self.disc(x, y, 2, color)

    def frame(self):
        """A black outer border plus a thin red inner line, so the page
        reads as a printed front page even on a white background."""
        self.rect(0, 0, self.w, 4, BLACK)
        self.rect(0, self.h - 4, self.w, 4, BLACK)
        self.rect(0, 0, 4, self.h, BLACK)
        self.rect(self.w - 4, 0, 4, self.h, BLACK)
        self.rect(8, 8, self.w - 16, 2, RED)
        self.rect(8, self.h - 10, self.w - 16, 2, RED)

    def text(self, s, x, y, scale, color):
        cx = x
        for ch in s:
            rows = GLYPHS.get(ch)
            if rows is None:
                rows = GLYPHS.get(ch.upper(), BLANK)
            for r in range(7):
                bits = rows[r]
                for c in range(5):
                    if bits[c] == "1":
                        self.rect(cx + c * scale, y + r * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return max(0, len(s) * 6 * scale - scale)

    def center(self, s, y, scale, color):
        self.text(s, (self.w - self.text_w(s, scale)) // 2, y, scale, color)


def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.pix[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", binascii.crc32(tag + data) & 0xffffffff))


def draw_tanker(cv, x, y, w):
    """One oil tanker: black hull, red funnel with smoke, white bridge."""
    cv.rect(x, y, w, 28, BLACK)
    cv.rect(x + 8, y - 17, 22, 17, RED)
    cv.rect(x + w - 42, y - 17, 34, 17, WHITE)
    cv.line(x + w // 2, y, x + w // 2, y - 12, BLACK)
    cv.disc(x + 19, y - 24, 5, SMOKE)
    cv.disc(x + 12, y - 32, 4, SMOKE)
    cv.disc(x + 26, y - 34, 4, SMOKE)


def draw_scene(cv):
    """The lead illustration: the Strait of Hormuz at dusk, y 330..580."""
    cv.rect(0, 330, W, 140, SKY)
    cv.rect(0, 470, W, 110, NAVY)
    # Sun with rays, top right.
    cv.disc(930, 378, 30, YELLOW)
    for k in range(8):
        ang = math.pi * k / 4.0 + math.pi / 8.0
        cv.line(int(930 + 36 * math.cos(ang)), int(378 + 36 * math.sin(ang)),
                int(930 + 50 * math.cos(ang)), int(378 + 50 * math.sin(ang)),
                ORANGE)
    # Bahrain coast on the left, with a radar dish crossed out in red.
    cv.rect(0, 428, 210, 42, LAND)
    cv.line(110, 428, 110, 398, BLACK)
    cv.line(110, 428, 110, 398, BLACK)
    cv.disc(110, 392, 16, GREY)
    cv.ring(110, 392, 16, BLACK)
    cv.line(94, 376, 126, 408, RED)
    cv.line(126, 376, 94, 408, RED)
    cv.text("BAHRAIN", 64, 448, 2, WHITE)
    # Four tankers on the sea; the 2nd and 4th are burning.
    for x in (120, 330, 540, 750):
        draw_tanker(cv, x, 495, 160)
    cv.burst(410, 442, 30, ORANGE)
    cv.burst(410, 442, 16, YELLOW)
    cv.burst(830, 442, 30, ORANGE)
    cv.burst(830, 442, 16, YELLOW)
    # Dotted missile arcs falling onto the burning tankers.
    cv.dotted_arc(180, 342, 410, 442, 25, RED)
    cv.dotted_arc(640, 342, 830, 442, 25, RED)
    # Waves and the sea label.
    for wx, wy, wl in ((60, 536, 90), (300, 556, 70), (520, 534, 80),
                       (700, 562, 90), (880, 540, 70), (180, 566, 60)):
        cv.rect(wx, wy, wl, 3, SEA_LIGHT)
    cv.center("STRAIT OF HORMUZ", 548, 2, WHITE)


STORIES = [
    ("UKRAINE TALKS",
     "PEACE TALKS RESUME AS LEADERS MEET.",
     "CEASEFIRE HOPES RISE AFTER STALEMATE."),
    ("NVIDIA CEO QUITS",
     "CHIEF EXECUTIVE RESIGNS SUDDENLY.",
     "SHARES FALL 16% IN A SINGLE DAY."),
    ("MICROSOFT 365 DOWN",
     "OUTAGE HITS MILLIONS OF USERS.",
     "EMAIL AND TEAMS OFFLINE FOR HOURS."),
    ("BINANCE $1.2B SEIZED",
     "AUTHORITIES SEIZE $1.2 BILLION.",
     "LARGEST CRYPTO SEIZURE ON RECORD."),
    ("GAZA HOSPITAL",
     "HOSPITAL HIT AS FIGHTING RAGES ON.",
     "AID GROUPS WARN OF DEEPENING CRISIS."),
    ("VAN HOLLEN v SCHUMER",
     "SENATORS CLASH OVER THE SHUTDOWN.",
     "DEAL STILL OUT OF REACH IN WASHINGTON."),
]


def draw_page(cv):
    # Masthead: solid red band, THE WORLD in white, thin white rule.
    cv.rect(0, 0, W, 118, RED)
    cv.center("THE WORLD", 24, 10, WHITE)
    cv.rect(362, 104, 300, 3, WHITE)
    # Date strip.
    cv.text("WORLD EDITION", 24, 127, 2, GREY)
    cv.center("FRIDAY, 13 NOVEMBER 2026", 127, 2, BLACK)
    cv.text("NO. 317", 918, 127, 2, GREY)
    cv.rect(0, 150, W, 3, BLACK)
    # Kicker, giant headline, two-line sub-head.
    cv.center("BREAKING - STRAIT OF HORMUZ", 160, 3, RED)
    cv.center("HORMUZ ON FIRE", 194, 10, BLACK)
    cv.center("IRAN HITS FOUR TANKERS IN THE STRAIT", 272, 3, BLACK)
    cv.center("RADAR STATION IN BAHRAIN DESTROYED", 298, 3, BLACK)
    # Lead illustration and caption.
    draw_scene(cv)
    cv.center("FOUR TANKERS STRUCK IN THE STRAIT. RADAR IN BAHRAIN DESTROYED.",
              588, 2, GREY)
    cv.rect(0, 612, W, 3, BLACK)
    # Two-column grid of six more stories.
    for i, (head, line1, line2) in enumerate(STORIES):
        x = 24 if i % 2 == 0 else 524
        y = 626 + (i // 2) * 102
        cv.rect(x, y - 8, 46, 5, RED)
        cv.text(head, x, y, 3, BLACK)
        cv.text(line1, x, y + 30, 2, BLACK)
        cv.text(line2, x, y + 48, 2, GREY)
    # ALSO strip, footer rule, sources, bottom red band.
    cv.rect(0, 904, W, 2, BLACK)
    cv.center("ALSO: POPE LEO \u2022 GEMINI 4 \u2022 ENGLAND-CROATIA",
              914, 2, RED)
    cv.rect(0, 942, W, 2, BLACK)
    cv.center("SOURCES: AP \u2022 REUTERS \u2022 AFP \u2022 WIRE REPORTS, 13 NOVEMBER 2026",
              952, 2, BLACK)
    cv.rect(0, 990, W, 34, RED)


def main():
    cv = Canvas(W, H, WHITE)
    draw_page(cv)
    cv.frame()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.png")
    write_png(out, cv)
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes,",
          "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
