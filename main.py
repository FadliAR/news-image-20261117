#!/usr/bin/env python3
"""news-image-20261117: one image summing up world news of Tuesday 17 Nov 2026.

Renders a 1024x1024 PNG (entry.png) from scratch: hand-written PNG encoder,
hand-drawn raster shapes and a hand-built 5x7 bitmap font. Python 3.13 stdlib
only, no network, fully deterministic (same bytes on every run).

Layout: masthead with the date, six story panels (2 columns x 3 rows) covering
Europe, the Middle East, Asia, business, migration and space, plus a footer
naming the sources. Every story was verified against real reporting of
17 November 2026 before it was drawn (see STORIES).
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette ---
CREAM = (247, 243, 232)
PAPER = (255, 255, 255)
INK = (20, 20, 26)
NAVY = (20, 33, 61)
GOLD = (252, 163, 17)
MUTED = (90, 96, 110)
GREY_LINE = (200, 198, 188)

# ------------------------------------------- stories (verified 17 Nov 2026) --
# Sources: BBC, AP, Reuters, Al Jazeera, Just Security Early Edition,
# Level Headlines daily brief, Zark News, One Turn, FeedCast (all 17 Nov 2026).
STORIES = [
    {
        "tag": "EUROPE",
        "title": "KERCH BRIDGE HIT",
        "fact": "Ukraine strike collapses a road span; Russia hits two Kyiv bridges.",
        "accent": (180, 35, 24),
        "icon": "bridge",
    },
    {
        "tag": "MIDDLE EAST",
        "title": "TANKERS HIT AT HORMUZ",
        "fact": "Mines strike tankers and set them ablaze; a third US carrier arrives.",
        "accent": (11, 94, 110),
        "icon": "ship",
    },
    {
        "tag": "ASIA",
        "title": "TRUMP IN ASIA",
        "fact": "Manila ASEAN visit; Xi-Trump-Putin talks set for Thursday in Shenzhen.",
        "accent": (30, 64, 175),
        "icon": "globe",
    },
    {
        "tag": "BUSINESS",
        "title": "JPMORGAN OUTAGE",
        "fact": "Software bug disrupts online banking and Zelle payments.",
        "accent": (22, 101, 52),
        "icon": "bank",
    },
    {
        "tag": "EUROPE",
        "title": "EU MIGRANT HUB",
        "fact": "Five states plan a Rwanda return hub for rejected asylum seekers.",
        "accent": (107, 33, 168),
        "icon": "pin",
    },
    {
        "tag": "SPACE",
        "title": "VULCAN ROCKET FAILS",
        "fact": "ULA rocket fails in flight; 40 Amazon satellites are lost.",
        "accent": (194, 65, 12),
        "icon": "rocket",
    },
]

# ------------------------------------------------------- 5x7 bitmap font ---
# Each glyph is 7 rows of 5 pixels ('#' = on, '.' = off). Hand-built.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", "..#..", ".#..."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "#...."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}

CHAR_W = 5
CHAR_H = 7


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between glyphs)."""
    if not text:
        return 0
    return len(text) * (CHAR_W * scale + scale) - scale


def wrap_words(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------------ canvas --
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for ty in range(thickness):
                for tx in range(thickness):
                    self.set(x0 + tx, y0 + ty, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if filled:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(xx, yy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        steps = 120
        for i in range(steps):
            a = 2 * 3.141592653589793 * i / steps
            x = int(cx + rx * _cos(a))
            y = int(cy + ry * _sin(a))
            self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()  # bitmap font is uppercase-only; normalise here
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(CHAR_H):
                bits = glyph[row]
                for col in range(CHAR_W):
                    if bits[col] == "#":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
            cx += (CHAR_W + 1) * scale

    def text_center(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)


def _cos(a):
    # Cosine via Taylor series (stdlib-only, deterministic).
    a = a % 6.283185307179586
    term = 1.0
    total = 1.0
    for n in range(1, 8):
        term *= -a * a / ((2 * n - 1) * (2 * n))
        total += term
    return total


def _sin(a):
    return _cos(a - 1.5707963267948966)


# -------------------------------------------------------------- pictograms ---
def draw_bridge(cv, x, y, color):
    # Broken bridge: two towers, sagging cables, a gap in the deck.
    cv.line(x + 10, y + 16, x + 10, y + 46, color, 3)
    cv.line(x + 58, y + 16, x + 58, y + 46, color, 3)
    cv.line(x + 10, y + 16, x + 36, y + 32, color, 2)
    cv.line(x + 58, y + 16, x + 36, y + 32, color, 2)
    cv.fill_rect(x + 4, y + 44, 26, 5, color)
    cv.fill_rect(x + 42, y + 44, 26, 5, color)
    cv.line(x + 30, y + 49, x + 40, y + 62, color, 3)
    cv.line(x + 6, y + 64, x + 24, y + 64, color, 2)
    cv.line(x + 44, y + 64, x + 66, y + 64, color, 2)


def draw_ship(cv, x, y, color):
    # Tanker hull, mast, explosion star, waves.
    cv.fill_rect(x + 8, y + 40, 52, 12, color)
    cv.line(x + 60, y + 40, x + 68, y + 52, color, 3)
    cv.line(x + 8, y + 40, x + 4, y + 52, color, 3)
    cv.line(x + 34, y + 40, x + 34, y + 18, color, 3)
    cv.fill_rect(x + 34, y + 18, 14, 8, color)
    for dx, dy in ((0, -12), (10, -8), (12, 2), (4, 10), (-8, 8), (-12, -2)):
        cv.line(x + 52, y + 14, x + 52 + dx, y + 14 + dy, GOLD, 2)
    cv.line(x + 4, y + 60, x + 22, y + 60, color, 2)
    cv.line(x + 28, y + 64, x + 48, y + 64, color, 2)
    cv.line(x + 52, y + 60, x + 68, y + 60, color, 2)


def draw_globe(cv, x, y, color):
    cv.circle(x + 36, y + 36, 27, color, filled=False)
    cv.ellipse(x + 36, y + 36, 12, 27, color)
    cv.line(x + 36, y + 9, x + 36, y + 63, color, 1)
    cv.line(x + 12, y + 24, x + 60, y + 24, color, 1)
    cv.line(x + 10, y + 36, x + 62, y + 36, color, 1)
    cv.line(x + 12, y + 48, x + 60, y + 48, color, 1)


def draw_bank(cv, x, y, color):
    # Bank pediment + columns, struck by a lightning bolt.
    cv.line(x + 8, y + 28, x + 36, y + 12, color, 3)
    cv.line(x + 36, y + 12, x + 64, y + 28, color, 3)
    cv.line(x + 8, y + 28, x + 64, y + 28, color, 3)
    for cx in (14, 33, 52):
        cv.fill_rect(x + cx, y + 32, 6, 24, color)
    cv.fill_rect(x + 8, y + 56, 56, 6, color)
    cv.line(x + 48, y + 6, x + 42, y + 20, GOLD, 3)
    cv.line(x + 42, y + 20, x + 48, y + 20, GOLD, 3)
    cv.line(x + 48, y + 20, x + 40, y + 34, GOLD, 3)


def draw_pin(cv, x, y, color):
    # Map pin + rightward arrow (a hub sending people on).
    cv.circle(x + 28, y + 26, 15, color, filled=True)
    cv.line(x + 16, y + 34, x + 28, y + 58, color, 3)
    cv.line(x + 40, y + 34, x + 28, y + 58, color, 3)
    cv.circle(x + 28, y + 26, 6, PAPER, filled=True)
    cv.line(x + 44, y + 52, x + 64, y + 52, color, 3)
    cv.line(x + 64, y + 52, x + 56, y + 44, color, 3)
    cv.line(x + 64, y + 52, x + 56, y + 60, color, 3)


def draw_rocket(cv, x, y, color):
    # Rocket climbing, flame below, stars around.
    cv.fill_rect(x + 30, y + 16, 12, 34, color)
    cv.line(x + 30, y + 16, x + 36, y + 4, color, 3)
    cv.line(x + 42, y + 16, x + 36, y + 4, color, 3)
    cv.circle(x + 36, y + 28, 4, PAPER, filled=True)
    cv.line(x + 30, y + 50, x + 22, y + 62, color, 3)
    cv.line(x + 42, y + 50, x + 50, y + 62, color, 3)
    cv.line(x + 32, y + 50, x + 36, y + 66, GOLD, 3)
    cv.line(x + 40, y + 50, x + 36, y + 66, GOLD, 3)
    for sx, sy in ((10, 10), (60, 14), (8, 44), (62, 40)):
        cv.line(x + sx - 3, y + sy, x + sx + 3, y + sy, GOLD, 2)
        cv.line(x + sx, y + sy - 3, x + sx, y + sy + 3, GOLD, 2)


ICONS = {
    "bridge": draw_bridge,
    "ship": draw_ship,
    "globe": draw_globe,
    "bank": draw_bank,
    "pin": draw_pin,
    "rocket": draw_rocket,
}

# ------------------------------------------------------------------- layout --
HEADER_H = 150
FOOTER_H = 34
MARGIN = 24
GAP = 12


def draw_panel(cv, px, py, pw, ph, story):
    cv.fill_rect(px, py, pw, ph, PAPER)
    cv.rect(px, py, pw, ph, GREY_LINE, 1)
    accent = story["accent"]
    cv.fill_rect(px, py, pw, 8, accent)
    # Region tag, bottom right (kept clear of the title lines).
    tag = story["tag"]
    tw = text_width(tag, 2)
    cv.text(px + pw - tw - 14, py + ph - 26, tag, 2, MUTED)
    # Pictogram in a tinted square, left.
    ix, iy = px + 14, py + 26
    cv.fill_rect(ix, iy, 76, 76, CREAM)
    cv.rect(ix, iy, 76, 76, GREY_LINE, 1)
    ICONS[story["icon"]](cv, ix + 2, iy + 2, accent)
    # Title, right of the pictogram, wrapped to two lines.
    tx = ix + 76 + 12
    max_tw = px + pw - 14 - tx
    title_lines = wrap_words(story["title"], max_tw, 3)[:2]
    ty = py + 30
    for line in title_lines:
        cv.text(tx, ty, line, 3, NAVY)
        ty += 3 * CHAR_H + 6
    # Fact text, full width below.
    fx = px + 14
    fw = pw - 28
    fact_lines = wrap_words(story["fact"], fw, 3)[:3]
    fy = py + 118
    for line in fact_lines:
        cv.text(fx, fy, line, 3, INK)
        fy += 3 * CHAR_H + 8


def render():
    cv = Canvas(WIDTH, HEIGHT, CREAM)
    # Masthead.
    cv.fill_rect(0, 0, WIDTH, HEADER_H, NAVY)
    cv.fill_rect(0, HEADER_H - 6, WIDTH, 6, GOLD)
    cv.text_center(26, "17 NOVEMBER 2026", 9, CREAM)
    cv.text_center(104, "TUESDAY - WORLD NEWS IN ONE IMAGE", 3, GOLD)
    # Story grid: 2 columns x 3 rows.
    grid_y = HEADER_H + GAP
    grid_h = HEIGHT - grid_y - FOOTER_H - GAP
    pw = (WIDTH - 2 * MARGIN - GAP) // 2
    ph = (grid_h - 2 * GAP) // 3
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        px = MARGIN + col * (pw + GAP)
        py = grid_y + row * (ph + GAP)
        draw_panel(cv, px, py, pw, ph, story)
    # Footer.
    footer = "ALL STORIES FIRST REPORTED 17 NOV 2026 - SOURCES: BBC, AP, REUTERS, AL JAZEERA"
    cv.text_center(HEIGHT - FOOTER_H + 8, footer, 2, MUTED)
    return cv


# ------------------------------------------------------------ PNG encoding --
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = render()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, cv)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, cv.w, cv.h))


if __name__ == "__main__":
    main()
