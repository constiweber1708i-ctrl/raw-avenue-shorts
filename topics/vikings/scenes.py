"""Scene drawings. Each scene fn(c, t, L) draws world content at t seconds into the scene.
L = list of line start times relative to the scene start. shots(L, D) gives camera cuts."""
import math
from draw import *


def helmet(c, x, y, s=1.0, horns=False, fill=LIGHT, horn_fill=GREY):
    r = 80 * s
    c.circle((x, y), r, w=9, fill=fill)
    c.line((x, y - r * 0.15), (x, y + r * 0.65), 7)
    c.line((x - r * 0.45, y - r * 0.05), (x + r * 0.45, y - r * 0.05), 7)
    for sgn in (-1, 1):
        c.circle((x + r * 0.3 * sgn, y - r * 0.02), r * 0.16, w=5)
    if horns:
        for sgn in (-1, 1):
            c.poly([(x + r * 0.35 * sgn, y - r * 0.15), (x + r * 0.9 * sgn, y - r * 1.1),
                    (x + r * 0.6 * sgn, y - r * 0.15)], w=6, fill=horn_fill)
    return (x, y - r)


def shield(c, x, y, s=1.0):
    c.circle((x, y), 70 * s, w=8, fill=WOOD)
    c.circle((x, y), 22 * s, w=6, fill=GREY)


def axe(c, x, y, rot=0):
    r = math.radians(rot)

    def rp(dx, dy):
        return (x + dx * math.cos(r) - dy * math.sin(r), y + dx * math.sin(r) + dy * math.cos(r))
    c.line(rp(0, -80), rp(0, 90), 8)
    c.poly([rp(-6, -80), rp(56, -50), rp(56, -10), rp(-6, -30)], w=6, fill=GREY)


# ------------------------------------------------------------------ PART 1
def s_hook(c, t, L):
    pin_label(c, (540, 440), "PICTURE A VIKING", t, 0.0, 44)
    viking(c, (540, 1000), t, face="smile")
    k = pop(t, 2.5, 0.25)
    if k > 0:
        c.text((760, 560), "?", 140 * k, RED, F_MARK, rot=10)
    stamp(c, (540, 650), "WRONG", t, 4.3, rot=-10, size=126)


def shots_hook(L, D):
    return [(0, 1.0, 540, 800), (2.4, 1.4, 540, 700), (4.2, 1.25, 540, 780)]


def s_famous(c, t, L):
    viking(c, (420, 1000), t, face="smile")
    shield(c, 760, 960, 0.8)
    axe(c, 830, 980, 10)
    k = pop(t, 0.4)
    c.text((540, 520), "FURS   AXE   HORNS", 54 * k, INK, F_BLACK)
    if t > L[1]:
        labels = ["BEER CANS", "SPORTS LOGOS", "HALLOWEEN"]
        for i, lab in enumerate(labels):
            pin_label(c, (220 + i * 330, 1090), lab, t, L[1] + i * 0.5, 34)


def shots_famous(L, D):
    return [(0, 1.0, 540, 800), (1.6, 1.2, 540, 800), (L[1], 1.05, 540, 820), (L[1] + 1.4, 1.2, 540, 850)]


def s_digs(c, t, L):
    for x0, lab in ((70, "MYTH"), (560, "THE DIGS")):
        c.rect(x0, 430, x0 + 450, 1140, w=8, fill=WHITE)
        c.text((x0 + 225, 470), lab, 50, INK, F_BLACK)
    viking(c, (295, 1010), t, face="smile")
    for sgn, dx in ((-1, 690), (1, 900)):
        axe(c, dx, 1000, 12 * sgn)
    shield(c, 800, 900, 0.7)
    c.line((690, 1050), (900, 1050), 6, GREY)
    pin_label(c, (295, 560), "HORNS", t, 0.4, 34)
    if t > L[1]:
        k = pop(t, L[1])
        c.text((800, 1070), "0", 90 * k, RED, F_BLACK)
        pin_label(c, (800, 620), "NO HELMET HORNS", t, L[1] + 0.3, 34)


def shots_digs(L, D):
    return [(0, 1.0, 540, 790), (1.6, 1.5, 295, 800), (L[1] - 0.2, 1.0, 540, 790), (L[1] + 1.2, 1.5, 800, 850)]


def s_find(c, t, L):
    k = pop(t, 0.3)
    helmet(c, 540, 620, 1.4 * max(0.2, k))
    stamp(c, (760, 560), "ONLY 1", t, 1.8, rot=-8, size=90)
    if t > L[1]:
        pin_label(c, (540, 440), "NORWAY, 1943", t, L[1] + 0.1, 46)
        stickman(c, (300, 1030), 0.95, P(t=22, la1=40, la2=90, ra1=-10, ra2=-70), face="neutral", facing=1)
        c.line((360, 1080), (430, 1120), 8, WOOD)
        c.poly([(420, 1100), (460, 1110), (450, 1135), (415, 1130)], w=5, fill=GREY)
        c.ellipse((640, 1145), 220, 24, w=6, fill=(150, 128, 96))


def shots_find(L, D):
    return [(0, 1.0, 540, 780), (1.6, 1.35, 700, 640), (L[1], 1.0, 540, 800), (L[1] + 1.6, 1.1, 480, 780)]


def s_compare(c, t, L):
    pin_label(c, (540, 440), "GJERMUNDBU HELMET", t, 0.0, 42)
    helmet(c, 540, 720, 2.0)
    stamp(c, (830, 900), "NO HORNS", t, 2.0, rot=-10, size=84)


def shots_compare(L, D):
    return [(0, 1.0, 540, 790), (1.4, 1.5, 540, 700), (2.9, 1.25, 700, 700)]


def s_stage(c, t, L):
    out = t >= L[1]
    closed = 1.0 if not out else 1 - ease((t - L[1]) / 1.2)
    curtains(c, closed)
    if not out:
        stickman(c, (540, 1010), 0.95, P(la1=-70, la2=-20, ra1=70, ra2=20), face="neutral")
        c.poly([(540 - 26, 900), (540, 800), (540 + 26, 900)], w=6, fill=GREY)
    else:
        viking(c, (540, 1010), t, face="smile")
        pin_label(c, (540, 440), "A THEATRE STAGE", t, L[1] + 0.2, 46)


def shots_stage(L, D):
    return [(0, 1.0, 540, 800), (1.5, 1.35, 540, 850), (L[1], 1.0, 540, 800), (L[1] + 1.3, 1.4, 540, 740)]


def s_cta1(c, t, L):
    k = pop(t, 0.05)
    c.text((540, 540), "PART 2", 190 * k, INK, F_MARK)
    c.text((540, 680), "who, where, why", 58 * pop(t, 0.6), RED, F_MARK)
    viking(c, (540, 1010), t, face="smile")
    pin_label(c, (540, 1095), "FOLLOW", t, 1.7, 44)


def shots_cta1(L, D):
    return [(0, 1.0, 540, 800), (2.1, 1.25, 540, 830)]


# ------------------------------------------------------------------ PART 2
def s_hook2(c, t, L):
    pin_label(c, (540, 440), "PART 2", t, 0.0, 52)
    k = pop(t, 1.6, 0.3)
    if k > 0:
        c.text((540, 640), "THE MAN WHO DID IT", 62 * k, RED, F_MARK)
    stickman(c, (540, 1010), 1.05, P(la1=-30, la2=-60, ra1=30, ra2=60), face="neutral", facing=1)


def shots_hook2(L, D):
    return [(0, 1.0, 540, 800), (1.9, 1.3, 540, 750)]


def s_bayreuth(c, t, L):
    curtains(c, 1.0)
    if t > L[1]:
        conductor = stickman(c, (540, 1020), 0.95, P(la1=-100, la2=-20, ra1=100, ra2=20), face="neutral")
        c.line((conductor["rh"][0], conductor["rh"][1]), (conductor["rh"][0] + 60, conductor["rh"][1] - 60), 6)
        pin_label(c, (540, 440), "BAYREUTH, GERMANY", t, L[1] + 0.2, 40)
    else:
        pin_label(c, (540, 440), "1876", t, 0.2, 52)


def shots_bayreuth(L, D):
    return [(0, 1.0, 540, 790), (2.2, 1.3, 540, 700), (L[1], 1.0, 540, 800), (L[1] + 1.5, 1.2, 620, 720)]


def s_doepler(c, t, L):
    designer = stickman(c, (330, 1000), 1.0, P(ra1=60, ra2=-10, la1=-20), face="neutral", facing=1)
    c.rect(500, 620, 780, 900, w=7, fill=WHITE)
    if t < L[1]:
        pin_label(c, (540, 440), "COSTUME DESIGNER", t, 0.3, 40)
    else:
        helmet(c, 640, 760, 1.1, horns=True)
        pin_label(c, (540, 440), "CARL EMIL DOEPLER", t, L[1] + 0.1, 38)


def shots_doepler(L, D):
    return [(0, 1.0, 540, 790), (1.9, 1.2, 330, 800), (L[1], 1.0, 540, 790), (L[1] + 1.4, 1.3, 640, 700)]


def s_spread(c, t, L):
    if t < L[1]:
        audience(c, 940, n=6, face="neutral" if t < 2.0 else "shock", t=t)
        c.rect(320, 520, 760, 760, w=8, fill=WHITE)
        helmet(c, 540, 660, 1.0, horns=True)
        if t > 2.6:
            pin_label(c, (540, 440), "PAINTERS. HOLLYWOOD.", t, 2.6, 40)
    else:
        c.text((260, 700), "1876", 90 * pop(t, L[1]), INK, F_BLACK)
        c.line((420, 700), (650, 700), 10)
        c.line((610, 668), (650, 700), 10)
        c.line((610, 732), (650, 700), 10)
        c.text((820, 700), "NOW", 90 * pop(t, L[1] + 0.7), RED, F_BLACK)
        pin_label(c, (540, 440), "150 YEARS", t, L[1] + 1.2, 44)


def shots_spread(L, D):
    return [(0, 1.0, 540, 800), (1.5, 1.4, 540, 640), (L[1], 1.0, 540, 750), (L[1] + 1.3, 1.3, 540, 720)]


def s_twist(c, t, L):
    pin_label(c, (540, 440), "THE TWIST", t, 0.0, 50)
    k = pop(t, 0.8, 0.3)
    if k > 0:
        c.text((540, 620), "HORNS ARE REAL", 68 * k, INK, F_MARK)
    k2 = pop(t, 2.4, 0.3)
    if k2 > 0:
        c.text((540, 900), "WRONG PEOPLE", 78 * k2, RED, F_MARK, rot=-6)


def shots_twist(L, D):
    return [(0, 1.0, 540, 790), (1.3, 1.3, 540, 680), (2.5, 1.3, 540, 700)]


def s_vekso(c, t, L):
    if t < L[1]:
        helmet(c, 400, 700, 1.15, horns=True, fill=BRONZE, horn_fill=BRONZE)
        helmet(c, 700, 700, 1.15, horns=True, fill=BRONZE, horn_fill=BRONZE)
        pin_label(c, (540, 440), "DENMARK, 1942", t, 0.3, 42)
        c.ellipse((540, 1080), 320, 40, w=6, fill=(96, 92, 62))
    else:
        c.text((280, 720), "1500 BC", 62 * pop(t, L[1]), INK, F_BLACK)
        c.line((440, 720), (640, 720), 8)
        c.line((600, 692), (640, 720), 8)
        c.line((600, 748), (640, 720), 8)
        c.text((840, 720), "VIKINGS", 62 * pop(t, L[1] + 0.8), RED, F_BLACK)
        pin_label(c, (540, 440), "1,500 YEARS APART", t, L[1] + 1.4, 42)


def shots_vekso(L, D):
    return [(0, 1.0, 540, 790), (1.5, 1.3, 450, 700), (L[1], 1.0, 540, 790), (L[1] + 1.5, 1.3, 540, 750)]


def s_next(c, t, L):
    pin_label(c, (540, 440), "NEXT MYTH", t, 0.0, 50)
    fig = stickman(c, (540, 1030), 0.85, P(la1=-20, la2=-10, ra1=20, ra2=30), face="smile", cap=True)
    hx, hy = fig["head"]
    c.poly([(hx - 70, hy - 10), (hx - 10, hy - 46), (hx + 40, hy - 14), (hx + 76, hy - 10)], w=6, fill=INK)
    stamp(c, (540, 660), "SHORT?", t, 1.5, rot=-10, size=100)
    k = pop(t, 3.6, 0.3)
    if k > 0:
        c.text((850, 800), "?", 220 * k, RED, F_MARK)
    pin_label(c, (540, 1095), "FOLLOW", t, 4.8, 44)


def shots_next(L, D):
    return [(0, 1.0, 540, 800), (1.4, 1.4, 540, 700), (3.4, 1.2, 620, 750), (4.7, 1.0, 540, 800)]


SCENES = {k[2:]: (v, globals()["shots_" + k[2:]]) for k, v in list(globals().items()) if k.startswith("s_")}
