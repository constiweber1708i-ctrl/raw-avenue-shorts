"""Sound: narration + quiet plucked music bed + whooshes on scene cuts + optional hit thumps."""
import json, subprocess
import numpy as np, soundfile as sf

SR = 48000


def _note(f, dur, amp):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 4.5) * np.minimum(1, t / 0.005)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))


def _hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def main(part, hits=()):
    """Reads out/{part}_timeline.json + out/{part}_voice.wav, writes out/{part}_mix.wav."""
    tl = json.load(open(f"out/{part}_timeline.json"))
    D = tl["duration"] + 1.0
    v, vsr = sf.read(f"out/{part}_voice.wav")
    v = np.interp(np.arange(int(len(v) * SR / vsr)) / SR, np.arange(len(v)) / vsr, v)
    N = int(D * SR)
    voice = np.zeros(N); voice[:len(v)] = v[:N]
    voice *= 0.1 / np.sqrt(np.mean(voice[voice != 0] ** 2))
    rng = np.random.default_rng(3)

    # music bed: Am F C E plucks at 96 bpm with a soft bass
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [52, 56, 59, 64]]
    music = np.zeros(N)
    step = 60 / 96 / 2
    i, t0 = 0, 0.0
    while t0 < D:
        ch = chords[int(t0 // (step * 8)) % 4]
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][i % 8]]
        s = int(t0 * SR); n = _note(_hz(m), 1.2, 0.5)
        music[s:s + len(n)] += n[:N - s]
        if i % 8 == 0:
            tb = np.arange(int(step * 8 * SR)) / SR
            b = 0.35 * np.sin(2 * np.pi * _hz(ch[0] - 12) * tb) * np.minimum(1, tb / 0.2) * np.exp(-tb * 0.4)
            music[s:s + len(b)] += b[:N - s]
        i += 1; t0 += step
    music *= 0.011 / np.sqrt(np.mean(music ** 2))
    fade = np.ones(N)
    fade[-SR:] = np.linspace(1, 0, SR)
    fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
    music *= fade

    sfx = np.zeros(N)

    def whoosh(at, amp=0.05, dur=0.32):
        n = int(dur * SR); tt = np.arange(n) / n
        x = rng.normal(0, 1, n); y = np.zeros(n); a = 0.0
        for k in range(n):
            a += (0.02 + 0.25 * np.sin(np.pi * tt[k])) * (x[k] - a); y[k] = a
        y *= np.sin(np.pi * tt) ** 2
        s = int(max(0, at - dur * 0.6) * SR)
        sfx[s:s + n] += (amp * y / (np.abs(y).max() + 1e-9))[:N - s]

    def thump(at, amp=0.35):
        n = int(0.18 * SR); tt = np.arange(n) / SR
        y = np.sin(2 * np.pi * (140 - 300 * tt) * tt) * np.exp(-tt * 28) + 0.3 * rng.normal(0, 1, n) * np.exp(-tt * 60)
        s = int(at * SR)
        sfx[s:s + n] += (amp * y)[:N - s]

    for sc in tl["scenes"][1:]:
        whoosh(sc["s"])
    for h in hits:
        thump(h)
    mix = voice + music + sfx
    sf.write(f"out/{part}_mix_raw.wav", mix.astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"out/{part}_mix_raw.wav", "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", f"out/{part}_mix.wav"], check=True)
