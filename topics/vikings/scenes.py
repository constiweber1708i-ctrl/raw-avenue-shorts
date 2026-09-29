"""Vikings scenes: Viking helmets myth."""
import math
from draw import *


def auto_shots(framings, D, every=2.9):
    framings = [(1.0, 540, 790), (1.3, 540, 810)]
    n = max(1, round(D / every))
    return [(i * D / n,) + framings[i % len(framings)] for i in range(n)]


def wide_close(cx=540, cy=790, fx=540, fy=790):
    return [(1.0, cx, cy), (1.45, fx, fy)]


def helmet(c, x, y, s=1.0, horns=False, col=INK):
    c.poly([(x - 70 * s, y), (x - 50 * s, y - 60 * s), (x, y - 85 * s), (x + 50 * s, y - 60 * s), (x + 70 * s, y)],
           w=8, fill=GREY)
    c.line((x - 70 * s, y), (x + 70 * s, y), 8)
    if horns:
        for sg in (-1, 1):
            c.poly([(x + 55 * sg * s, y - 55 * s), (x + 120 * sg * s, y - 150 * s), (x + 90 * sg * s, y - 40 * s)],
                   w=7, fill=WHITE)
    else:
        c.arc((x, y - 10 * s), 40 * s, 20, 160, w=6, c=INK)


def sc_generic(c, t, L, pin, big, stamp_txt=None, fig=True, horns=False, hx=None):
    pin_label(c, (540, 440), pin, t, 0.3, 46)
    if big:
        c.text((540, 580), big, 84 * pop(t, 0.6), INK, F_MARK)
    if fig:
        stickman(c, (hx or 540, 1000), 1.1, P(la1=-40 + 8 * math.sin(t * 3), la2=-70, ra1=40, ra2=60),
                 face="neutral", facing=1, horns=horns)
    if stamp_txt:
        stamp(c, (540, 800), stamp_txt, t, L[-1] if len(L) > 1 else 1.5, rot=-8, size=100)


# ---------------- PART 1
def s_hook(c, t, L):
    pin_label(c, (540, 440), "PICTURE A VIKING", t, 0.2, 46)
    stickman(c, (540, 1000), 1.2, P(la1=-60, la2=-120, ra1=40, ra2=20), face="smile", horns=True)
    stamp(c, (540, 700), "WRONG", t, L[0] + 2.6 if len(L) == 1 else 3.0, rot=-10, size=130)


def shots_hook(L, D): return auto_shots([(1.0, 540, 790), (1.5, 540, 800)], D)


def s_famous(c, t, L):
    pin_label(c, (540, 440), "THE POPULAR IMAGE", t, 0.2, 46)
    stickman(c, (400, 1000), 1.1, P(la1=-60, la2=-120, ra1=40, ra2=20), face="smile", horns=True)
    c.line((640, 850), (640, 1120), 10); c.poly([(580, 830), (700, 830), (660, 900), (620, 900)], w=8, fill=GREY)
    c.text((780, 620), "BEER", 60 * pop(t, 1.0), INK, F_MARK)
    c.text((780, 700), "TEAMS", 60 * pop(t, 1.6), INK, F_MARK)
    c.text((780, 780), "COSTUMES", 60 * pop(t, 2.2), INK, F_MARK)


def shots_famous(L, D): return auto_shots([(1.0, 540, 790), (1.5, 420, 860)], D)


def s_digs(c, t, L):
    pin_label(c, (540, 440), "ARCHAEOLOGY", t, 0.2, 46)
    for i, w in enumerate(("SWORDS", "SHIPS", "SHIELDS", "GRAVES")):
        c.text((270 + (i % 2) * 540, 640 + (i // 2) * 110), w, 62 * pop(t, 0.6 + i * 0.7), INK, F_MARK)
    helmet(c, 540, 1040, 1.4, horns=True)
    if t > L[-1] + 0.3:
        k = ease((t - L[-1] - 0.3) / 0.3)
        c.line((360, 800), (360 + 360 * k, 800 + 300 * k), 18, RED)
        c.line((720, 800), (720 - 360 * k, 800 + 300 * k), 18, RED)
    stamp(c, (540, 700), "ZERO", t, L[-1] + 0.8, rot=-8, size=110)


def shots_digs(L, D): return auto_shots([(1.0, 540, 790), (1.4, 540, 900)], D)


def s_find(c, t, L):
    pin_label(c, (540, 440), "NORWAY 1943", t, 0.2, 46)
    helmet(c, 540, 900, 2.0)
    c.text((540, 1080), "GJERMUNDBU", 64 * pop(t, 1.0), INK, F_BLACK)
    stamp(c, (540, 620), "ONE", t, 1.8, rot=-6, size=130)


def shots_find(L, D): return auto_shots([(1.0, 540, 790), (1.5, 540, 880)], D)


def s_compare(c, t, L):
    for x0, lab in ((70, "MYTH"), (560, "FACT")):
        c.rect(x0, 400, x0 + 450, 1130, w=8, fill=WHITE)
        c.text((x0 + 225, 460), lab, 56, RED if lab == "MYTH" else INK, F_BLACK)
    helmet(c, 295, 850, 1.6, horns=True)
    helmet(c, 785, 850, 1.6)
    c.text((295, 1000), "HORNS", 56, INK, F_MARK)
    c.text((785, 1000), "ROUND CAP", 56, INK, F_MARK)
    if t > 2.5:
        k = ease((t - 2.5) / 0.3)
        c.line((110, 520), (110 + 370 * k, 520 + 560 * k), 16, RED)
        c.line((480, 520), (480 - 370 * k, 520 + 560 * k), 16, RED)


def shots_compare(L, D): return [(0, 1.0, 540, 780), (1.8, 1.5, 300, 830), (3.6, 1.5, 780, 830)][: max(1, min(3, int(D / 1.8)))]


def s_stage(c, t, L):
    pin_label(c, (540, 440), "1000 YEARS LATER", t, 0.2, 46)
    curtains(c, 0.0)
    stickman(c, (540, 1000), 1.1, P(la1=-60, la2=-120, ra1=40, ra2=20), face="smile", horns=True)
    audience(c, 1085, t=t)
    stamp(c, (540, 640), "A STAGE", t, L[-1] if len(L) > 1 else 3, rot=-6, size=100)


def shots_stage(L, D): return auto_shots([(1.0, 540, 800), (1.4, 540, 850)], D)


def s_cta1(c, t, L):
    c.text((540, 640), "PART 2", 200 * pop(t, 0.3), INK, F_MARK)
    stickman(c, (540, 1000), 1.1, P(la1=-60, la2=-120, ra1=40, ra2=20), face="neutral", horns=True)
    pin_label(c, (540, 1095), "FOLLOW", t, 1.5, 48)


def shots_cta1(L, D): return auto_shots([(1.0, 540, 800), (1.35, 540, 800)], D)


# ---------------- PART 2
def s_hook2(c, t, L):
    pin_label(c, (540, 440), "PART 2", t, 0.1, 46)
    c.text((540, 600), "WHO DID IT?", 92 * pop(t, 0.4), RED, F_MARK)
    stickman(c, (540, 1000), 1.1, P(la1=-60, la2=-120, ra1=40, ra2=20), face="smile", horns=True)


def shots_hook2(L, D): return auto_shots([(1.0, 540, 790), (1.45, 540, 800)], D)


def s_bayreuth(c, t, L):
    pin_label(c, (540, 440), "BAYREUTH 1876", t, 0.2, 46)
    curtains(c, 0.0)
    stickman(c, (540, 1000), 1.0, P(la1=-60, la2=-120, ra1=40, ra2=20), face="smile", horns=True)
    audience(c, 1085, t=t)
    c.text((540, 600), "THE RING", 76 * pop(t, 1.0), INK, F_MARK)


def shots_bayreuth(L, D): return auto_shots([(1.0, 540, 800), (1.4, 540, 850)], D)


def s_doepler(c, t, L):
    pin_label(c, (540, 440), "COSTUME DESIGNER", t, 0.2, 46)
    stickman(c, (400, 1000), 1.1, P(la1=-40, la2=-70, ra1=30, ra2=50), face="smile", facing=1)
    helmet(c, 720, 950, 1.8, horns=True)
    c.text((540, 560), "DOEPLER", 80 * pop(t, 0.6), INK, F_MARK)
    stamp(c, (700, 700), "HIS IDEA", t, L[1] if len(L) > 1 else 3, rot=-8, size=90)


def shots_doepler(L, D): return auto_shots([(1.0, 540, 790), (1.5, 700, 900), (1.4, 400, 900)], D)


def s_spread(c, t, L):
    pin_label(c, (540, 440), "IT SPREADS", t, 0.2, 46)
    for i, w in enumerate(("PAINTINGS", "COSTUMES", "CARTOONS", "HOLLYWOOD")):
        c.text((540, 600 + i * 90), w, 66 * pop(t, 0.6 + i * 0.8), INK, F_MARK)
    stamp(c, (540, 1040), "150 YEARS", t, L[-1] if len(L) > 1 else 3.5, rot=-8, size=90)


def shots_spread(L, D): return auto_shots([(1.0, 540, 790), (1.4, 540, 700)], D)


def s_twist(c, t, L):
    pin_label(c, (540, 440), "THE TWIST", t, 0.2, 46)
    helmet(c, 540, 950, 1.7, horns=True)
    stamp(c, (540, 660), "REAL", t, 1.0, rot=-8, size=120)
    c.text((540, 1060), "WRONG PEOPLE", 70 * pop(t, 2.5), INK, F_MARK)


def shots_twist(L, D): return auto_shots([(1.0, 540, 790), (1.5, 540, 900)], D)


def s_vekso(c, t, L):
    pin_label(c, (540, 440), "DENMARK 1942", t, 0.2, 46)
    c.rect(70, 900, 1010, 1130, w=8, fill=(120, 96, 70))
    helmet(c, 330, 900, 1.3, horns=True)
    helmet(c, 750, 900, 1.3, horns=True)
    c.text((540, 570), "BRONZE AGE", 72 * pop(t, 1.0), BRONZE, F_MARK)
    stamp(c, (540, 680), "1,500+ YEARS EARLIER", t, L[2] if len(L) > 2 else 5, rot=-6, size=52)


def shots_vekso(L, D): return auto_shots([(1.0, 540, 790), (1.5, 380, 880), (1.5, 700, 880)], D)


def s_next(c, t, L):
    pin_label(c, (540, 440), "NEXT MYTH", t, 0.0, 50)
    stickman(c, (540, 1000), 1.1, P(la1=-40, la2=-60, ra1=40, ra2=60), face="smile", cap=True)
    stamp(c, (540, 640), "MYTH?", t, 1.5, rot=-10, size=110)
    c.text((850, 800), "?", 220 * pop(t, 3.6, 0.3), RED, F_MARK)
    pin_label(c, (540, 1095), "FOLLOW", t, 4.8, 44)


def shots_next(L, D): return [(0, 1.0, 540, 800), (1.4, 1.4, 540, 700), (3.4, 1.2, 620, 820), (4.7, 1.0, 540, 800)]


SCENES = {k[2:]: (v, globals()["shots_" + k[2:]]) for k, v in list(globals().items()) if k.startswith("s_")}
