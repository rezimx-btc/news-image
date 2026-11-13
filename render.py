#!/usr/bin/env python3
"""Render the news-image-01 entry: a one-page newspaper front page summing up
Friday 13 November 2026. Output: news.png (1024x1024, flat colours, exact text).
Deterministic: same bytes every run (no timestamps, no randomness)."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (255, 255, 255)   # pure white — max contrast
INK = (0, 0, 0)           # pure black
RED = (196, 12, 12)       # deeper, more saturated lead accent
GREY = (58, 58, 58)       # dark grey — was too light to read
SEA = (16, 48, 96)        # richer blue sea band
SEA2 = (23, 44, 74)
SAND = (245, 228, 190)    # brighter sky strip
GOLD = (232, 175, 10)     # brighter gold sun

def font(name, size):
    cands = [
        f"/usr/share/fonts/truetype/noto/{name}",
        f"/usr/share/fonts/truetype/dejavu/{name}",
    ]
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

F_MAST = font("NotoSerif-Bold.ttf", 84)
F_DATE = font("NotoSans-Bold.ttf", 21)
F_KICK = font("NotoSans-Bold.ttf", 23)
F_LEAD = font("NotoSerif-Bold.ttf", 46)
F_DECK = font("NotoSerif-Regular.ttf", 22)
F_H2 = font("NotoSerif-Bold.ttf", 24)
F_BODY = font("NotoSans-Regular.ttf", 18)
F_NUM = font("NotoSerif-Bold.ttf", 28)
F_FOOT = font("NotoSans-Regular.ttf", 16)
F_SRC = font("NotoSans-Bold.ttf", 16)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
MX = 36  # margin

def text_cx(y, s, f, fill=INK):
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2, y), s, font=f, fill=fill)

def rule(y, fill=INK, w=2):
    d.line([(MX, y), (W - MX, y)], fill=fill, width=w)

def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---- masthead ----
text_cx(28, "THE WORLD", F_MAST)
rule(140)
text_cx(152, "FRIDAY, 13 NOVEMBER 2026  •  THE DAY IN ONE PAGE", F_DATE, fill=GREY)
rule(186, fill=RED, w=3)

# ---- lead story ----
y = 200
d.text((MX, y), "LEAD STORY — THE GULF IN FLAMES", font=F_KICK, fill=RED)
y += 32
lead = "IRAN HITS U.S. RADAR; FOUR TANKERS STRUCK IN HORMUZ"
for ln in wrap(lead, F_LEAD, W - 2 * MX):
    d.text((MX, y), ln, font=F_LEAD, fill=INK)
    y += 53
y += 2
deck = "Tehran claims a U.S. early-warning radar destroyed in Bahrain as explosions hit four ships in the Strait of Hormuz. Washington silent; oil risk spikes."
for ln in wrap(deck, F_DECK, W - 2 * MX):
    d.text((MX, y), ln, font=F_DECK, fill=INK)
    y += 27
y += 6

# ---- lead visual: flat strait scene ----
vx0, vy0, vx1, vy1 = MX, y, W - MX, y + 132
d.rectangle([vx0, vy0, vx1, vy1], fill=SEA)
# sky strip
d.rectangle([vx0, vy0, vx1, vy0 + 44], fill=SAND)
# sun
d.ellipse([vx1 - 96, vy0 + 6, vx1 - 48, vy0 + 54], fill=GOLD)
# radar station (Bahrain, left): tower + dish, hit by a red burst
d.rectangle([vx0 + 62, vy0 + 16, vx0 + 78, vy0 + 44], fill=(20, 20, 20))
d.ellipse([vx0 + 44, vy0 + 2, vx0 + 96, vy0 + 32], fill=(45, 45, 45))
d.line([(vx0 + 70, vy0 + 16), (vx0 + 96, vy0 + 2)], fill=INK, width=4)
# tanker silhouettes
for tx in (300, 560):
    d.rectangle([tx, vy0 + 78, tx + 190, vy0 + 102], fill=(0, 0, 0))
    d.rectangle([tx + 30, vy0 + 62, tx + 70, vy0 + 78], fill=(0, 0, 0))
    d.rectangle([tx + 120, vy0 + 68, tx + 150, vy0 + 78], fill=(0, 0, 0))
# explosion bursts (orange starbursts)
def burst(cx, cy, r, col):
    for a in range(0, 360, 30):
        import math
        x2 = cx + r * math.cos(math.radians(a))
        y2 = cy + r * math.sin(math.radians(a))
        d.line([(cx, cy), (x2, y2)], fill=col, width=6)
    d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=col)
burst(70, vy0 + 12, 22, (255, 45, 0))
burst(395, vy0 + 62, 30, (255, 110, 0))
burst(655, vy0 + 68, 24, (255, 110, 0))
burst(880, vy0 + 60, 20, (255, 110, 0))
# waves
for wy in (vy0 + 112, vy0 + 124):
    for wx in range(vx0 + 10, vx1 - 10, 46):
        d.arc([wx, wy, wx + 34, wy + 12], 180, 360, fill=(120, 165, 225), width=3)
# caption
d.text((MX, vy1 + 6), "The Strait of Hormuz — four tankers hit Wed–Thu; one LNG tanker struck a mine.  •  Map: schematic", font=F_SRC, fill=GREY)
y = vy1 + 30

# ---- ranked stories ----
rule(y, fill=INK, w=2)
y += 12
stories = [
    ("2", "UKRAINE — PEACE TALKS OPEN TO EUROPE",
     "Europe joins the next peace-talk round; Kushner & Witkoff met Putin, then Zelenskyy. The largest prisoner swap is being prepared."),
    ("3", "NVIDIA — CEO RESIGNS, SHARES FALL 16%",
     "Jensen Huang quits as CEO and leaves the board; CFO Colette Kress is interim CEO."),
    ("4", "MICROSOFT — 365 OUTAGE HITS THE WORLD",
     "Mail and Teams fail across regions; businesses, schools and agencies disrupted."),
    ("5", "BINANCE — U.S. TO SEIZE $1.2 BILLION IN CRYPTO",
     "Court approves the seizure after the 29 Oct hack the FBI blames on North Korea."),
    ("6", "GAZA — STRIKE ON KHAN YOUNIS HOSPITAL KILLS 6",
     "Missile hits Nasser hospital's surgical wing; a surgeon among the dead."),
    ("7", "U.S. — VAN HOLLEN CHALLENGES SCHUMER",
     "Senate leadership fight after the midterms; Kansas governor race called."),
    ("8", "ALSO — POPE LEO IN PERU • GEMINI 4 • ENGLAND BEAT CROATIA",
     "Record crowds line Lima's streets; new search model ships; Three Lions reach the quarters."),
]
for num, head, body in stories:
    d.text((MX, y), num, font=F_NUM, fill=RED)
    d.text((MX + 44, y + 2), head, font=F_H2, fill=INK)
    y += 30
    for ln in wrap(body, F_BODY, W - 2 * MX - 44):
        d.text((MX + 44, y), ln, font=F_BODY, fill=INK)
        y += 22
    y += 4

# ---- footer ----
rule(y + 2, fill=RED, w=3)
y += 12
text_cx(y, "Sources: AP  •  Reuters  •  AFP  •  wire reports, 13 November 2026", F_FOOT, fill=GREY)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.png")
img.save(out, "PNG")
print("saved", out, os.path.getsize(out), "bytes")
