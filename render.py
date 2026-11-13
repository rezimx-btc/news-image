#!/usr/bin/env python3
"""news-image-01 entry: render a one-page newspaper for 13 November 2026.

Fresh 3-column broadsheet design: deep navy masthead on cream, a big lead
story with a tanker graphic, three ruled columns, an "ALSO IN THE NEWS"
strip and a sources footer. Stdlib only: the PNG encoder and the 5x7
bitmap font below are written from scratch in this file (no Pillow).
"""
import binascii
import hashlib
import os
import struct
import zlib

W = 1024
H = 1024
CREAM = (245, 239, 221)
NAVY = (20, 38, 77)
INK = (28, 28, 28)
RED = (168, 44, 34)

# 5x7 bitmap font. '#' = ink, '.' = blank. Every glyph is 7 rows of 5.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", "#...."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "#...."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...##", "..#..", "..#..", "..#..", "..#..", "..#..", "...##"),
    ')': ("##...", "..#..", "..#..", "..#..", "..#..", "..#..", "##..."),
    '/': ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '•': (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
    '—': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '<': ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    '>': ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    '\\': ("#....", "#....", ".#...", ".#...", "..#..", "..#..", "...#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '~': (".....", ".....", ".##..", "#..##", ".....", ".....", "....."),
}


class Canvas:
    """An RGB canvas backed by one bytearray per row (3 bytes per pixel)."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = [bytearray(bytes(bg) * w) for _ in range(h)]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            self.px[yy][x0 * 3:x1 * 3] = row

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def glyph(self, x, y, ch, scale, color):
        g = FONT.get(ch)
        if g is None:
            return
        for r, row in enumerate(g):
            yy = y + r * scale
            for c, bit in enumerate(row):
                if bit == '#':
                    self.rect(x + c * scale, yy, scale, scale, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            if ch == ' ':
                cx += 6 * scale
                continue
            self.glyph(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        s = s.upper()
        return len(s) * 6 * scale - scale if s else 0

    def text_centered(self, y, s, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = self.text_w(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)

    def wrap(self, s, scale, max_w):
        words = s.upper().split(' ')
        lines = []
        cur = ''
        for wd in words:
            t = wd if not cur else cur + ' ' + wd
            if self.text_w(t, scale) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def story(self, x, y, w, headline, deck, hscale=3, dscale=2):
        """Draw one column story: headline + deck lines. Returns bottom y."""
        for ln in self.wrap(headline, hscale, w):
            self.text(x, y, ln, hscale, NAVY)
            y += 9 * hscale
        y += 6
        for ln in deck:
            for sub in self.wrap(ln, dscale, w):
                self.text(x, y, sub, dscale, INK)
                y += 9 * dscale
            y += 2
        return y


def chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', binascii.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = b''.join(b'\x00' + bytes(row) for row in cv.px)
    comp = zlib.compress(raw, 9)
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr) + chunk(b'IDAT', comp) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return png


def tanker(cv, cx, y):
    """A small tanker silhouette with waves, centred on cx at height y."""
    hull_y = y + 30
    cv.rect(cx - 110, hull_y, 220, 14, NAVY)
    cv.rect(cx - 110, hull_y - 4, 220, 4, NAVY)
    cv.rect(cx - 44, y + 10, 52, 16, NAVY)
    cv.rect(cx + 28, y, 16, 26, RED)
    cv.rect(cx + 28, y, 16, 4, INK)
    cv.vline(cx - 92, y + 8, 18, NAVY, 2)
    cv.rect(cx - 96, y + 6, 10, 3, RED)
    cv.hline(cx - 110, hull_y + 22, 220, NAVY, 2)
    cv.hline(cx - 78, hull_y + 30, 156, NAVY, 2)
    cv.hline(cx - 46, hull_y + 38, 92, NAVY, 2)


def draw_newspaper(cv):
    # Frame: navy border, cream field, thin inner rule.
    cv.rect(12, 12, 1000, 1000, NAVY)
    cv.rect(18, 18, 988, 988, CREAM)
    cv.hline(28, 28, 968, NAVY, 1)
    cv.hline(28, 995, 968, NAVY, 1)
    cv.vline(28, 28, 968, NAVY, 1)
    cv.vline(995, 28, 968, NAVY, 1)

    # Masthead: navy band with the paper's name in cream.
    cv.rect(36, 36, 952, 132, NAVY)
    cv.text_centered(60, "THE WORLD", 12, CREAM, 36, 988)
    # Date line with volume / number at the sides.
    cv.text(36, 182, "VOL. I", 2, NAVY)
    cv.text_centered(182, "FRIDAY, 13 NOVEMBER 2026", 3, NAVY, 36, 988)
    right = "NO. 13"
    cv.text(988 - cv.text_w(right, 2), 182, right, 2, NAVY)
    cv.hline(36, 214, 952, NAVY, 3)

    # Lead story.
    cv.text_centered(228, "LEAD STORY", 2, RED, 36, 988)
    cv.text_centered(250, "FOUR TANKERS HIT", 6, NAVY, 36, 988)
    cv.text_centered(306, "RADAR DESTROYED IN BAHRAIN", 3, INK, 36, 988)
    cv.text_centered(336, "IRAN STRIKES IN THE STRAIT", 2, INK, 36, 988)
    tanker(cv, 512, 366)
    cv.hline(36, 446, 952, NAVY, 2)

    # Three ruled columns, two stories each.
    cv.vline(352, 466, 364, NAVY, 1)
    cv.vline(676, 466, 364, NAVY, 1)
    y1 = cv.story(36, 466, 304, "UKRAINE PEACE TALKS",
                  ["TALKS OPEN AMID WAR",
                   "ENVOYS SEEK AN END TO FIGHTING"])
    cv.hline(36, y1 + 24, 304, NAVY, 1)
    cv.story(36, y1 + 52, 304, "MICROSOFT 365 DOWN",
             ["OUTAGE HITS MILLIONS", "USERS LOCKED OUT"])
    cv.text_centered(800, "• • •", 2, NAVY, 36, 340)
    y2 = cv.story(360, 466, 304, "NVIDIA CEO RESIGNS",
                  ["SHARES FALL 16%", "AFTER CHIEF STEPS DOWN"])
    cv.hline(360, y2 + 24, 304, NAVY, 1)
    cv.story(360, y2 + 52, 304, "BINANCE SEIZURE",
             ["$1.2 BILLION SEIZED"])
    cv.text_centered(800, "• • •", 2, NAVY, 360, 664)
    y3 = cv.story(684, 466, 304, "GAZA HOSPITAL HIT",
                  ["STRIKE HITS HOSPITAL", "IN GAZA"])
    cv.hline(684, y3 + 24, 304, NAVY, 1)
    cv.story(684, y3 + 52, 304, "VAN HOLLEN V SCHUMER",
             ["SENATE SHOWDOWN", "IN WASHINGTON"])
    cv.text_centered(800, "• • •", 2, NAVY, 684, 988)

    # "Also in the news" strip.
    cv.hline(36, 852, 952, NAVY, 1)
    cv.text_centered(864, "ALSO IN THE NEWS", 2, NAVY, 36, 988)
    cv.text_centered(890, "POPE LEO", 2, NAVY, 36, 352)
    cv.text_centered(890, "GEMINI 4", 2, NAVY, 360, 676)
    cv.text_centered(890, "ENGLAND V CROATIA", 2, NAVY, 684, 988)
    cv.text_centered(912, "VATICAN", 2, INK, 36, 352)
    cv.text_centered(912, "GOOGLE AI", 2, INK, 360, 676)
    cv.text_centered(912, "FOOTBALL", 2, INK, 684, 988)
    cv.hline(36, 934, 952, NAVY, 1)

    # Sources footer.
    cv.text_centered(952, "SOURCES: AP • REUTERS • AFP • WIRE REPORTS, "
                          "13 NOVEMBER 2026", 2, NAVY, 36, 988)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "news.png")
    cv = Canvas(W, H, CREAM)
    draw_newspaper(cv)
    png = write_png(out, cv)
    digest = hashlib.sha256(png).hexdigest()
    print("wrote %s %d bytes, (%d, %d) sha256 %s"
          % (out, len(png), W, H, digest))


if __name__ == "__main__":
    main()
