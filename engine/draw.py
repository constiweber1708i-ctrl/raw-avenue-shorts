"""Stick-figure explainer renderer: draws every frame in code and pipes to ffmpeg."""
import json, math, random, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
import os
CACHE = os.path.expanduser(os.environ.get("RAW_AVENUE_CACHE", "~/.cache/rawavenue"))
FONTS = f"{CACHE}/fonts"
F_MARK = f"{FONTS}/PermanentMarker-Regular.ttf"
F_HAND = f"{FONTS}/PatrickHand-Regular.ttf"
F_BLACK = f"{FONTS}/ArchivoBlack-Regular.ttf"

PAPER = (246, 241, 231)
INK = (30, 28, 26)
RED = (196, 46, 40)
BLUE = (64, 120, 164)
WATER = (168, 206, 226)
YEL = (255, 210, 60)
GREY = (160, 154, 146)
LIGHT = (222, 214, 200)
WOOD = (150, 104, 66)
BRONZE = (170, 118, 58)
WHITE = (255, 255, 255)

VIS_CY = 820  # centre of the drawing area on screen
TAIL = 1.0    # seconds of end hold


@lru_cache(maxsize=256)
def font(path, size):
    return ImageFont.truetype(path, max(8, int(size)))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def pop(t, t0, d=0.25):
    """0->1 with a small overshoot, starting at t0."""
    x = (t - t0) / d
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1 - math.cos(x * math.pi * 1.5) * (1 - x) * 0.6 - (1 - x) * 0.4


def dirv(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


class Ctx:
    def __init__(self, img, cam, boil):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.z, self.cx, self.cy = cam
        self.boil = boil

    def T(self, p):
        return ((p[0] - self.cx) * self.z + W / 2, (p[1] - self.cy) * self.z + VIS_CY)

    def jit(self, p, amt=2.2):
        r = random.Random(hash((self.boil, round(p[0]), round(p[1]))))
        return (p[0] + r.uniform(-amt, amt), p[1] + r.uniform(-amt, amt))

    def line(self, a, b, w=9, c=INK, wob=True):
        if wob:
            a2, b2 = self.jit(a), self.jit(b)
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            m2 = self.jit(m, 2.8)
            pts = [self.T(a2), self.T(m2), self.T(b2)]
        else:
            pts = [self.T(a), self.T(b)]
        ww = max(1, int(w * self.z))
        self.d.line(pts, fill=c, width=ww, joint="curve")
        r = ww / 2
        for p in (pts[0], pts[-1]):
            self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=c)

    def poly(self, pts, w=8, c=INK, fill=None, closed=True):
        jp = [self.jit(p) for p in pts]
        sp = [self.T(p) for p in jp]
        if fill is not None:
            self.d.polygon(sp, fill=fill)
        if w:
            seq = jp + ([jp[0]] if closed else [])
            for a, b in zip(seq, seq[1:]):
                self.line(a, b, w, c, wob=False)

    def rect(self, x0, y0, x1, y1, w=8, c=INK, fill=None):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w, c, fill)

    def circle(self, p, r, w=8, c=INK, fill=None):
        p = self.jit(p, 1.5)
        x, y = self.T(p)
        rr = r * self.z
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill,
                       outline=c if w else None, width=max(1, int(w * self.z)) if w else 0)

    def ellipse(self, p, rx, ry, w=8, c=INK, fill=None):
        x, y = self.T(p)
        self.d.ellipse([x - rx * self.z, y - ry * self.z, x + rx * self.z, y + ry * self.z],
                       fill=fill, outline=c if w else None, width=max(1, int(w * self.z)) if w else 0)

    def arc(self, p, r, a0, a1, w=7, c=INK):
        x, y = self.T(p)
        rr = r * self.z
        self.d.arc([x - rr, y - rr, x + rr, y + rr], a0, a1, fill=c, width=max(1, int(w * self.z)))

    def text(self, p, s, size=60, c=INK, f=F_MARK, anchor="mm", rot=0, scale=1.0, stroke=0, sc=None):
        if scale <= 0.01 or size * scale < 4:
            return
        fs = size * self.z * scale
        fnt = font(f, fs)
        x, y = self.T(p)
        if rot == 0:
            self.d.text((x, y), s, font=fnt, fill=c, anchor=anchor,
                        stroke_width=int(stroke * self.z * scale), stroke_fill=sc)
            return
        bbox = fnt.getbbox(s, stroke_width=int(stroke * self.z * scale))
        tw, th = bbox[2] - bbox[0] + 40, bbox[3] - bbox[1] + 40
        layer = Image.new("RGBA", (int(tw), int(th)), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((tw / 2, th / 2), s, font=fnt, fill=c, anchor="mm",
                                   stroke_width=int(stroke * self.z * scale), stroke_fill=sc)
        layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
        self.img.paste(layer, (int(x - layer.width / 2), int(y - layer.height / 2)), layer)

    def alpha_poly(self, pts, fill, alpha):
        sp = [self.T(p) for p in pts]
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(sp, fill=fill + (int(alpha * 255),))
        self.img.paste(layer, (0, 0), layer)


# ----------------------------------------------------------------- figures
STAND = dict(t=0, n=0, la1=-18, la2=-8, ra1=18, ra2=8, ll1=-12, ll2=-6, rl1=12, rl2=6)


def P(**kw):
    p = dict(STAND)
    p.update(kw)
    return p


def lerp_pose(a, b, x):
    x = ease(x)
    return {k: a[k] + (b[k] - a[k]) * x for k in a}


def stickman(c, hip, s=1.0, pose=None, rot=0, face="neutral", facing=0, hair=False, bow=False,
             cap=False, mirror=False, horns=False, longhair=False, cast=False, chains=False, w=10):
    pose = pose or STAND
    hx, hy = hip

    def R(v):  # local vector -> world point (rotate by rot, scale)
        x, y = v
        r = math.radians(rot)
        return (hx + (x * math.cos(r) - y * math.sin(r)) * s, hy + (x * math.sin(r) + y * math.cos(r)) * s)

    def add(p, a, L):
        v = dirv(a)
        return (p[0] + v[0] * L, p[1] + v[1] * L)

    o = (0, 0)
    neck = add(o, 180 + pose["t"], 125)
    head = add(neck, 180 + pose["t"] + pose["n"], 44)
    sh = add(neck, pose["t"], 14)
    le = add(sh, pose["la1"], 66); lh = add(le, pose["la2"], 60)
    re_ = add(sh, pose["ra1"], 66); rh = add(re_, pose["ra2"], 60)
    lk = add(o, pose["ll1"], 78); lf = add(lk, pose["ll2"], 78)
    rk = add(o, pose["rl1"], 78); rf = add(rk, pose["rl2"], 78)
    lw = w * s
    for a, b in [(o, neck), (sh, le), (le, lh), (sh, re_), (re_, rh), (o, lk), (lk, lf), (o, rk), (rk, rf)]:
        c.line(R(a), R(b), lw)
    if cast:
        cp = R(((lk[0] + lf[0]) / 2, (lk[1] + lf[1]) / 2 + 10))
        c.circle(cp, 20 * s, w=6 * s, fill=WHITE)
    if chains:
        for i in range(5):
            y = -30 - i * 18
            c.ellipse(R((-6 + (i % 2) * 12, y)), 16 * s, 8 * s, w=5 * s, c=GREY)
    hc = R(head)
    r = 36 * s
    if longhair:
        for dx in (-34, -24, 24, 34):
            c.line(R((head[0] + dx, head[1] - 10)), R((head[0] + dx * 1.15, head[1] + 55)), 7 * s)
    c.circle(hc, r, w=lw * 0.9, fill=PAPER)
    if hair:
        for dx in (-14, 0, 14):
            c.circle(R((head[0] + dx, head[1] - 38)), 9 * s, w=5 * s, fill=INK)
    if cap:
        c.poly([R((head[0] - 38, head[1] - 12)), R((head[0] + 10, head[1] - 46)), R((head[0] + 44, head[1] - 18)),
                R((head[0] + 70 * (1 if facing >= 0 else -1), head[1] - 14))], w=6 * s, fill=INK, closed=True)
    if horns:
        c.poly([R((head[0] - 40, head[1] - 4)), R((head[0], head[1] - 44)), R((head[0] + 40, head[1] - 4))],
               w=6 * s, fill=GREY)
        for sgn in (-1, 1):
            c.poly([R((head[0] + 36 * sgn, head[1] - 20)), R((head[0] + 78 * sgn, head[1] - 72)),
                    R((head[0] + 60 * sgn, head[1] - 20))], w=5 * s, fill=WHITE)
    if mirror:
        c.circle(R((head[0], head[1] - 20)), 12 * s, w=4 * s, fill=LIGHT)
    if bow:
        b0 = R(add(neck, 180 + pose["t"], 4))
        c.poly([(b0[0] - 18 * s, b0[1] - 10 * s), (b0[0] - 18 * s, b0[1] + 10 * s), (b0[0] + 18 * s, b0[1] - 10 * s),
                (b0[0] + 18 * s, b0[1] + 10 * s)], w=0, fill=RED)
    draw_face(c, hc, r, face, facing, s, rot)
    return dict(head=hc, lh=R(lh), rh=R(rh), neck=R(neck), hip=R(o))


def draw_face(c, hc, r, face, facing, s, rot):
    ex = 12 * s
    ox = facing * 10 * s
    up = math.radians(rot)

    def F(dx, dy):  # face-local offset rotated with body
        return (hc[0] + dx * math.cos(up) - dy * math.sin(up), hc[1] + dx * math.sin(up) + dy * math.cos(up))

    if face in ("neutral", "smile", "shock", "worried"):
        for sx in (-1, 1):
            c.circle(F(ox + sx * ex, -6 * s), 4.5 * s, w=0, fill=INK)
    if face == "smile":
        c.arc(F(ox, 2 * s), 14 * s, 20 + rot, 160 + rot, w=4 * s)
    elif face == "neutral":
        c.line(F(ox - 8 * s, 14 * s), F(ox + 8 * s, 14 * s), 4 * s)
    elif face == "shock":
        c.circle(F(ox, 15 * s), 7 * s, w=4 * s)
    elif face == "worried":
        c.arc(F(ox, 24 * s), 11 * s, 200 + rot, 340 + rot, w=4 * s)
    elif face in ("wince", "pain"):
        for sx in (-1, 1):
            c.line(F(ox + sx * ex - 5 * s, -12 * s), F(ox + sx * ex + 5 * sx * s * 0 + sx * 0, -6 * s), 4 * s)
            c.line(F(ox + sx * ex - 5 * s, 0), F(ox + sx * ex, -6 * s), 4 * s)
        pts = [F(ox - 12 * s, 16 * s), F(ox - 4 * s, 11 * s), F(ox + 4 * s, 17 * s), F(ox + 12 * s, 12 * s)]
        for a, b in zip(pts, pts[1:]):
            c.line(a, b, 4 * s, wob=False)
    elif face == "closed":
        for sx in (-1, 1):
            c.line(F(ox + sx * ex - 6 * s, -5 * s), F(ox + sx * ex + 6 * s, -5 * s), 4 * s)
        c.line(F(ox - 6 * s, 14 * s), F(ox + 6 * s, 14 * s), 4 * s)


# ------------------------------------------------------------- props
def calendar(c, p, month, day, year, s=1.0, sc=1.0):
    if sc <= 0:
        return
    s = s * sc
    x, y = p
    w, h = 150 * s, 170 * s
    c.rect(x - w, y - h, x + w, y + h, w=9, fill=WHITE)
    c.rect(x - w, y - h, x + w, y - h + 80 * s, w=9, fill=RED)
    c.text((x, y - h + 42 * s), month, 48 * s, WHITE, F_BLACK)
    c.text((x, y + 20 * s), day, 150 * s, INK, F_MARK)
    c.text((x, y + h - 42 * s), year, 44 * s, INK, F_BLACK)
    for dx in (-80, 80):
        c.circle((x + dx * s, y - h), 14 * s, w=6, fill=GREY)


def stamp(c, p, s, t, t0, rot=-12, size=110, col=RED):
    k = pop(t, t0, 0.22)
    if k <= 0:
        return
    sc = 1 + (1 - k) * 1.6
    c.text(p, s, size, col, F_BLACK, rot=rot, scale=sc)
    fnt = font(F_BLACK, size * c.z * sc)


def bubble(c, p, s, t, t0, size=52, w=None, tail=(0, 1), col=INK, fill=WHITE):
    k = pop(t, t0, 0.22)
    if k <= 0:
        return
    fnt = font(F_MARK, size)
    bb = fnt.getbbox(s)
    tw, th = (bb[2] - bb[0]) / 2 + 36, (bb[3] - bb[1]) / 2 + 30
    tw *= k; th *= k
    x, y = p
    tx, ty = x + tail[0] * tw * 0.4, y + th
    c.poly([(tx - 22 * k, ty - 4), (tx + 60 * tail[0] * k + 8, ty + 50 * k), (tx + 22 * k, ty - 4)], w=7, fill=fill)
    c.poly([(x - tw, y - th), (x + tw, y - th), (x + tw, y + th), (x - tw, y + th)], w=7, fill=fill)
    c.text((x, y + 2), s, size * k, col, F_MARK)


def couch(c, x, y, s=1.0):
    c.rect(x - 230 * s, y - 70 * s, x + 230 * s, y + 30 * s, w=9, fill=RED)
    c.rect(x - 230 * s, y - 150 * s, x - 170 * s, y + 30 * s, w=9, fill=RED)
    c.rect(x + 170 * s, y - 150 * s, x + 230 * s, y + 30 * s, w=9, fill=RED)
    for dx in (-200, 200):
        c.line((x + dx * s, y + 30 * s), (x + dx * s, y + 70 * s), 10)


def tank(c, x, y0, y1, half=150, water=True, t=0, bubbles=True, bub_top=None):
    if water:
        c.rect(x - half, y0 + 50, x + half, y1, w=0, fill=WATER)
        # waves
        for i in range(6):
            xx = x - half + 25 + i * (2 * half - 50) / 5
            c.arc((xx, y0 + 50 + 8 * math.sin(t * 3 + i)), 22, 200, 340, w=4, c=BLUE)
    c.line((x - half, y0), (x - half, y1), 10)
    c.line((x + half, y0), (x + half, y1), 10)
    c.line((x - half, y1), (x + half, y1), 10)
    c.line((x - half + 20, y0 + 70), (x - half + 20, y1 - 40), 4, WHITE)
    if bubbles and bub_top is not None:
        for i in range(7):
            ph = (t * 0.7 + i / 7) % 1
            by = bub_top - ph * (bub_top - y0 - 70)
            bx = x + 20 * math.sin(i * 2.1 + t * 2) + (i - 3) * 8
            c.circle((bx, by), 7 + (i % 3) * 3, w=4, c=BLUE)


def stocks(c, x, y, half=190):
    c.rect(x - half, y - 22, x + half, y + 22, w=8, fill=WOOD)
    for dx in (-20, 20):
        c.circle((x + dx, y), 12, w=5, fill=INK)


def bed(c, x, y, s=1.0):
    c.rect(x - 260, y - 30, x + 260, y + 20, w=9, fill=WHITE)
    c.line((x - 260, y - 110), (x - 260, y + 90), 10)
    c.line((x + 260, y - 60), (x + 260, y + 90), 10)
    c.line((x - 260, y - 110), (x - 200, y - 110), 10)
    c.ellipse((x - 190, y - 48), 55, 26, w=7, fill=WHITE)


def window(c, x, y, moon=True):
    c.rect(x - 110, y - 130, x + 110, y + 130, w=9, fill=(52, 64, 92))
    c.line((x, y - 130), (x, y + 130), 7)
    c.line((x - 110, y), (x + 110, y), 7)
    if moon:
        c.circle((x - 50, y - 70), 28, w=0, fill=(245, 235, 190))
        c.circle((x - 38, y - 78), 24, w=0, fill=(52, 64, 92))


def pin_label(c, p, s, t, t0, size=50):
    k = pop(t, t0)
    if k <= 0:
        return
    x, y = p
    fnt = font(F_BLACK, size)
    bb = fnt.getbbox(s)
    tw = (bb[2] - bb[0]) / 2 + 40
    c.rect(x - tw * k, y - 44 * k, x + tw * k, y + 44 * k, w=7, fill=INK)
    c.text((x, y), s, size * k, WHITE, F_BLACK)


def thermometer(c, x, y, level, label, t, t0):
    k = pop(t, t0)
    if k <= 0:
        return
    c.rect(x - 26, y - 230, x + 26, y + 30, w=8, fill=WHITE)
    c.circle((x, y + 50), 46, w=8, fill=RED)
    lv = y + 30 - level * 250
    c.rect(x - 14, lv, x + 14, y + 30, w=0, fill=RED)
    c.text((x + 150, y - 150), label, 64 * k, RED, F_BLACK)


def audience(c, y, n=7, face="neutral", t=0):
    for i in range(n):
        x = 110 + i * (860 / (n - 1))
        bob = 4 * math.sin(t * 5 + i)
        c.arc((x, y + 60), 60, 180, 360, w=9)
        c.circle((x, y - 12 + bob), 34, w=8, fill=PAPER)
        if face == "shock":
            c.circle((x, y - 4 + bob), 7, w=4)
            for sx in (-1, 1):
                c.circle((x + sx * 11, y - 20 + bob), 4, w=0, fill=INK)


def curtains(c, closed):
    """closed: 0 open .. 1 fully closed"""
    wdt = 80 + closed * 460
    for side in (-1, 1):
        x_edge = 540 + side * (540 - wdt)
        x_out = 540 + side * 560
        pts = [(x_out, 360), (x_edge, 360), (x_edge + side * 20, 1150), (x_out, 1150)]
        c.poly(pts, w=9, fill=RED)
        for i in range(1, 4):
            xx = x_out + (x_edge - x_out) * i / 4
            c.line((xx, 380), (xx, 1130), 4, (150, 30, 26))
    c.rect(0, 330, 1080, 380, w=0, fill=(120, 24, 22))


def clapper(c, p, s, rot, t):
    x, y = p
    c.rect(x - 230, y - 90, x + 230, y + 160, w=9, fill=INK)
    ang = -18 + 18 * ease((t % 2.2) / 0.3) if (t % 2.2) < 0.3 else 0
    r = math.radians(-ang)
    base = (x - 230, y - 90)

    def rp(dx, dy):
        return (base[0] + dx * math.cos(r) - dy * math.sin(r), base[1] + dx * math.sin(r) + dy * math.cos(r))
    c.poly([rp(0, 0), rp(460, 0), rp(460, -60), rp(0, -60)], w=9, fill=WHITE)
    for i in range(5):
        c.poly([rp(20 + i * 92, 0), rp(66 + i * 92, 0), rp(96 + i * 92, -60), rp(50 + i * 92, -60)], w=0, fill=INK)
    c.text((x, y + 5), s, 64, WHITE, F_BLACK)
    c.text((x, y + 90), "HOUDINI", 44, (220, 210, 190), F_MARK)


def fist_burst(c, p, r, t, col=YEL):
    x, y = p
    pts = []
    for i in range(20):
        a = i / 20 * 2 * math.pi
        rr = r if i % 2 == 0 else r * 0.55
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, w=8, fill=col)


def candle(c, x, y, lit, t):
    c.rect(x - 22, y - 110, x + 22, y + 40, w=7, fill=WHITE)
    c.line((x, y - 110), (x, y - 128), 5)
    if lit > 0:
        fl = 1 + 0.12 * math.sin(t * 17) + 0.08 * math.sin(t * 29)
        h = 58 * fl * lit
        c.alpha_poly([(x - 90, y - 170), (x + 90, y - 170), (x + 90, y - 80), (x - 90, y - 80)], YEL, 0.0)
        c.poly([(x, y - 128 - h), (x + 18 * lit, y - 140), (x, y - 126), (x - 18 * lit, y - 140)], w=4, c=RED, fill=YEL)
    else:
        for i in range(4):
            yy = y - 140 - i * 30 - (t * 40) % 30
            c.arc((x + 12 * math.sin(yy / 20), yy), 14, 90, 270, w=4, c=GREY)


def viking(c, hip, t, face="smile"):
    return stickman(c, hip, 1.25, P(la1=-60 + 10 * math.sin(t * 4), la2=-120, ra1=40, ra2=20), face=face, horns=True)
