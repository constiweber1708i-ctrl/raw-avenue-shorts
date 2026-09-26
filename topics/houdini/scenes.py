"""Scene drawings. Each scene fn(c, t, L) draws world content at t seconds into the scene.
L = list of line start times relative to the scene start. shots(L, D) gives camera cuts."""
import math
from draw import *

HOU = dict(hair=True, bow=True)


def auto_shots(framings, D, every=2.9):
    n = max(1, round(D / every))
    return [(i * D / n,) + framings[i % len(framings)] for i in range(n)]


# ------------------------------------------------------------------ PART 1
def s_hook(c, t, L):
    calendar(c, (330, 780), "OCTOBER", "31", "1926", 1.0, pop(t, -0.2))
    k = pop(t, 0.35)
    c.text((540, 450), "100 YEARS AGO", 74 * k, INK, F_BLACK)
    wig = math.sin(t * 9)
    stickman(c, (780, 1000), 1.15, P(la1=-10 + 6 * wig, la2=-4, ra1=10 - 6 * wig, ra2=4, t=3 * wig),
             face="worried", facing=-1, chains=True, **HOU)
    stamp(c, (330, 790), "MYTH?", t, L[1] + 1.1, rot=-14, size=120)


def shots_hook(L, D):
    return [(0, 1.0, 540, 790), (L[1] - 0.2, 1.45, 330, 780), (L[1] + 1.9, 1.35, 700, 820)]


def houdini_upside(c, x, y, t, face="worried", s=1.0):
    sway = 4 * math.sin(t * 2.2)
    return stickman(c, (x, y), s, P(ll1=-4, ll2=-2, rl1=4, rl2=2, la1=-162 + sway, la2=-172 + sway,
                                    ra1=162 + sway, ra2=172 + sway), rot=180, face=face, **HOU)


def s_tank(c, t, L):
    off = -300 * (1 - ease(t / 2.0))
    tank(c, 540, 560, 1120, water=True, t=t, bubbles=False)
    for x0, x1 in ((330, 400), (750, 680)):
        c.line((x0, 330), (x1, 530 + off), 5, GREY)
    fig = houdini_upside(c, 540, 700 + off, t)
    tank(c, 540, 560, 1120, water=False, t=t, bubbles=t > 2.0, bub_top=fig["head"][1] - 40)
    stocks(c, 540, 540 + off)
    k = pop(t, 0.8)
    c.text((540, 440), "WATER TORTURE CELL", 64 * k, RED, F_MARK)
    if t > L[1] + 0.6:
        pin_label(c, (215, 900), "GLASS", t, L[1] + 0.6, 40)
    if t > L[1] + 2.6:
        pin_label(c, (865, 540), "STOCKS", t, L[1] + 2.6, 40)


def shots_tank(L, D):
    return [(0, 1.0, 540, 790), (2.9, 1.7, 540, 900), (L[1], 1.0, 540, 790), (L[1] + 2.4, 1.55, 560, 640)]


def s_curtain(c, t, L):
    out = t >= L[1]
    tank(c, 540, 600, 1060, half=120, water=True, t=t, bubbles=False)
    fig = houdini_upside(c, 540, 730, t * (0 if out else 1), face="closed" if out else "worried", s=0.8)
    tank(c, 540, 600, 1060, half=120, water=False, t=t, bubbles=not out, bub_top=fig["head"][1] - 30)
    stocks(c, 540, 585, 150)
    closed = ease(t / 1.1) if not out else 1 - ease((t - L[1]) / 1.1)
    curtains(c, closed)
    if not out and t > 1.3:
        span = max(0.1, L[1] - 1.3)
        secs = int(min(2.2, (t - 1.3) / span * 2.2) * 60)
        c.text((540, 720), f"{secs // 60}:{secs % 60:02d}", 190, WHITE, F_BLACK)
    audience(c, 1085, face="shock" if out and t > L[1] + 0.9 else "neutral", t=t)
    stamp(c, (540, 560), "NEVER GOT OUT", t, L[1] + 1.8, rot=-6, size=84)


def shots_curtain(L, D):
    return [(0, 1.0, 540, 800), (1.4, 1.3, 540, 720), (L[1], 1.0, 540, 800), (L[1] + 1.4, 1.4, 540, 800)]


def s_film(c, t, L):
    if t < L[1]:
        clapper(c, (540, 760), "1953", 0, t)
        stamp(c, (540, 540), "HOLLYWOOD", t, 1.4, rot=-8, size=100)
        return
    u = t - L[1]
    for x0, lab in ((70, "MOVIE"), (560, "REALITY")):
        c.rect(x0, 400, x0 + 450, 1130, w=8, fill=WHITE)
        c.text((x0 + 225, 460), lab, 56, INK, F_BLACK)
    tank(c, 295, 640, 1060, half=100, water=True, t=t, bubbles=False)
    houdini_upside(c, 295, 750, 0, face="closed", s=0.62)
    tank(c, 295, 640, 1060, half=100, water=False, t=t, bubbles=False)
    tank(c, 720, 700, 1060, half=80, water=True, t=t, bubbles=False)
    tank(c, 720, 700, 1060, half=80, water=False, t=t, bubbles=False)
    k = ease(u / 0.5)
    stickman(c, (880, 950), 0.72, lerp_pose(STAND, P(la1=-150, la2=-165, ra1=150, ra2=165), k),
             face="smile", facing=-1, **HOU)
    pin_label(c, (785, 560), "BERLIN 1912", t, L[1] + 0.8, 38)
    if u > 3.2:
        kx = ease((u - 3.2) / 0.3)
        c.line((110, 520), (110 + 370 * kx, 520 + 560 * kx), 16, RED)
        c.line((480, 520), (480 - 370 * kx, 520 + 560 * kx), 16, RED)


def shots_film(L, D):
    return [(0, 1.0, 540, 780), (1.6, 1.4, 540, 700), (L[1], 1.0, 540, 770), (L[1] + 1.4, 1.55, 780, 780),
            (L[1] + 3.1, 1.3, 300, 780)]


def s_hospital(c, t, L):
    window(c, 240, 600)
    bed(c, 500, 950)
    stickman(c, (500, 922), 1.0, P(la1=-40, la2=-60, ra1=40, ra2=60, ll1=-2, ll2=0, rl1=2, rl2=0), rot=-90,
             face="closed", **HOU)
    c.rect(480, 900, 770, 955, w=7, fill=LIGHT)
    if t < L[1]:
        pin_label(c, (540, 440), "DETROIT", t, 0.6, 48)
    calendar(c, (800, 610), "OCTOBER", "31", "1926", 0.72, pop(t, 2.5))
    stamp(c, (540, 450), "AGE 52", t, L[1] + 0.1, rot=-6, size=96)


def shots_hospital(L, D):
    return [(0, 1.0, 540, 790), (2.6, 1.45, 760, 660), (5.2, 1.35, 440, 860), (L[1] - 0.1, 1.0, 540, 790)]


def s_dressing(c, t, L):
    # mirror with bulbs
    c.rect(720, 470, 960, 700, w=8, fill=(214, 226, 230))
    for i in range(6):
        c.circle((720 + i * 48, 460), 13, w=5, fill=YEL)
    couch(c, 650, 1010, 0.95)
    stickman(c, (680, 925), 0.95, P(la1=-120, la2=-150, ra1=-100, ra2=-160, ll1=-2, ll2=0, rl1=4, rl2=0),
             rot=-90, face="neutral", facing=1, **HOU)
    c.rect(505, 790, 555, 850, w=5, fill=WHITE)  # letter
    op = ease((t - L[1]) / 0.8) if t > L[1] else 0
    c.rect(80, 640, 310, 1130, w=9, fill=(60, 50, 44))
    if op > 0.25:
        stickman(c, (195, 975), 0.95, P(la1=-10, ra1=40, ra2=-40), face="neutral", facing=1, cap=True)
    dw = 230 * (1 - 0.8 * op)
    c.rect(80, 640, 80 + dw, 1130, w=9, fill=WOOD)
    c.circle((80 + dw - 24, 890), 10, w=4, fill=YEL)
    if t < 2.4:
        pin_label(c, (540, 440), "9 DAYS EARLIER", t, 0.2, 46)
    else:
        pin_label(c, (540, 440), "MONTREAL", t, 2.4, 46)
    k = pop(t, L[1] + 2.4, 0.3)
    c.text((200, 520), "?", 200 * k, RED, F_MARK)


def shots_dressing(L, D):
    return [(0, 1.0, 540, 800), (2.6, 1.5, 680, 870), (L[1], 1.0, 540, 800), (L[1] + 1.8, 1.45, 260, 800)]


def s_cta1(c, t, L):
    k = pop(t, 0.05)
    c.text((540, 560), "PART 2", 190 * k, INK, F_MARK)
    c.text((540, 700), "the punch", 70 * pop(t, 0.6), RED, F_MARK)
    stickman(c, (330, 1000), 1.05, P(ra1=150 + 8 * math.sin(t * 6), ra2=165), face="neutral", facing=1, cap=True)
    stickman(c, (760, 1000), 1.05, P(la1=-30, la2=-60, ra1=30, ra2=60), face="worried", facing=-1, **HOU)
    pin_label(c, (540, 1095), "FOLLOW", t, 1.6, 44)


def shots_cta1(L, D):
    return [(0, 1.0, 540, 800), (2.2, 1.25, 540, 820)]


# ------------------------------------------------------------------ PART 2
def s_hook2(c, t, L):
    pin_label(c, (540, 440), "PART 2", t, 0.0, 52)
    k = pop(t, 0.35, 0.25)
    if k > 0:
        fist_burst(c, (560, 700), 230 * k, t)
        c.text((560, 700), "POW", 120 * k, RED, F_BLACK, rot=-8)
    stickman(c, (560, 1020), 1.1, P(t=-22 if t > 0.5 else 0, la1=40, la2=100, ra1=50, ra2=110),
             face="wince" if t > 0.5 else "neutral", facing=-1, **HOU)


def shots_hook2(L, D):
    return [(0, 1.0, 540, 790), (1.8, 1.35, 560, 820)]


def lying_on_couch(c, face="neutral", cast=True):
    couch(c, 540, 1010)
    stickman(c, (600, 925), 1.0, P(la1=-120, la2=-60, ra1=-110, ra2=-50, ll1=-3, ll2=0, rl1=3, rl2=0), rot=-90,
             face=face, facing=1, cast=cast, **HOU)


def s_couch(c, t, L):
    if t < L[1]:
        calendar(c, (540, 760), "OCTOBER", "22", "1926", 1.0, pop(t, 0.05))
        pin_label(c, (540, 440), "MONTREAL", t, 1.5, 50)
        return
    lying_on_couch(c)
    pin_label(c, (540, 440), "BACKSTAGE", t, L[1] + 0.2, 46)
    if t > L[1] + 2.6:
        k = pop(t, L[1] + 2.6)
        c.text((830, 730), "BROKEN", 50 * k, RED, F_MARK)
        c.text((830, 785), "ANKLE", 50 * k, RED, F_MARK)
        c.line((830, 820), (770, 900), 6, RED)


def shots_couch(L, D):
    return [(0, 1.0, 540, 790), (1.3, 1.35, 540, 700), (L[1], 1.0, 540, 820), (L[1] + 2.4, 1.6, 720, 860)]


def sitting(c, face="neutral", hunch=0, facing=-1, x=660):
    couch(c, 640, 1010)
    return stickman(c, (x, 935), 1.0, P(t=-hunch, n=-hunch * 0.3, ll1=-80, ll2=-5, rl1=-86, rl2=5,
                                        la1=-30 if not hunch else -40, la2=-40 if not hunch else -100,
                                        ra1=30, ra2=40), face=face, facing=facing, **HOU)


def student(c, x, punch=0.0, face="neutral"):
    return stickman(c, (x, 1000), 1.0, lerp_pose(P(ra1=40, ra2=150, la1=-20), P(ra1=88, ra2=90, la1=-40, t=6), punch),
                    face=face, facing=1, cap=True)


def s_question(c, t, L):
    sitting(c, face="smile" if t > L[1] else "neutral")
    student(c, 300)
    pin_label(c, (540, 440), "McGILL STUDENT", t, 0.6, 44)
    bubble(c, (330, 600), "ANY PUNCH?", t, 2.6, 56, tail=(0, 1))
    bubble(c, (760, 610), "YES.", t, L[1] + 0.3, 60, tail=(-1, 1))


def shots_question(L, D):
    return [(0, 1.0, 540, 800), (2.3, 1.45, 330, 760), (L[1] - 0.1, 1.5, 700, 780)]


PUNCHES = [0.35, 1.2, 1.95, 2.7]


def s_punch(c, t, L):
    hits = PUNCHES + [L[1] + 0.3, L[1] + 1.2]
    near = min(abs(t - h) for h in hits)
    k = max(0.0, 1 - near / 0.2)
    hit = k > 0.5
    sitting(c, face="wince" if (hit or t > L[1] + 1.8) else "worried", hunch=18 if hit else 6)
    student(c, 470, punch=k, face="neutral")
    if hit:
        fist_burst(c, (640, 830), 80, t)
        c.text((640, 830), "POW", 40, RED, F_BLACK, rot=-10)
    n = sum(1 for h in hits if t >= h)
    if n:
        c.text((860, 470), f"x{n}", 90, RED, F_BLACK)
    if t > L[1]:
        for i, x in enumerate((110, 200)):
            stickman(c, (x, 1040), 0.7, P(la1=-60, la2=-150, ra1=60, ra2=150), face="shock", facing=1)
        pin_label(c, (330, 440), "WITNESSES", t, L[1] + 1.6, 42)


def shots_punch(L, D):
    return [(0, 1.0, 540, 800), (1.6, 1.6, 600, 840), (L[1] - 0.1, 1.0, 540, 800), (L[1] + 1.9, 1.5, 660, 820)]


def s_doctor(c, t, L):
    doc = stickman(c, (330, 1000), 1.0, P(ra1=60, ra2=-10, la1=-20), face="neutral", facing=1, mirror=True)
    c.rect(doc["rh"][0] - 10, doc["rh"][1] - 60, doc["rh"][0] + 50, doc["rh"][1] + 10, w=6, fill=WHITE)
    stickman(c, (760, 1000), 1.0, P(t=-14, n=-6, la1=40, la2=100, ra1=50, ra2=110), face="pain", facing=-1, **HOU)
    if t < L[1]:
        pin_label(c, (540, 440), "2 DAYS LATER", t, 0.2, 46)
        k = pop(t, 3.4)
        c.text((540, 560), "ACUTE APPENDICITIS", 50 * k, RED, F_MARK)
    else:
        pin_label(c, (540, 440), "SHOW TONIGHT", t, L[1] + 1.0, 46)
    bubble(c, (330, 660), "SURGERY. NOW.", t, max(4.2, L[1] - 1.6), 50, tail=(0, 1))
    bubble(c, (780, 640), "NO.", t, L[1] + 0.25, 64, tail=(0, 1))


def shots_doctor(L, D):
    return [(0, 1.0, 540, 790), (2.9, 1.15, 540, 700), (L[1] - 1.7, 1.5, 330, 780), (L[1], 1.5, 760, 780)]


def s_stage(c, t, L):
    c.alpha_poly([(470, 330), (610, 330), (900, 1060), (180, 1060)], YEL, 0.28)
    c.line((40, 1060), (1040, 1060), 10)
    pin_label(c, (540, 440), "DETROIT", t, 0.0, 50)
    lvl = 0.45 + 0.5 * ease((t - 1.0) / 1.6)
    thermometer(c, 140, 820, lvl, "104°F", t, 0.8)
    if t < L[1] + 0.3:
        rot, hy, pose, face = 0, 904, STAND, "pain"
    else:
        u = t - L[1] - 0.3
        if u < 0.5:
            f = ease(u / 0.5); rot, hy, pose, face = -88 * f, 904 + 120 * f, STAND, "pain"
        elif u < 2.0:
            rot, hy, pose, face = -88, 1024, STAND, "closed"
        else:
            f = ease((u - 2.0) / 0.5)
            rot, hy = -88 * (1 - f), 1024 - 120 * f
            pose, face = lerp_pose(STAND, P(la1=-150, la2=-165, ra1=150, ra2=165), f), "smile" if f > 0.6 else "pain"
    stickman(c, (620, hy), 1.0, pose, rot=rot, face=face, facing=-1, **HOU)


def shots_stage(L, D):
    return [(0, 1.0, 540, 790), (1.4, 1.45, 260, 730), (L[1], 1.0, 560, 820), (L[1] + 2.2, 1.45, 620, 860)]


def s_death(c, t, L):
    if t < 3.2:
        k = pop(t, 0.1)
        fist_burst(c, (540, 760), 190 * k, t, col=RED)
        c.text((540, 760), "BURST", 70 * k, WHITE, F_BLACK)
        pin_label(c, (540, 1040), "PERITONITIS", t, 1.4, 52)
        return
    if t < L[1]:
        k = pop(t, 3.2)
        c.text((280, 760), "1926", 110 * k, INK, F_BLACK)
        c.line((420, 760), (650, 760), 12, INK)
        c.line((610, 725), (655, 760), 12, INK)
        c.line((610, 795), (655, 760), 12, INK)
        k2 = pop(t, 4.3)
        c.text((800, 760), "1928", 110 * k2, RED, F_BLACK)
        pin_label(c, (800, 600), "PENICILLIN", t, 4.6, 40)
        return
    window(c, 240, 600)
    bed(c, 500, 950)
    stickman(c, (500, 922), 1.0, P(la1=-40, la2=-60, ra1=40, ra2=60, ll1=-2, ll2=0, rl1=2, rl2=0), rot=-90,
             face="closed", **HOU)
    c.rect(480, 900, 770, 955, w=7, fill=LIGHT)
    pin_label(c, (540, 440), "HALLOWEEN 1926", t, L[1] + 0.1, 46)


def shots_death(L, D):
    return [(0, 1.0, 540, 790), (1.6, 1.3, 540, 820), (3.2, 1.0, 540, 760), (4.4, 1.4, 760, 700),
            (L[1], 1.0, 540, 790), (L[1] + 1.4, 1.4, 420, 860)]


def s_twist(c, t, L):
    pin_label(c, (540, 440), "THE TWIST", t, 0.0, 50)
    stickman(c, (280, 1000), 1.0, P(ra1=110, ra2=130), face="neutral", facing=1, mirror=True)
    stickman(c, (800, 1000), 1.0, P(la1=-110, la2=-130), face="worried", facing=-1, mirror=True)
    bubble(c, (300, 620), "THE PUNCHES!", t, 1.1, 46, tail=(0, 1))
    bubble(c, (780, 780), "APPENDIX!", t, 2.3, 46, tail=(0, 1))
    k = pop(t, L[1] + 0.4, 0.3)
    c.text((540, 900), "?", 220 * k, RED, F_MARK)


def shots_twist(L, D):
    return [(0, 1.0, 540, 790), (1.0, 1.4, 320, 760), (2.2, 1.4, 760, 840), (L[1], 1.1, 540, 820)]


def s_seance(c, t, L):
    lit = 0.0 if t > L[1] + 1.6 else 1.0
    if lit:
        c.alpha_poly([(540, 1000), (-200, 330), (1280, 330)], YEL, 0.10)
    stickman(c, (540, 1000), 1.0, P(la1=-50, la2=-80, ra1=50, ra2=80), face="neutral", longhair=True)
    for x in (270, 810):
        stickman(c, (x, 1010), 0.9, P(la1=-60, la2=-80, ra1=60, ra2=80), face="neutral", facing=1 if x < 540 else -1)
    c.ellipse((540, 1050), 380, 70, w=9, fill=WOOD)
    candle(c, 700, 1030, lit, t)
    yr = 1927 + min(9, int(t / max(0.1, L[1]) * 9))
    c.text((860, 450), str(yr), 72, INK, F_BLACK)
    msg = "ROSABELLE, BELIEVE"
    n = int(max(0, min(len(msg), (t - 3.0) / 2.6 * len(msg))))
    if n:
        c.text((540, 600), msg[:n], 60, BLUE, F_MARK)


def shots_seance(L, D):
    return [(0, 1.0, 540, 790), (2.8, 1.2, 540, 680), (L[1], 1.0, 540, 790), (L[1] + 1.2, 1.7, 700, 920)]


def s_next(c, t, L):
    pin_label(c, (540, 440), "NEXT MYTH", t, 0.0, 50)
    viking(c, (540, 1000), t, face="smile")
    stamp(c, (540, 640), "MYTH?", t, 1.5, rot=-10, size=110)
    k = pop(t, 3.6, 0.3)
    c.text((850, 800), "?", 220 * k, RED, F_MARK)
    pin_label(c, (540, 1095), "FOLLOW", t, 4.8, 44)


def shots_next(L, D):
    return [(0, 1.0, 540, 800), (1.4, 1.4, 540, 700), (3.4, 1.2, 620, 820), (4.7, 1.0, 540, 800)]


SCENES = {k[2:]: (v, globals()["shots_" + k[2:]]) for k, v in list(globals().items()) if k.startswith("s_")}


def hits(part, tl):
    """Times (s) for impact thumps in the mix."""
    if part != "part2":
        return []
    sc = {s["id"]: s for s in tl["scenes"]}
    p = sc["punch"]
    L1 = p["lines"][1]["s"] - p["s"]
    return [sc["hook2"]["s"] + 0.35] + [p["s"] + h for h in PUNCHES + [L1 + 0.3, L1 + 1.2]]
