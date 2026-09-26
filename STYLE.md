# Raw Avenue house style — locked

Every video must look and sound like the Houdini pair. Compare your preview sheet side by side with
`style/reference_part1.png` and `style/reference_part2.png` before building.

## What is fixed in code (never edit)
- `engine/` is frozen: frame layout, paper background, header badge and title, caption font, size,
  position and yellow word highlight, camera push-in, band masks, music bed, whooshes, loudness,
  narrator voice (`am_michael`, speed 1.05) and pacing gaps. Do not change any file in `engine/`.
  If a topic seems to need an engine change, draw it differently in the topic's `scenes.py` instead.
- Colours: only the constants in `engine/draw.py` (PAPER, INK, RED, BLUE, WATER, YEL, GREY, LIGHT,
  WOOD, BRONZE, WHITE). No new colours, no gradients, no photos.
- Fonts: F_MARK (Permanent Marker) for hand-written labels and big words, F_BLACK (Archivo Black) for
  pins, stamps and numbers. Nothing else.

## What each topic's scenes.py must follow
- Characters are `stickman(...)` figures only, line weight default (w=10), scale 0.7–1.25.
  The main historical person gets one small identifying prop drawn with primitives
  (Houdini: hair curls + red bow tie; a Viking: `horns=True`; a king: a simple crown polygon).
- One red accent per frame at most in large areas (a stamp, a curtain, a couch); everything else ink
  on paper.
- Every scene has: one clear drawing, a pinned black label (`pin_label`) for place/date, and, where the
  narration makes a claim or reveal, a red `stamp(...)` or a big marker word.
- Reuse the Houdini building blocks where they fit: `calendar`, `pin_label`, `stamp`, `bubble`,
  `thermometer`, `audience`, `curtains`, `bed`, `window`, `couch`, `fist_burst`, `candle`, `clapper`.
  Build new props from `line`, `rect`, `poly`, `circle`, `ellipse`, `arc` in the same hand-drawn way.
- Split-screen "MOVIE vs REALITY" / "MYTH vs FACT" panels (as in Houdini part 1, scene 4) are the house
  way to show a reversal; use one in every Part 1.
- Shots: wide 1.0 then close 1.35–1.7, cut every 2–3.5 s, hard cuts only.
- Part 1 last scene: big "PART 2" in marker + FOLLOW pin. Part 2 last scene: "NEXT MYTH" pin + the next
  topic's figure + red "?".

## Words
- Header title: the topic in 2–3 uppercase words ("HOUDINI'S DEATH", "VIKING HELMETS").
- Script voice: dry, confident, short sentences, no filler, no emoji, no "guys".
- Hook formulas: anniversary flip, picture flip ("Picture X. Wrong."), quote flip, number flip.
