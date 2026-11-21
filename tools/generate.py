#!/usr/bin/env python3
"""tools/generate.py - the front page of Saturday 21 November 2026.

One newspaper page carrying 25 stories of that single day: a lead on the ICJ's
genocide ruling against Myanmar, twelve illustrated blocks in a four-column
grid, and twelve one-line briefs beneath them. Seven regions, ten fields.

Everything is drawn here from primitives (rectangles, polygons, ellipses, arcs):
no photographs, no downloaded artwork, nothing but the system's URW base35
fonts. The page is composed at 2x and downsampled with LANCZOS so type stays
crisp at 1024x1024.

Layout is computed, not eyeballed: every block measures its own wrapped text
and the script asserts that it fits the cell it was given, so an overflow is a
hard error rather than a smudge.

Run: python3 tools/generate.py     (needs Pillow; writes entry.png at repo root)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas ----
S = 2                     # supersample factor
W = H = 1024              # final size in px
OUT = Path(__file__).resolve().parent.parent / "entry.png"

INK = (17, 15, 13)
PAPER = (250, 247, 240)
NAVY = (12, 24, 44)
RED = (176, 28, 36)
GOLD = (232, 194, 108)
GREY = (84, 78, 72)
DARK = (48, 44, 40)
RULE = (168, 160, 148)
TINT = (236, 230, 218)
WHITE = (255, 255, 255)

REGCOL = {
    "EUROPE": (24, 72, 148),
    "ASIA": (170, 26, 40),
    "MIDEAST": (166, 76, 14),
    "AFRICA": (102, 50, 134),
    "AMERICAS": (22, 110, 62),
    "PACIFIC": (0, 108, 116),
    "GLOBAL": (60, 52, 118),
    "MARKETS": (18, 96, 82),
    "SCIENCE": (44, 64, 156),
    "CLIMATE": (28, 108, 78),
}

FDIR = Path("/usr/share/fonts/opentype/urw-base35")
FONTS = {
    "mast": FDIR / "C059-Bold.otf",
    "head": FDIR / "NimbusSansNarrow-Bold.otf",
    "bold": FDIR / "NimbusSans-Bold.otf",
    "body": FDIR / "NimbusSans-Regular.otf",
}

img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)
_fonts = {}
CHECKS = []


def font(kind, size):
    key = (kind, round(size, 2))
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(str(FONTS[kind]), int(round(size * S)))
    return _fonts[key]


def px(v):
    return int(round(v * S))


def tw(s, kind, size):
    return d.textlength(s, font=font(kind, size)) / S


def text(x, y, s, kind="body", size=15, fill=INK, anchor="la", track=0.0):
    f = font(kind, size)
    if track:
        cx = x
        for ch in s:
            d.text((px(cx), px(y)), ch, font=f, fill=fill, anchor="la")
            cx += d.textlength(ch, font=f) / S + track
        return
    d.text((px(x), px(y)), s, font=f, fill=fill, anchor=anchor)


def right(x, y, s, kind="body", size=15, fill=INK):
    d.text((px(x), px(y)), s, font=font(kind, size), fill=fill, anchor="ra")


def center(x, y, s, kind="body", size=15, fill=INK):
    d.text((px(x), px(y)), s, font=font(kind, size), fill=fill, anchor="ma")


def wrap(s, kind, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(trial, kind, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rule(y, x1=0, x2=W, col=INK, w=1):
    d.rectangle([px(x1), px(y), px(x2) - 1, px(y + w) - 1], fill=col)


def vrule(x, y1, y2, col=RULE, w=1):
    d.rectangle([px(x), px(y1), px(x + w) - 1, px(y2) - 1], fill=col)


def box(x1, y1, x2, y2, fill=None, outline=None, w=1):
    d.rectangle([px(x1), px(y1), px(x2) - 1, px(y2) - 1], fill=fill,
                outline=outline, width=max(1, px(w)))


def fit(name, s, kind, size, maxw):
    CHECKS.append((name, 1, 1, tw(s, kind, size), maxw))


def fits(name, used, cap, wid, maxw):
    CHECKS.append((name, used, cap, wid, maxw))


# ---------------------------------------------------------------- icons -----
def icon(kind, x, y, s, col):
    """Small pictogram in an s-px square, drawn from primitives."""
    if kind == "missile":
        d.polygon([(px(x + s * .50), px(y + s * .02)), (px(x + s * .70), px(y + s * .34)),
                   (px(x + s * .70), px(y + s * .70)), (px(x + s * .30), px(y + s * .70)),
                   (px(x + s * .30), px(y + s * .34))], fill=col)
        d.polygon([(px(x + s * .30), px(y + s * .52)), (px(x + s * .08), px(y + s * .74)),
                   (px(x + s * .30), px(y + s * .74))], fill=INK)
        d.polygon([(px(x + s * .70), px(y + s * .52)), (px(x + s * .92), px(y + s * .74)),
                   (px(x + s * .70), px(y + s * .74))], fill=INK)
        d.rectangle([px(x + s * .32), px(y + s * .78), px(x + s * .68), px(y + s * .88)], fill=GOLD)
    elif kind == "chart":
        pts = [(x + s * .06, y + s * .18), (x + s * .32, y + s * .44),
               (x + s * .50, y + s * .30), (x + s * .86, y + s * .82)]
        for i in range(len(pts) - 1):
            d.line([(px(pts[i][0]), px(pts[i][1])), (px(pts[i + 1][0]), px(pts[i + 1][1]))],
                   fill=col, width=max(1, px(2.4)))
        d.polygon([(px(x + s * .62), px(y + s * .82)), (px(x + s * .94), px(y + s * .88)),
                   (px(x + s * .84), px(y + s * .58))], fill=col)
        d.rectangle([px(x + s * .04), px(y + s * .90), px(x + s * .94), px(y + s * .94)], fill=INK)
    elif kind == "pill":
        d.rounded_rectangle([px(x + s * .04), px(y + s * .30), px(x + s * .96), px(y + s * .70)],
                            radius=px(s * .20), fill=col)
        d.rounded_rectangle([px(x + s * .50), px(y + s * .30), px(x + s * .96), px(y + s * .70)],
                            radius=px(s * .20), fill=INK)
    elif kind == "shield":
        d.polygon([(px(x + s * .50), px(y + s * .04)), (px(x + s * .92), px(y + s * .22)),
                   (px(x + s * .86), px(y + s * .60)), (px(x + s * .50), px(y + s * .94)),
                   (px(x + s * .14), px(y + s * .60)), (px(x + s * .08), px(y + s * .22))], fill=col)
        d.line([(px(x + s * .50), px(y + s * .18)), (px(x + s * .50), px(y + s * .78))],
               fill=WHITE, width=max(1, px(1.8)))
    elif kind == "burst":
        import math
        for i in range(8):
            a = math.radians(i * 45)
            d.polygon([(px(x + s * .5 + math.cos(a) * s * .10), px(y + s * .5 + math.sin(a) * s * .10)),
                       (px(x + s * .5 + math.cos(a - .26) * s * .46),
                        px(y + s * .5 + math.sin(a - .26) * s * .46)),
                       (px(x + s * .5 + math.cos(a + .26) * s * .46),
                        px(y + s * .5 + math.sin(a + .26) * s * .46))],
                      fill=col if i % 2 == 0 else INK)
        d.ellipse([px(x + s * .36), px(y + s * .36), px(x + s * .64), px(y + s * .64)], fill=GOLD)
    elif kind == "coin":
        d.ellipse([px(x + s * .04), px(y + s * .04), px(x + s * .96), px(y + s * .96)],
                  fill=col, outline=INK, width=max(1, px(1.8)))
        text(x + s * .5, y + s * .18, "B", "bold", s * .52, WHITE, anchor="ma")
    elif kind == "mic":
        d.rounded_rectangle([px(x + s * .34), px(y + s * .04), px(x + s * .66), px(y + s * .54)],
                            radius=px(s * .16), fill=col)
        d.arc([px(x + s * .16), px(y + s * .20), px(x + s * .84), px(y + s * .74)],
              start=0, end=180, fill=INK, width=max(1, px(2.2)))
        d.rectangle([px(x + s * .46), px(y + s * .72), px(x + s * .54), px(y + s * .90)], fill=INK)
        d.rectangle([px(x + s * .26), px(y + s * .88), px(x + s * .74), px(y + s * .94)], fill=INK)
    elif kind == "globe":
        d.ellipse([px(x + s * .04), px(y + s * .04), px(x + s * .96), px(y + s * .96)], fill=col)
        d.ellipse([px(x + s * .33), px(y + s * .04), px(x + s * .67), px(y + s * .96)],
                  outline=WHITE, width=max(1, px(1.6)))
        d.rectangle([px(x + s * .04), px(y + s * .47), px(x + s * .96), px(y + s * .53)], fill=WHITE)
    elif kind == "ballot":
        box(x + s * .10, y + s * .16, x + s * .90, y + s * .92, fill=col)
        d.rectangle([px(x + s * .22), px(y + s * .02), px(x + s * .78), px(y + s * .20)], fill=INK)
        d.line([(px(x + s * .26), px(y + s * .54)), (px(x + s * .44), px(y + s * .74))],
               fill=WHITE, width=max(1, px(2.6)))
        d.line([(px(x + s * .44), px(y + s * .74)), (px(x + s * .76), px(y + s * .34))],
               fill=WHITE, width=max(1, px(2.6)))
    elif kind == "quake":
        for i, r in enumerate((.16, .30, .44)):
            d.arc([px(x + s * .5 - s * r), px(y + s * .5 - s * r),
                   px(x + s * .5 + s * r), px(y + s * .5 + s * r)],
                  start=200, end=340, fill=col if i == 0 else INK, width=max(1, px(2.2)))
        d.rectangle([px(x + s * .06), px(y + s * .84), px(x + s * .94), px(y + s * .90)], fill=col)
    elif kind == "plane":
        d.polygon([(px(x + s * .94), px(y + s * .10)), (px(x + s * .42), px(y + s * .46)),
                   (px(x + s * .16), px(y + s * .38)), (px(x + s * .06), px(y + s * .48)),
                   (px(x + s * .30), px(y + s * .60)), (px(x + s * .26), px(y + s * .84)),
                   (px(x + s * .36), px(y + s * .90)), (px(x + s * .52), px(y + s * .66)),
                   (px(x + s * .82), px(y + s * .76))], fill=col)
    elif kind == "alert":
        d.polygon([(px(x + s * .50), px(y + s * .04)), (px(x + s * .96), px(y + s * .90)),
                   (px(x + s * .04), px(y + s * .90))], fill=col)
        d.rectangle([px(x + s * .45), px(y + s * .32), px(x + s * .55), px(y + s * .62)], fill=WHITE)
        d.rectangle([px(x + s * .45), px(y + s * .68), px(x + s * .55), px(y + s * .78)], fill=WHITE)


# ------------------------------------------------------------- masthead -----
MH = 96
d.rectangle([0, 0, px(W) - 1, px(MH) - 1], fill=NAVY)

box(20, 10, 104, 86, fill=RED)
center(62, 14, "NOV", "bold", 13, WHITE)
center(62, 28, "21", "bold", 37, WHITE)
center(62, 69, "SAT 2026", "bold", 10.5, GOLD)

text(114, -2, "THE WORLD", "mast", 64, WHITE)
fit("masthead name", "THE WORLD", "mast", 64, 520)
text(116, 64, "SATURDAY 21 NOVEMBER 2026", "bold", 28, GOLD)
fit("masthead date", "SATURDAY 21 NOVEMBER 2026", "bold", 28, 520)

right(1000, 14, "25 STORIES", "bold", 20, WHITE)
right(1000, 42, "7 REGIONS · 10 FIELDS", "bold", 15, GOLD)
right(1000, 64, "ALL OF IT FROM ONE DAY", "body", 13, (184, 194, 212))

# scope line
center(512, 100, "Every story on this page happened, or was first reported, on Saturday 21 November 2026.",
       "body", 18, GREY)
fit("scope line", "Every story on this page happened, or was first reported, on Saturday 21 November 2026.",
    "body", 18, 992)
rule(126, 0, W, NAVY, 3)

# ---------------------------------------------------------------- lead ------
text(24, 132, "COURTS · THE HAGUE · WORLD COURT", "bold", 15, RED, track=0.6)
fit("lead kicker", "COURTS · THE HAGUE · WORLD COURT", "bold", 15, 620)

LEAD_H = ["World court: Myanmar", "committed genocide"]
for i, ln in enumerate(LEAD_H):
    text(24, 152 + i * 44, ln, "head", 42, INK)
    fit("lead headline %d" % i, ln, "head", 42, 630)
text(24, 240, "against the Rohingya", "head", 42, INK)
fit("lead headline 2", "against the Rohingya", "head", 42, 630)

lead_deck = ("The ICJ held a state responsible for genocide for the first time, ordering "
             "Myanmar to let Rohingya return and pay reparations.")
dl = wrap(lead_deck, "body", 20, 630)
for i, ln in enumerate(dl):
    text(24, 292 + i * 24, ln, "body", 20, INK)
fits("lead deck", len(dl), 2, max(tw(l, "body", 20) for l in dl), 630)
assert len(dl) <= 2, dl

vrule(668, 132, 334, RULE, 1)

# courthouse drawing
CX, CY, CW = 682, 132, 318
CH = 150
box(CX, CY, CX + CW, CY + CH, fill=TINT)
d.polygon([(px(CX + 10), px(CY + 60)), (px(CX + CW / 2), px(CY + 14)),
           (px(CX + CW - 10), px(CY + 60))], fill=NAVY)
text(CX + CW / 2, CY + 28, "ICJ", "bold", 15, GOLD, anchor="ma")
box(CX + 14, CY + 60, CX + CW - 14, CY + 72, fill=NAVY)
for i in range(5):
    x0 = CX + 26 + i * 57
    box(x0, CY + 76, x0 + 24, CY + 122, fill=(226, 219, 204), outline=NAVY, w=1.2)
    box(x0 - 4, CY + 74, x0 + 28, CY + 78, fill=NAVY)
    box(x0 - 4, CY + 120, x0 + 28, CY + 124, fill=NAVY)
box(CX + 8, CY + 126, CX + CW - 8, CY + 134, fill=NAVY)
box(CX, CY + 136, CX + CW, CY + 144, fill=(202, 194, 178))

cap = "The Peace Palace in The Hague, seat of the International Court of Justice."
cl = wrap(cap, "body", 14, 318)
for i, ln in enumerate(cl):
    text(682, 288 + i * 16, ln, "body", 14, DARK)
fits("lead caption", len(cl), 2, max(tw(l, "body", 14) for l in cl), 318)

text(682, 322, "Myanmar rejected the ruling as unfair.", "bold", 14, RED)
fit("lead reject", "Myanmar rejected the ruling as unfair.", "bold", 14, 318)

rule(342, 0, W, INK, 2)

# ------------------------------------------------------------ story grid ----
COLW = 236
GX = [24, 274, 524, 774]
GY = [348, 488, 628]
CELL_H = 138

GRID = [
    ("UKRAINE", "WAR", REGCOL["EUROPE"], "missile",
     "Russia fires 400 drones at Ukraine",
     "8 killed in Kyiv; bridges hit."),
    ("MARKETS", "US", REGCOL["MARKETS"], "chart",
     "S&P 500 falls into correction",
     "Down 3.7%; Nvidia off about 14%."),
    ("POLAND", "NATO", REGCOL["EUROPE"], "shield",
     "Russian missiles land in Poland",
     "Warsaw: a provocation. NATO scrambles."),
    ("GAZA", "MIDEAST", REGCOL["MIDEAST"], "burst",
     "Six killed in Israeli strikes",
     "Four of them near Bureij camp."),
    ("HEALTH", "TRIAL", REGCOL["SCIENCE"], "pill",
     "Cancer pill clears tumours",
     "1 in 12 scans clear; most halt growth."),
    ("CRYPTO", "MARKETS", REGCOL["MARKETS"], "coin",
     "Bitcoin falls below $60,000",
     "First time in 4 months; worst since 2022."),
    ("WASHINGTON", "POLITICS", REGCOL["GLOBAL"], "mic",
     "Trump hails Putin after summit",
     "Zelensky: 'He's a killer.' China joins talks."),
    ("TURKIYE", "CLIMATE", REGCOL["CLIMATE"], "globe",
     "COP31 runs into overtime",
     "Minister expects a deal; text may slip."),
    ("S. AFRICA", "VOTE", REGCOL["AFRICA"], "ballot",
     "ANC's worst result since 1994",
     "31%, down from 46%; one province held."),
    ("PERU", "DISASTER", REGCOL["AMERICAS"], "quake",
     "Magnitude 6.7 quake in Peru",
     "Deep Andes tremor; no damage reported."),
    ("GERMANY", "JOBS", REGCOL["EUROPE"], "plane",
     "Lufthansa to cut 1,000 jobs",
     "Frankfurt and Munich; 180m-euro loss."),
    ("DENMARK", "SECURITY", REGCOL["EUROPE"], "alert",
     "Denmark expels Russian attache",
     "Alleged plot to kill a rapper in Copenhagen."),
]

for i, (tag, sub, col, ic, head, fact) in enumerate(GRID):
    cx = GX[i % 4]
    cy = GY[i // 4]
    box(cx, cy, cx + COLW, cy + 3, fill=col)
    icon(ic, cx + COLW - 17, cy + 3, 15, col)
    text(cx, cy + 7, "%s · %s" % (tag, sub), "bold", 12.5, col, track=0.4)
    fit("grid%d tag" % i, "%s · %s" % (tag, sub), "bold", 12.5, COLW - 26)

    hl = wrap(head, "head", 34, COLW)
    for j, ln in enumerate(hl):
        text(cx, cy + 22 + j * 32, ln, "head", 34, INK)
    fits("grid%d head" % i, len(hl), 2, max(tw(l, "head", 34) for l in hl), COLW)

    fy = cy + 22 + len(hl) * 32 + 2
    fl = wrap(fact, "body", 21, COLW)
    for j, ln in enumerate(fl):
        text(cx, fy + j * 23, ln, "body", 21, DARK)
    fits("grid%d fact" % i, len(fl), 2, max(tw(l, "body", 21) for l in fl), COLW)

    used = 22 + len(hl) * 32 + 2 + len(fl) * 23
    assert used <= CELL_H - 2, (tag, used, CELL_H)
    assert len(hl) <= 2 and len(fl) <= 2, (tag, hl, fl)

    if i % 4:
        vrule(cx - 8, cy + 4, cy + CELL_H - 6, RULE, 1)

rule(772, 0, W, INK, 2)

# --------------------------------------------------------------- briefs -----
# 2 columns, 6 briefs each = 12 one-liners, full-height rows at 22px
text(24, 778, "ALSO TODAY", "bold", 15, NAVY, track=1.6)
right(1000, 780, "12 MORE STORIES FROM SATURDAY 21 NOVEMBER 2026", "body", 13, GREY)

BRIEFS = [
    ("FRANCE", "EUROPE", "3 police jailed for 2020 Zecler assault."),
    ("YEMEN", "MIDEAST", "3 Houthi missiles at Riyadh intercepted."),
    ("IRAN", "MIDEAST", "IRGC shoots down US drone over Hormuz."),
    ("JAPAN", "ASIA", "Buys 8m barrels of Saudi crude for reserve."),
    ("CHINA", "ASIA", "Agrees to nuclear talks after the summit."),
    ("BRAZIL", "AMERICAS", "Bolsonaro, 71, in hospital with bowel block."),
    ("HAITI", "AMERICAS", "3 new prisons to be built with El Salvador."),
    ("PACIFIC", "PACIFIC", "Cyclone Xavier hits record strength."),
    ("BRUSSELS", "EUROPE", "EU-UK deepen defence ties."),
    ("U.N.", "GLOBAL", "$52m for 300,000 children in crisis."),
    ("SPACE", "SCIENCE", "BepiColombo reaches Mercury in 8 years."),
    ("UKRAINE", "EUROPE", "Kryvyi Rih strike wounds about 20."),
]

# two equal columns at x=24 and 524, width 488 each
BCX = [24, 524]
BCOLW = 488
BROW = 24  # one line at 22px with 2px padding
for i, (tag, reg, body) in enumerate(BRIEFS):
    col = i % 2
    row = i // 2
    x = BCX[col]
    y = 806 + row * BROW
    colr = REGCOL[reg]

    full = "%s %s" % (tag, body)
    fit("brief %s" % tag, full, "body", 21, BCOLW)
    # draw tag in region color, rest in INK
    tlen = tw(tag, "bold", 12.5)
    text(x, y, tag, "bold", 12.5, colr)
    text(x + tlen + 6, y, body, "body", 21, INK)

# vertical rule between the two brief columns
vrule(516, 798, 950, RULE, 1)

# --------------------------------------------------------------- footer -----
rule(958, 0, W, NAVY, 2)
d.rectangle([0, px(962), px(W) - 1, px(H) - 1], fill=NAVY)
text(24, 970, "THE WORLD", "mast", 22, WHITE)
text(24, 1000, "SATURDAY 21 NOVEMBER 2026", "bold", 17, GOLD)
fit("footer date", "SATURDAY 21 NOVEMBER 2026", "bold", 17, 420)
right(1000, 972, "25 STORIES · 7 REGIONS · 10 FIELDS", "bold", 15, WHITE)
fit("footer counts", "25 STORIES · 7 REGIONS · 10 FIELDS", "bold", 15, 460)
right(1000, 998, "DATE-CHECKED · WIRE REPORTS · PAGE 1", "body", 13, (186, 196, 214))
fit("footer note", "DATE-CHECKED · WIRE REPORTS · PAGE 1", "body", 13, 460)

# ------------------------------------------------------------ downsample ----
img = img.resize((W, H), Image.LANCZOS)
img.save(OUT, "PNG", optimize=True)

# -------------------------------------------------------------- report ------
bad = [c for c in CHECKS if (c[2] is not None and c[1] > c[2]) or c[3] > c[4] + 0.5]
for name, used, cap, wid, maxw in bad:
    print("FIT FAIL  %-22s lines %s/%s  width %.1f/%.1f" % (name, used, cap, wid, maxw))
print("checked %d text blocks, %d fail" % (len(CHECKS), len(bad)))
print("wrote %s  %d bytes  %dx%d" % (OUT, OUT.stat().st_size, W, H))
if bad:
    raise SystemExit(1)
