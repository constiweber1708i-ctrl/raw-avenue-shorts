"""Narration: offline TTS per sentence, timeline with estimated word timings."""
import json, re, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

import os
TTS = os.path.expanduser(os.environ.get("RAW_AVENUE_CACHE", "~/.cache/rawavenue"))
VOICE = "am_michael"
SPEED = 1.05
SR = 24000
GAP_SENT = 0.16   # between sentences inside a line
GAP_LINE = 0.30   # between lines inside a scene
GAP_SCENE = 0.45  # after a scene
LEAD_IN = 0.15

NUM_WORDS = {  # rough spoken length of numerals, for word-timing weights
    "1926": "nineteen twenty six", "1953": "nineteen fifty three", "1912": "nineteen twelve",
    "1936": "nineteen thirty six", "22nd": "twenty second", "31st": "thirty first",
}


def split_sentences(line):
    # split after . ? ! or : when followed by a space, but not after a lone initial like "J."
    parts, cur = [], ""
    tokens = re.split(r"(?<=[.?!])\s+", line)
    for tok in tokens:
        cur = (cur + " " + tok).strip() if cur else tok
        if re.search(r"\b[A-Z]\.$", cur):  # initial, keep going
            continue
        parts.append(cur)
        cur = ""
    if cur:
        parts.append(cur)
    return parts


def word_weight(w):
    core = re.sub(r"[^\w']", "", w)
    spoken = NUM_WORDS.get(core, core)
    wt = max(2, len(spoken)) + 1.5
    if re.search(r"[,:]$", w):
        wt += 4
    return wt


def trim(sig, thr=0.006):
    idx = np.where(np.abs(sig) > thr)[0]
    if len(idx) == 0:
        return sig
    a = max(0, idx[0] - int(0.02 * SR))
    b = min(len(sig), idx[-1] + int(0.06 * SR))
    return sig[a:b]


def main(part):
    data = json.load(open("scripts.json"))[part]
    k = Kokoro(f"{TTS}/kokoro.onnx", f"{TTS}/voices.bin")
    audio = [np.zeros(int(LEAD_IN * SR), dtype=np.float32)]
    t = LEAD_IN
    timeline = {"title": data["title"], "badge": data["badge"], "scenes": []}
    for sc in data["scenes"]:
        s_start = t
        lines_out = []
        for li, line in enumerate(sc["lines"]):
            l_start = t
            words_out = []
            sents = split_sentences(line)
            for si, sent in enumerate(sents):
                spoken = sent.replace("J. Gordon", "Jay Gordon")
                sig, sr = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-us")
                assert sr == SR
                sig = trim(sig.astype(np.float32))
                dur = len(sig) / SR
                words = sent.split()
                ws = np.array([word_weight(w) for w in words])
                # distribute words over voiced time only, so internal pauses fall between words
                win = int(0.03 * SR)
                env = np.convolve(np.abs(sig), np.ones(win) / win, "same")
                voiced = (env > 0.004).astype(np.float64)
                cum = np.cumsum(voiced) / SR
                vt = cum[-1]
                edges = np.concatenate([[0], np.cumsum(ws)]) / ws.sum() * vt
                for wi, w in enumerate(words):
                    st = np.searchsorted(cum, edges[wi], side="right") / SR if wi else 0.0
                    en = np.searchsorted(cum, edges[wi + 1], side="left") / SR
                    words_out.append({"w": w, "s": round(t + min(st, dur), 3), "e": round(t + min(en, dur), 3)})
                audio.append(sig)
                t += dur
                gap = GAP_SENT if si < len(sents) - 1 else 0
                if gap:
                    audio.append(np.zeros(int(gap * SR), dtype=np.float32)); t += gap
            lines_out.append({"text": line, "s": round(l_start, 3), "e": round(t, 3), "words": words_out})
            if li < len(sc["lines"]) - 1:
                audio.append(np.zeros(int(GAP_LINE * SR), dtype=np.float32)); t += GAP_LINE
        audio.append(np.zeros(int(GAP_SCENE * SR), dtype=np.float32)); t += GAP_SCENE
        timeline["scenes"].append({"id": sc["id"], "s": round(s_start, 3), "e": round(t, 3), "lines": lines_out})
    voice = np.concatenate(audio)
    sf.write(f"out/{part}_voice.wav", voice, SR)
    timeline["duration"] = round(t, 3)
    json.dump(timeline, open(f"out/{part}_timeline.json", "w"), indent=1)
    print(part, "duration", round(t, 2))
    for s in timeline["scenes"]:
        print(f"  {s['id']:10s} {s['s']:6.2f}-{s['e']:6.2f}  ({s['e']-s['s']:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
