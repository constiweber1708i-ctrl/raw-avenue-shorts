"""Profile picture: the channel's stick-figure narrator raising an 'actually...' finger."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))
import numpy as np
from PIL import Image
import draw
from draw import *

S = 1080
draw.VIS_CY = S / 2
rng = np.random.default_rng(7)
base = np.ones((S, S, 3), np.float32) * np.array(PAPER, np.float32) + rng.normal(0, 3, (S, S))[..., None]
img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
c = Ctx(img, (1.0, 540, 540), boil=3)
s = 5.6
fig = stickman(c, (440, 1480), s, P(la1=-12, la2=-5, ra1=128, ra2=172), face="smile", bow=True, w=8)
hx, hy = fig["head"]
# raised eyebrow over the viewer-right eye, flat brow on the other
c.line((hx + 12 * s - 40, hy - 6 * s - 62), (hx + 12 * s + 40, hy - 6 * s - 92), 20)
c.line((hx - 12 * s - 38, hy - 6 * s - 52), (hx - 12 * s + 38, hy - 6 * s - 52), 20)
# fist + pointing finger
fx, fy = fig["rh"]
c.circle((fx, fy), 44, w=18, fill=PAPER)
c.line((fx + 4, fy - 40), (fx + 10, fy - 150), 22)
# small red exclamation lines by the finger
for a in (-40, 0, 40):
    r = math.radians(a - 90)
    c.line((fx + 10 + math.cos(r) * 60, fy - 150 + math.sin(r) * 60),
           (fx + 10 + math.cos(r) * 110, fy - 150 + math.sin(r) * 110), 16, RED)
img.save(os.path.join(os.path.dirname(__file__), "avatar.png"))
# circular preview as TikTok shows it
m = Image.new("L", (S, S), 0)
from PIL import ImageDraw
ImageDraw.Draw(m).ellipse([0, 0, S, S], fill=255)
prev = Image.new("RGB", (S, S), (255, 255, 255)); prev.paste(img, (0, 0), m)
prev.resize((200, 200), Image.LANCZOS).save(os.path.join(os.path.dirname(__file__), "avatar_preview_200.png"))
