# Raw Avenue Shorts — daily run instructions

This repo produces and schedules one TikTok video per day for the history myth-busting channel
**Raw Avenue**. Every topic is told in exactly two parts (Part 1 ends on a cliffhanger, Part 2 pays
it off and teases the next topic). Each post is scheduled in Metricool with autoPublish on and goes live automatically.

**Style is locked:** read `STYLE.md` before writing any script or scene, never edit `engine/`, and make
every video match `style/reference_part1.png` and `style/reference_part2.png`.

## The daily run (do these in order)

1. `bash setup.sh` (installs deps, the offline voice model and fonts into `~/.cache/rawavenue`).
2. Open `calendar.json`. Today's entry is the one whose `date` equals today's date in Asia/Dubai.
   - `status` is `scheduled` or `posted` → nothing to do; go to step 11.
   - No entry for today → go to step 11, then stop.
   - `videos/<date>_<slug>_<part>.mp4` already exists → skip to step 8.
3. **Script** (only if `topics/<slug>/scripts.json` is missing). Write both parts at once:
   - Research the myth with web search; open the pages you use. Every date, number and name must be
     supported by a page you opened; contested points are said as contested ("may have", "doctors still
     disagree"). Put the URLs in `topics/<slug>/SOURCES.md`, one line per fact.
   - Format: copy `topics/houdini/scripts.json`. `title` = short uppercase topic, `badge` = `PART 1 OF 2`
     / `PART 2 OF 2`. 6–10 scenes per part, 1–2 lines per scene, one idea per scene.
   - Part 1: 150–175 words, hook spoken in the first 3 s, reveals the myth is false, ends with a concrete
     open question + "Part two ... Follow so you don't miss it."
   - Part 2: 160–210 words, opens "Part two. ...", answers with dates and names, one twist, and the last
     scene teases the **next topic in calendar.json** ("Next, a brand new myth. ... Follow for that one.").
   - Spoken style: dry, confident, short sentences, no filler. Write numbers as words when they are
     spoken ("fifty two"); years may stay as digits.
4. **Scenes** (only if `topics/<slug>/scenes.py` is missing). Write `s_<id>(c, t, L)` and
   `shots_<id>(L, D)` for every scene id, using `engine/draw.py` primitives. Model it on
   `topics/houdini/scenes.py` (start the file with `from draw import *`) and follow `STYLE.md`. Layout rules:
   - World coordinates: 1080 wide; keep drawings between y 430 and y 1140; pin labels at y 440;
     figures stand with hip at y ≈ 1000 (feet at ≈ 1156). Camera centre is usually (540, 790).
   - Shots: a cut every 2–3.5 s; alternate wide (1.0) and close (1.35–1.7) framings; the close
     framings must keep their subject inside the frame.
   - Pop labels/stamps on the word they illustrate using `L` (line start times within the scene).
   - Stick figures only, one red accent, paper background; no real logos, no copyrighted characters.
   - Optional `hits(part, tl)` returns times for impact sounds.
5. **Preview**: `python engine/build.py <slug> <part> --preview t1,t2,...` with one timestamp in every
   scene (read scene times from the printed table). Open `work/<slug>/out/sheet_<part>.png` with Read.
   Also open `style/reference_part1.png` and compare: same paper, line weight, fonts, label style and
   density. Fix text cut off by the header/caption bands, overlaps, empty frames and anything off-style.
   At most 3 rounds.
6. **Build**: `python engine/build.py <slug> <part> --date <date>`. Duration must be ≥ 61 s
   (TikTok rewards need > 1 min); if shorter, add a line to the script and rebuild.
7. **Commit and push**: `git add videos/ topics/<slug>/ calendar.json`, commit
   "Add <date> <slug> <part>", `git push origin main`.
8. Wait until `curl -sI <raw_base><file>` returns 200 (retry for up to 3 minutes).
9. **Schedule** with the Metricool `createScheduledPost` tool:
   - `blogId`: `7099952`; `date`: `<date>T18:00:00+04:00` (if that time has passed, 15 minutes from now).
   - `info` (JSON string):
     ```json
     {"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "",
      "hasNotReadNotes": false, "media": ["<raw_base><file>"], "mediaAltText": [],
      "providers": [{"network": "tiktok"}],
      "publicationDate": {"dateTime": "<date>T18:00:00", "timezone": "Asia/Dubai"},
      "shortener": false, "smartLinkData": {"ids": []}, "text": "<caption>",
      "tiktokData": {"disableComment": false, "disableDuet": false, "disableStitch": false,
        "privacyOption": "PUBLIC_TO_EVERYONE", "commercialContentThirdParty": false,
        "commercialContentOwnBrand": false, "title": "<short title, required>", "autoAddMusic": false,
        "photoCoverIndex": 0, "isAigc": true}}
     ```
   - `tiktokData.title` is required by Metricool: a short title such as "Houdini didn't die in the tank (Part 1)".
   - Caption: line 1 the hook as a claim, line 2 the open question, line 3 "Part 2 on my page" (Part 1)
     or "Part 1 on my page" (Part 2), then 3–5 hashtags: #history #mythbusting #historyfacts plus one
     topic tag. Under 300 characters.
10. Set the entry's `status` to `scheduled`, add `planner_url` and `file`, commit and push.
11. **Keep new ideas coming** (every run, even when today needed nothing):
    - Keep at least 10 `planned` entries after today in `calendar.json`. To add a topic, take the top
      item of `IDEAS.md`, verify its reversal in two independent sources you open, and if it holds,
      append it as a part1/part2 pair on the next free dates at 18:00 and remove it from `IDEAS.md`.
      If it fails, move it to "Dropped" with the reason and try the next idea.
    - When `IDEAS.md` has fewer than 10 ideas, research new history myths that meet its rules and add
      them to the backlog. Never repeat a topic that is already in `topics/` or `calendar.json`.
    - Commit and push `calendar.json` and `IDEAS.md`.

## If something breaks
Never schedule a broken, silent or sub-61-second video. If a step cannot be fixed within the run, set
the entry's `status` to `failed` with a `note`, push, and say so at the top of your final message.
