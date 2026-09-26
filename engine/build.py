"""Build one video: python engine/build.py <topic-slug> <part1|part2> [--date YYYY-MM-DD] [--preview 2,6,9]

Reads topics/<slug>/scripts.json + topics/<slug>/scenes.py, works in work/<slug>/,
writes videos/<date>_<slug>_<part>.mp4 (or preview frames + a contact sheet with --preview).
"""
import argparse, datetime, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("slug"); ap.add_argument("part")
ap.add_argument("--date", default=datetime.date.today().isoformat())
ap.add_argument("--preview", default=None)
a = ap.parse_args()

topic = os.path.join(ROOT, "topics", a.slug)
work = os.path.join(ROOT, "work", a.slug)
os.makedirs(os.path.join(work, "out"), exist_ok=True)
shutil.copy(os.path.join(topic, "scripts.json"), os.path.join(work, "scripts.json"))
sys.path[:0] = [os.path.join(ROOT, "engine"), topic]
os.chdir(work)
import tts, render, mix, scenes  # noqa: E402

tl_path = f"out/{a.part}_timeline.json"
if not os.path.exists(tl_path) or os.path.getmtime(tl_path) < os.path.getmtime("scripts.json"):
    tts.main(a.part)
if a.preview:
    for f in os.listdir("out"):
        if f.startswith(f"prev_{a.part}_"):
            os.remove(os.path.join("out", f))
    render.main(a.part, [float(x) for x in a.preview.split(",")])
    subprocess.run([sys.executable, os.path.join(ROOT, "engine", "sheet.py"), f"out/prev_{a.part}_*.png",
                    f"out/sheet_{a.part}.png", "5"], check=True)
    print("preview:", os.path.join(work, f"out/sheet_{a.part}.png"))
    sys.exit(0)
render.main(a.part)
tl = json.load(open(tl_path))
mix.main(a.part, getattr(scenes, "hits", lambda p, t: [])(a.part, tl))
os.makedirs(os.path.join(ROOT, "videos"), exist_ok=True)
dst = os.path.join(ROOT, "videos", f"{a.date}_{a.slug}_{a.part}.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"out/{a.part}_video.mp4", "-i", f"out/{a.part}_mix.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst], check=True)
dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                     capture_output=True, text=True).stdout.strip()
print("video:", dst, "duration:", dur)
