"""Render the news-image entry for Thursday 19 November 2026.

Reads stories.json next to this file and draws a 1024x1024 front page
with PIL. Deterministic: no timestamps, no randomness, no network.
Run:  python3 render.py [output.png]
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# Palette
NAVY = (22, 40, 63)
NAVY2 = (30, 54, 84)
GOLD = (212, 169, 60)
CREAM = (247, 243, 233)
PAPER = (252, 250, 244)
INK = (26, 26, 26)
GREY = (110, 110, 108)
LINE = (205, 198, 184)
RED = (176, 42, 42)
TEAL = (17, 122, 101)

with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
    DATA = json.load(f)

STORIES = DATA["stories"]
BY_ID = {s["id"]: s for s in STORIES}


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap. Raises if a single word is wider than max_w."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if text_w(draw, word, fnt) > max_w:
                raise ValueError("word too wide: %r" % word)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, fnt, x, y, max_w, max_lines, fill, leading):
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        raise ValueError("text overflows %d lines: %r -> %r"
                         % (max_lines, text, lines))
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


# ---------------------------------------------------------------- art
def art_shenzhen(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(23, 62, 94))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(18, 48, 74))
    # skyline blocks
    blocks = [(0, 46, 34, 58), (38, 30, 30, 74), (72, 52, 26, 52),
              (102, 22, 30, 82), (136, 40, 26, 64), (166, 52, 30, 52),
              (200, 28, 28, 76), (232, 44, 26, 60), (262, 34, 28, 70),
              (294, 50, 28, 54)]
    for bx, by, bw, bh in blocks:
        d.rectangle([x + bx, y + h - 26 - bh + 22, x + bx + bw,
                     y + h - 4], fill=(52, 96, 130))
        for wy in range(0, bh - 8, 10):
            d.rectangle([x + bx + 5, y + h - 26 - bh + 22 + wy + 3,
                         x + bx + 9, y + h - 26 - bh + 22 + wy + 6],
                        fill=(212, 169, 60))
    # three flags on poles
    for i, (fx, cols) in enumerate([(52, [(176, 42, 42), (247, 243, 233)]),
                                    (150, [(222, 60, 60)]),
                                    (248, [(247, 243, 233), (30, 90, 160), (176, 42, 42)])]):
        px = x + fx
        d.line([px, y + 8, px, y + h - 26], fill=(247, 243, 233), width=2)
        if i == 0:  # US: stripes + blue corner
            for s in range(4):
                d.rectangle([px, y + 8 + s * 5, px + 26, y + 12 + s * 5],
                            fill=cols[s % 2])
            d.rectangle([px, y + 8, px + 11, y + 17], fill=(30, 60, 120))
        elif i == 1:  # CN: red + stars
            d.rectangle([px, y + 8, px + 26, y + 28], fill=cols[0])
            for sx, sy in [(5, 4), (13, 7), (17, 3), (10, 12), (18, 11)]:
                d.ellipse([px + sx, y + 8 + sy, px + sx + 3, y + 11 + sy],
                          fill=(255, 222, 60))
        else:  # RU: three horizontal bands
            for s, c in enumerate(cols):
                d.rectangle([px, y + 8 + s * 7, px + 26, y + 14 + s * 7],
                            fill=c)


def art_vicecity(d, x, y, w, h):
    # sunset bands
    bands = [(255, 122, 89), (255, 170, 90), (255, 214, 130), (150, 220, 220)]
    for i, c in enumerate(bands):
        d.rectangle([x, y + i * h // 4, x + w, y + (i + 1) * h // 4], fill=c)
    d.ellipse([x + w - 96, y + 6, x + w - 40, y + 62], fill=(255, 240, 180))
    # art-deco buildings
    for bx, bw, bh in [(0, 46, 40), (50, 40, 58), (94, 52, 34),
                       (150, 44, 62), (198, 48, 42), (250, 44, 56),
                       (298, 24, 30)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(38, 38, 64))
        d.rectangle([x + bx + 6, y + h - bh - 8, x + bx + bw - 6,
                     y + h - bh], fill=(38, 38, 64))
        for wy in range(8, bh - 6, 12):
            d.rectangle([x + bx + 8, y + h - bh + wy, x + bx + 14,
                         y + h - bh + wy + 5], fill=(255, 214, 130))
    # palms
    for px, py in [(120, h - 34), (230, h - 42)]:
        d.line([x + px, y + py, x + px + 4, y + py - 26], fill=(30, 80, 50),
               width=3)
        for dx, dy in [(-16, -8), (-8, -14), (8, -14), (16, -8), (0, -18)]:
            d.line([x + px + 2, y + py - 26, x + px + 2 + dx,
                    y + py - 26 + dy], fill=(30, 110, 60), width=3)


def art_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 74, 52))
    # bars
    vals = [18, 26, 22, 34, 30, 44, 40, 56, 52, 68]
    bw = w // len(vals)
    for i, v in enumerate(vals):
        d.rectangle([x + i * bw + 4, y + h - v - 6, x + (i + 1) * bw - 4,
                     y + h - 6], fill=(46, 160, 110))
    # rising line
    pts = [(x + 8 + i * (w - 16) // 9, y + h - 14 - int(v * 0.95))
           for i, v in enumerate([20, 24, 22, 30, 36, 34, 44, 50, 58, 72])]
    d.line(pts, fill=(255, 222, 90), width=4)
    d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
              fill=(255, 222, 90))
    d.polygon([(pts[-1][0] + 2, pts[-1][1] - 14), (pts[-1][0] + 16, pts[-1][1] - 2),
               (pts[-1][0] + 2, pts[-1][1] + 2)], fill=(255, 222, 90))
    d.text((x + 10, y + 6), "$83", font=font(SANS_B, 22), fill=(255, 255, 255))


def art_vangogh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 92, 150))
    for sx, sy in [(12, 6), (40, 12), (70, 5), (110, 9), (150, 6), (180, 11)]:
        d.ellipse([x + sx, y + sy, x + sx + 5, y + sy + 5], fill=(255, 222, 90))
    # chestnut tree: trunk + canopy
    d.polygon([(x + 96, y + h), (x + 102, y + 14), (x + 108, y + h)],
              fill=(96, 60, 30))
    for cx, cy, r in [(84, 16, 14), (104, 10, 16), (124, 18, 13), (96, 24, 12)]:
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                  fill=(90, 150, 70))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(120, 140, 90))


def art_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 208, 192))
    d.polygon([(x + 30, y + 4), (x + w - 30, y + 4), (x + w // 2, y + 16)],
              fill=(120, 110, 96))
    d.rectangle([x + 30, y + 16, x + w - 30, y + 20], fill=(120, 110, 96))
    for i in range(5):
        cx = x + 44 + i * 26
        d.rectangle([cx, y + 20, cx + 8, y + h - 6], fill=(247, 243, 233))
    d.rectangle([x + 30, y + h - 8, x + w - 30, y + h - 4], fill=(120, 110, 96))


def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 208, 224))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(52, 110, 150))
    d.polygon([(x + 10, y + h - 10), (x + w // 2, y + 6), (x + w - 10, y + h - 10)],
              fill=(176, 42, 42))
    d.rectangle([x + 8, y + h - 16, x + w - 8, y + h - 10], fill=(230, 225, 210))
    for cx in range(30, w - 20, 24):
        d.line([x + cx, y + h - 16, x + cx, y + h - 22], fill=(120, 110, 96),
               width=2)


def art_voyager(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 30))
    for sx, sy in [(10, 8), (30, 20), (60, 6), (90, 16), (130, 8), (160, 18),
                   (185, 6), (45, 28), (110, 26), (150, 28)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    # dish + body + boom
    d.polygon([(x + 70, y + 10), (x + 110, y + 10), (x + 90, y + 24)],
              fill=(200, 200, 210))
    d.rectangle([x + 82, y + 24, x + 98, y + 30], fill=(180, 180, 190))
    d.line([x + 98, y + 27, x + 150, y + 27], fill=(180, 180, 190), width=2)
    d.ellipse([x + 152, y + 20, x + 166, y + 34], fill=(212, 169, 60))


def art_euro(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 60, 130))
    import math
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx = x + w // 2 + int(52 * math.cos(a)) - 3
        sy = y + h // 2 + int(10 * math.sin(a)) - 3
        d.ellipse([sx, sy, sx + 6, sy + 6], fill=(255, 222, 60))
    d.text((x + w // 2 - 8, y + h // 2 - 12), "€", font=font(SANS_B, 20),
           fill=(255, 255, 255))


def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 90, 110))
    import math
    cx, cy = x + w // 2, y + h // 2
    for r in range(4, 17, 4):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
              fill=(255, 255, 255), width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 222, 90))
    d.text((x + 8, y + h - 14), "35 kt", font=font(SANS_B, 11),
           fill=(255, 255, 255))


def art_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 44))
    d.ellipse([x + w // 2 - 14, y + 3, x + w // 2 + 14, y + 31],
              fill=(247, 147, 26))
    d.text((x + w // 2 - 7, y + 6), "B", font=font(SANS_B, 20),
           fill=(255, 255, 255))
    d.line([(x + 10, y + 8), (x + 40, y + 20), (x + 70, y + 14),
            (x + 100, y + 26), (x + 130, y + 22), (x + 170, y + 30)],
           fill=(220, 60, 60), width=3)


def art_tanks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 196, 150))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(190, 160, 110))
    d.rectangle([x + 60, y + 12, x + 130, y + 24], fill=(90, 84, 70))
    d.rectangle([x + 76, y + 6, x + 108, y + 13], fill=(90, 84, 70))
    d.line([x + 108, y + 9, x + 150, y + 9], fill=(90, 84, 70), width=3)
    for wx in (66, 84, 102, 120):
        d.ellipse([x + wx, y + 24, x + wx + 10, y + 32], fill=(60, 56, 48))


def art_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 60, 90))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(12, 44, 66))
    # ship
    d.polygon([(x + 60, y + h - 12), (x + 140, y + h - 12), (x + 130, y + h - 4),
               (x + 70, y + h - 4)], fill=(200, 200, 200))
    d.rectangle([x + 88, y + h - 22, x + 112, y + h - 12], fill=(180, 60, 50))
    # red arcs (strikes)
    for cx in (30, 170):
        d.arc([x + cx - 12, y + 2, x + cx + 12, y + 26], start=200, end=340,
              fill=(255, 90, 60), width=3)


def art_protest(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 226, 200))
    for i, hx in enumerate(range(14, w - 10, 22)):
        c = (176, 42, 42) if i % 3 == 0 else (30, 90, 160) if i % 3 == 1 else (60, 60, 60)
        d.ellipse([x + hx, y + 12, x + hx + 12, y + 24], fill=c)
        d.rectangle([x + hx - 2, y + 25, x + hx + 14, y + h - 4], fill=c)
    d.rectangle([x + 70, y + 6, x + 124, y + 14], fill=(247, 243, 233),
                outline=(176, 42, 42))


ART = {"shenzhen": art_shenzhen, "vicecity": art_vicecity, "ipo": art_ipo,
       "vangogh": art_vangogh, "court": art_court, "bridge": art_bridge,
       "voyager": art_voyager, "euro": art_euro, "cyclone": art_cyclone,
       "bitcoin": art_bitcoin, "tanks": art_tanks, "gulf": art_gulf,
       "protest": art_protest}

REGION_COLOR = {r["name"]: r["color"] for r in DATA["regions"]}

# Dotted world map land cells: (row, col_start, col_end), grid 26 x 52.
LAND = [
    (1, 30, 38), (1, 42, 48),
    (2, 3, 6), (2, 12, 16), (2, 32, 50),
    (3, 2, 8), (3, 11, 17), (3, 24, 28), (3, 31, 51),
    (4, 2, 9), (4, 11, 17), (4, 24, 30), (4, 31, 51),
    (5, 2, 10), (5, 12, 17), (5, 24, 31), (5, 31, 50),
    (6, 3, 11), (6, 13, 17), (6, 25, 31), (6, 31, 49),
    (7, 4, 12), (7, 14, 18), (7, 25, 30), (7, 31, 47),
    (8, 5, 12), (8, 15, 18), (8, 25, 32), (8, 32, 46),
    (9, 7, 12), (9, 24, 33), (9, 33, 45),
    (10, 8, 12), (10, 14, 16), (10, 24, 33), (10, 34, 44),
    (11, 14, 19), (11, 24, 32), (11, 35, 42),
    (12, 15, 20), (12, 25, 32), (12, 36, 40),
    (13, 15, 20), (13, 25, 31), (13, 42, 44),
    (14, 15, 19), (14, 26, 30), (14, 43, 48),
    (15, 16, 19), (15, 26, 30), (15, 43, 48),
    (16, 16, 18), (16, 27, 29), (16, 44, 48),
    (17, 16, 18), (17, 27, 29), (17, 44, 47),
    (18, 16, 17), (18, 45, 46),
    (19, 16, 17),
    (20, 17, 17),
]


def hexcol(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 110], fill=NAVY)
    d.rectangle([0, 110, W, 112], fill=GOLD)
    d.text((16, 10), DATA["meta"]["kicker"], font=font(SANS_B, 12), fill=GOLD)
    d.text((16, 28), DATA["meta"]["title"].split(" — ")[0],
           font=font(SERIF_B, 38), fill=(255, 255, 255))
    # date badge, top right
    badge = "THU · 19 NOV 2026"
    bw = text_w(d, badge, font(SANS_B, 13)) + 22
    d.rounded_rectangle([W - 16 - bw, 12, W - 16, 40], radius=6,
                        outline=GOLD, width=2)
    d.text((W - 16 - bw + 11, 19), badge, font=font(SANS_B, 13), fill=GOLD)
    d.text((16, 78), DATA["meta"]["deck"], font=font(SANS, 13),
           fill=(210, 215, 225))
    d.text((16, 96), "Drawn from the day's reporting · Prices: CoinGecko",
           font=font(SANS, 9), fill=(150, 160, 175))

    # ---- region strip ----
    y = 120
    d.text((16, y), "REGIONS", font=font(SANS_B, 11), fill=INK)
    rx = 92
    total_w = W - 16 - rx
    per = total_w // len(DATA["regions"])
    for i, r in enumerate(DATA["regions"]):
        cx = rx + i * per
        d.ellipse([cx, y + 1, cx + 10, y + 11], fill=hexcol(r["color"]))
        label = "%s %d" % (r["name"], r["count"])
        d.text((cx + 14, y), label, font=font(SANS_B, 11), fill=INK)

    # ---- timeline strip ----
    y = 146
    d.line([16, y, W - 16, y], fill=LINE, width=1)
    d.text((16, y + 5), "THE DAY IN UTC", font=font(SANS_B, 10), fill=RED)
    slots = DATA["timeline"]
    sw = (W - 32 - 130) // len(slots)
    for i, s in enumerate(slots):
        sx = 146 + i * sw
        d.text((sx, y + 5), s["time"], font=font(SANS_B, 10), fill=INK)
        draw_wrapped(d, s["text"], font(SANS, 9), sx, y + 18, sw - 8, 3,
                     GREY, 11)

    # ---- 3 leads ----
    ly, lh, lw, gap = 190, 182, 322, 10
    for i, s in enumerate(STORIES[:3]):
        x = 16 + i * (lw + gap)
        d.rectangle([x, ly, x + lw, ly + lh], outline=LINE, width=1,
                    fill=(255, 255, 255))
        ART[s["art"]](d, x + 1, ly + 1, lw - 2, 96)
        d.rectangle([x + 1, ly + 97, x + lw - 1, ly + 98], fill=LINE)
        tag = "%d · %s · %s" % (s["id"], s["region"].upper(),
                               s["source"].upper())
        d.text((x + 10, ly + 104), tag, font=font(SANS_B, 9),
               fill=hexcol(REGION_COLOR[s["region"]]))
        draw_wrapped(d, s["headline"], font(SANS_B, 15), x + 10, ly + 117,
                     lw - 20, 2, INK, 16)
        draw_wrapped(d, s["deck"], font(SANS, 11), x + 10, ly + 152, lw - 20,
                     2, GREY, 12)

    # ---- 10 medium cards ----
    my, mh, mw, mgap = 378, 93, 194, 7
    for j, s in enumerate(STORIES[3:13]):
        row, col = divmod(j, 5)
        x = 16 + col * (mw + mgap)
        y = my + row * (mh + 6)
        d.rectangle([x, y, x + mw, y + mh], outline=LINE, width=1,
                    fill=(255, 255, 255))
        d.text((x + 8, y + 4), "%d · %s" % (s["id"], s["region"].upper()),
               font=font(SANS_B, 8),
               fill=hexcol(REGION_COLOR[s["region"]]))
        ART[s["art"]](d, x + 1, y + 14, mw - 2, 30)
        draw_wrapped(d, s["headline"], font(SANS_B, 10), x + 8, y + 46,
                     mw - 16, 2, INK, 11)
        draw_wrapped(d, s["deck"], font(SANS, 8), x + 8, y + 68, mw - 16, 2,
                     GREY, 10)

    # ---- markets + dotted map ----
    y = 576
    d.line([16, y, W - 16, y], fill=LINE, width=1)
    d.text((16, y + 4), "MARKETS · BITCOIN, 24 HOURS (COINGECKO)",
           font=font(SANS_B, 10), fill=INK)
    d.text((362, y + 4), "SNAPSHOT · 19 NOV · FEAR 10",
           font=font(SANS_B, 10), fill=INK)
    d.text((652, y + 4), "WHERE THE NEWS HAPPENED", font=font(SANS_B, 10),
           fill=INK)
    # BTC chart
    pts = DATA["markets"]["btc_hourly_usd"]
    cx0, cy0, cw, ch = 16, y + 18, 330, 48
    lo, hi = min(pts), max(pts)
    px = [cx0 + i * cw / (len(pts) - 1) for i in range(len(pts))]
    py = [cy0 + ch - (p - lo) / (hi - lo) * ch for p in pts]
    poly = list(zip(px, py)) + [(px[-1], cy0 + ch), (px[0], cy0 + ch)]
    d.polygon(poly, fill=(220, 235, 225))
    d.line(list(zip(px, py)), fill=TEAL, width=2)
    d.text((cx0, cy0 + ch + 2), "$62,181 low", font=font(SANS, 8), fill=GREY)
    last = "$63,633  -1.6% 24h"
    d.text((cx0 + cw - text_w(d, last, font(SANS_B, 8)), cy0 + ch + 2), last,
           font=font(SANS_B, 8), fill=RED)
    # snapshot table
    sy = y + 18
    for i, row in enumerate(DATA["markets"]["snapshot"]):
        ry = sy + i * 11
        d.text((362, ry), row["asset"], font=font(SANS_B, 9), fill=INK)
        d.text((430, ry), row["price"], font=font(SANS, 9), fill=INK)
        d.text((540, ry), row["change"], font=font(SANS_B, 9),
               fill=RED if row["change"].startswith("-") else TEAL)
    # dotted map
    mx0, my0, mw2, mh2 = 652, y + 22, 356, 54
    for r, c0, c1 in LAND:
        for c in range(c0, c1 + 1):
            dx = mx0 + (c + 0.5) * mw2 / 52
            dy = my0 + (r + 0.5) * mh2 / 26
            d.ellipse([dx - 2, dy - 1, dx + 2, dy + 1], fill=(150, 160, 175))
    # pins 1-13: cluster pins that share a spot, lay each cluster out in
    # a short horizontal row, shifting right only until clear of earlier pins
    raw = []
    for s in STORIES[:13]:
        raw.append((mx0 + (s["lon"] + 180) / 360 * mw2,
                    my0 + (90 - s["lat"]) / 180 * mh2))
    parent = list(range(13))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(13):
        for j in range(i + 1, 13):
            if (abs(raw[i][0] - raw[j][0]) < 11
                    and abs(raw[i][1] - raw[j][1]) < 11):
                parent[find(i)] = find(j)
    clusters = {}
    for i in range(13):
        clusters.setdefault(find(i), []).append(i)
    ordered = sorted(clusters.values(),
                     key=lambda m: sum(raw[k][0] for k in m) / len(m))
    final = [None] * 13
    placed_xy = []
    for members in ordered:
        members = sorted(members)
        mx = sum(raw[k][0] for k in members) / len(members)
        my = sum(raw[k][1] for k in members) / len(members)
        n = len(members)
        row = [(mx + (k - (n - 1) / 2) * 11, my) for k in range(n)]
        for _ in range(12):
            clash = False
            for (rx, ry) in row:
                for (ex, ey) in placed_xy:
                    if abs(rx - ex) < 11 and abs(ry - ey) < 11:
                        clash = True
            if not clash:
                break
            row = [(rx + 11, ry) for (rx, ry) in row]
        for k, pos in zip(members, row):
            final[k] = pos
            placed_xy.append(pos)
    for k, s in enumerate(STORIES[:13]):
        px, py = final[k]
        ox, oy = raw[k]
        if px != ox or py != oy:
            d.line([(ox, oy), (px, py)], fill=RED, width=1)
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED,
                  outline=(255, 255, 255), width=1)
        num = str(s["id"])
        d.text((px - text_w(d, num, font(SANS_B, 7)) / 2, py - 4), num,
               font=font(SANS_B, 7), fill=(255, 255, 255))

    # ---- briefs 14-50 ----
    y = 656
    d.line([16, y, W - 16, y], fill=LINE, width=1)
    d.text((16, y + 5), "ALSO ON THURSDAY 19 NOVEMBER",
           font=font(SANS_B, 12), fill=INK)
    d.text((W - 16 - text_w(d, "37 more stories, one line each",
                            font(SANS, 10)), y + 6),
           "37 more stories, one line each", font=font(SANS, 10), fill=GREY)
    briefs = STORIES[13:]
    col_w = 486
    line_h = 12.0
    for k, s in enumerate(briefs):
        col, row = divmod(k, 19)
        bx = 16 + col * 504
        by = y + 24 + row * line_h
        line = "%d. %s — %s" % (s["id"], s["headline"], s["source"])
        if text_w(d, line, font(SANS, 10)) > col_w:
            raise ValueError("brief too wide: %r" % line)
        d.text((bx, by), line, font=font(SANS, 10), fill=INK)

    # ---- date check ----
    y = 912
    d.rectangle([16, y, W - 16, y + 66], outline=RED, width=1,
                fill=(255, 246, 244))
    d.text((26, y + 4), "DATE CHECK — WHAT WE LEFT OUT",
           font=font(SANS_B, 10), fill=RED)
    for i, line in enumerate(DATA["date_check"]):
        d.text((26, y + 17 + i * 9.5), line, font=font(SANS, 8), fill=INK)

    # ---- footer ----
    d.text((16, 984), DATA["sources_line"], font=font(SANS, 9), fill=GREY)
    d.text((16, 996), "Quiet Meridian · Thursday 19 November 2026 · "
           "All 50 stories happened, or were first reported, on this day.",
           font=font(SANS, 9), fill=GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    img = build()
    img.save(out, format="PNG")
    with open(out, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print("wrote %s sha256=%s" % (out, digest))


if __name__ == "__main__":
    main()
