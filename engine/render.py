"""Render one part: frames drawn in PIL, piped to ffmpeg, then muxed with the audio mix."""
import json, math, re, subprocess, sys
from PIL import Image, ImageDraw
import numpy as np
from draw import *
from scenes import SCENES

CAP_Y = 1330
CAP_SIZE = 74
CAP_MAXW = 800


def paper_bg():
    rng = np.random.default_rng(7)
    base = np.ones((H, W, 3), np.float32) * np.array(PAPER, np.float32)
    noise = rng.normal(0, 5.0, (H // 4, W // 4)).astype(np.float32)
    noise = np.array(Image.fromarray(noise).resize((W, H), Image.BICUBIC))
    fine = rng.normal(0, 2.5, (H, W)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.07 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img = (base + (noise + fine)[..., None]) * vig[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def band_mask():
    m = np.zeros((H, W), np.float32)
    m[:365] = 1
    m[365:392] = np.linspace(1, 0, 27)[:, None]
    m[1212:1240] = np.linspace(0, 1, 28)[:, None]
    m[1240:] = 1
    return Image.fromarray((m * 255).astype(np.uint8))


def build_chunks(tl):
    words = [w for sc in tl["scenes"] for ln in sc["lines"] for w in ln["words"]]
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        end_punct = re.search(r"[.,?!:]$", w["w"])
        if len(cur) >= 3 or end_punct or len(txt) > 16:
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    out = []
    for i, ch in enumerate(chunks):
        s, e = ch[0]["s"], ch[-1]["e"]
        nxt = chunks[i + 1][0]["s"] if i + 1 < len(chunks) else e + 0.6
        show_to = nxt if nxt - e < 0.6 else e + 0.25
        out.append(dict(words=ch, s=s, e=show_to))
    return out


def clean(w):
    return w.strip('"').upper().rstrip(",:")


def draw_caption(img, chunk, t):
    d = ImageDraw.Draw(img)
    f = font(F_BLACK, CAP_SIZE)
    words = [clean(w["w"]) for w in chunk["words"]]
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    # wrap into lines
    lines, cur, cw = [], [], 0
    for i, wd in enumerate(widths):
        if cur and cw + space + wd > CAP_MAXW:
            lines.append(cur); cur, cw = [], 0
        cur.append(i); cw += (space if len(cur) > 1 else 0) + wd
    lines.append(cur)
    k = min(1.0, (t - chunk["s"]) / 0.12)
    sc = 0.86 + 0.14 * k
    lh = CAP_SIZE * 1.18
    y0 = CAP_Y - (len(lines) - 1) * lh / 2
    for li, ln in enumerate(lines):
        tot = sum(widths[i] for i in ln) + space * (len(ln) - 1)
        x = W / 2 - tot / 2
        y = y0 + li * lh
        for i in ln:
            w = chunk["words"][i]
            active = w["s"] <= t < w["e"] + 0.05
            if active:
                pad = 12
                d.rounded_rectangle([x - pad, y - CAP_SIZE * 0.62, x + widths[i] + pad, y + CAP_SIZE * 0.55],
                                    radius=14, fill=YEL)
            d.text((x, y), words[i], font=f, fill=INK, anchor="lm")
            x += widths[i] + space


def draw_header(img, tl, t):
    d = ImageDraw.Draw(img)
    fb = font(F_BLACK, 30)
    badge = tl["badge"]
    bw = fb.getlength(badge) / 2 + 26
    d.rounded_rectangle([540 - bw, 222, 540 + bw, 270], radius=24, fill=RED)
    d.text((540, 246), badge, font=fb, fill=WHITE, anchor="mm")
    d.text((540, 318), tl["title"], font=font(F_MARK, 58), fill=INK, anchor="mm")


def main(part, preview=None):
    tl = json.load(open(f"out/{part}_timeline.json"))
    D = tl["duration"] + TAIL
    nfr = int(D * FPS)
    bg = paper_bg()
    mask = band_mask()
    boxes = [(0, 0, W, 392), (0, 1212, W, H)]
    chunks = build_chunks(tl)
    scenes = []
    for sc in tl["scenes"]:
        fn, shots = SCENES[sc["id"]]
        L = [ln["s"] - sc["s"] for ln in sc["lines"]]
        dur = sc["e"] - sc["s"]
        scenes.append(dict(fn=fn, s=sc["s"], e=sc["e"], L=L, shots=sorted(shots(L, dur))))
    scenes[-1]["e"] = D
    scenes[0]["s"] = 0

    def frame(fi):
        t = fi / FPS
        sc = next(s for s in scenes if s["s"] <= t < s["e"] + 1e-6) if t < D else scenes[-1]
        lt = t - sc["s"]
        sh = [s for s in sc["shots"] if s[0] <= lt + 1e-6][-1]
        idx = sc["shots"].index(sh)
        s_end = sc["shots"][idx + 1][0] if idx + 1 < len(sc["shots"]) else sc["e"] - sc["s"]
        u = (lt - sh[0]) / max(0.1, s_end - sh[0])
        z = sh[1] * 1.08 * (1 + 0.04 * u)
        img = bg.copy()
        c = Ctx(img, (z, sh[2], sh[3]), boil=fi // 4)
        sc["fn"](c, lt, sc["L"])
        for bx in boxes:  # paper bands: header and caption zones stay clean
            img.paste(bg.crop(bx), bx[:2], mask.crop(bx))
        draw_header(img, tl, t)
        ch = next((x for x in chunks if x["s"] <= t < x["e"]), None)
        if ch:
            draw_caption(img, ch, t)
        return img

    if preview:
        for ts in preview:
            frame(int(ts * FPS)).save(f"out/prev_{part}_{ts:05.1f}.png")
        return
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", f"out/{part}_video.mp4"], stdin=subprocess.PIPE)
    for fi in range(nfr):
        ff.stdin.write(frame(fi).tobytes())
        if fi % 300 == 0:
            print(part, fi, "/", nfr, flush=True)
    ff.stdin.close(); ff.wait()
    # scene cut times for sound design
    json.dump([s["s"] for s in scenes[1:]], open(f"out/{part}_cuts.json", "w"))
    print("done", part, D)


if __name__ == "__main__":
    part = sys.argv[1]
    prev = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    main(part, prev)
