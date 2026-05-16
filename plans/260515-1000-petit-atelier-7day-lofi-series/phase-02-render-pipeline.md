# Phase 2 — Render Pipeline (per day)

Execution checklist + commands to render each daily video. Refer to [phase-01](phase-01-content-briefs.md) for visual/audio briefs.

## Pre-flight (each day)

```bash
# 1. Health
curl -s http://127.0.0.1:8100/health   # extension_connected: true

# 2. Credits (need ≥ 50 for 1h video gen with safety margin)
curl -s http://127.0.0.1:8100/api/flow/credits

# 3. Verify previous video uploaded successfully (no ghost entries)
./venv/bin/python -c "
import json
h = json.load(open('youtube/channels/petit-atelier/upload_history.json'))
print(f'last upload: {h[-1].get(\"uploaded_at\")} | {h[-1].get(\"title\")[:60]}')
"
```

**ABORT** if credits low, extension disconnected, or previous upload missing on YouTube.

## Daily render workflow

### Step 1 — Create Flow project (1 scene, HORIZONTAL)

```bash
/fk-create-project
# Pass per Day's brief from phase-01:
#   name: "Petit Atelier — <title>"
#   material: realistic
#   orientation: HORIZONTAL
#   scenes: 1
#   entities: atelier_setting (location) + focal_objects (visual_asset)
```

### Step 2 — Generate ref + scene image

```bash
/fk-gen-refs <project_id>           # ~15-30s, ~10 credits
/fk-gen-images <project_id> <vid>   # ~30s, ~5 credits
```

**Quality gate:** preview image. If composition wrong, REGENERATE before video step (cheap re-roll).

### Step 3 — Ken Burns animation (FFmpeg, free)

**Per stock cũ:** Petit Atelier KHÔNG dùng Flow video gen. Static image + ffmpeg pan/zoom = visual loop hour-long. 0 Flow credits.

```bash
OUTDIR=output/lofi/<slug>
TARGET=3600   # 1h = 3600s

# Ken Burns: slow zoom in + subtle pan, 1080p HORIZONTAL
ffmpeg -y -loop 1 -i "$OUTDIR/visual.png" \
  -vf "scale=8000:-2,zoompan=z='min(zoom+0.0003,1.3)':d=${TARGET}*24:s=1920x1080:fps=24" \
  -t $TARGET -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUTDIR/ken_burns.mp4"
```

Output: 1h animated mp4 từ 1 image. Zero quota cost.

### Step 4 — Generate music via Gemini Lyria (FREE with AI Plus)

Per [memory feedback-music-as-mp3](../../../memory/feedback-music-as-mp3.md): transcode MP4 → MP3.

```bash
# Generate 2-3 min Pro track (browser automation, FREE)
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H 'Content-Type: application/json' \
  -d "{
    \"prompt\": \"<music brief from phase-01: genre + BPM + layers + mood>\",
    \"model\": \"Pro\",
    \"timeout\": 300,
    \"headless\": true
  }"
# Output: track_NN.mp4 (~2-3 min, raw Lyria)

# Gen 2-3 tracks for variety, concat
# Transcode all MP4 → MP3:
ffmpeg -y -i track_01.mp4 -vn -c:a libmp3lame -b:a 192k track_01.mp3

# Concat 2-3 tracks
echo "file 'track_01.mp3'\nfile 'track_02.mp3'" > concat_list.txt
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy concat_music.mp3

# Loop to TARGET duration
ffmpeg -y -stream_loop -1 -i concat_music.mp3 -t $TARGET -c copy looped_music.mp3

# Optional: mix subtle ambient layer (rain SFX etc.) — based on brief
```

Cost: **0 Flow credits**. Just AI Plus browser session.

### Step 5 — Compose final video

```bash
# Ken Burns animated visual + looped music = 1h final
ffmpeg -y -i "$OUTDIR/ken_burns.mp4" -i "$OUTDIR/looped_music.mp3" \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -shortest -movflags +faststart \
  "$OUTDIR/final.mp4"

# Verify duration matches target
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUTDIR/final.mp4"
```

### Step 6 — Branding (logo + intro)

```bash
/fk-brand-logo petit-atelier "$OUTDIR/final.mp4"
# Output: final_branded.mp4 with 5s intro + corner logo
```

### Step 7 — Thumbnail

```bash
/fk-thumbnail
# Use scene image from Step 2 as base
# Add handwritten French-style title overlay matching channel covers
```

### Step 8 — Upload

```bash
/fk-youtube-upload petit-atelier "$OUTDIR/final_branded.mp4" \
  --title "<Day title with emoji + duration>" \
  --tags "<from phase-01 SEO tags>" \
  --description "<hook from phase-01>" \
  --thumbnail "$OUTDIR/thumbnail.png" \
  --schedule "2026-05-XX 19:00 ICT"
```

**Verify after upload:**
```bash
./venv/bin/python -c "
from googleapiclient.discovery import build
# ... query channel uploads, confirm latest matches
"
```

## Quota safety (apply every video)

Per [memory feedback-flow-quota-safety](../../../memory/feedback-flow-quota-safety.md):

1. **Pre-flight credits check** (abort if < 50)
2. **Probe-first** — never batch parallel video gens
3. **Halt-on-quota-error** active (MAX_RETRIES=1 set in `agent/config.py`)
4. **No auto-resubmit on entity-not-found for video** (fix in `processor.py:514`)

## Per-day execution checklist

Copy/paste for each day:

```
[ ] Day N — <Title>
[ ] Pre-flight: health + credits + previous upload verified
[ ] /fk-create-project (1 scene HORIZONTAL)
[ ] /fk-gen-refs → review composition
[ ] /fk-gen-images → review composition (this becomes visual.png)
[ ] ffmpeg ken_burns → ken_burns.mp4 (1h animated visual, 0 quota)
[ ] Gemini Lyria → music tracks (2-3 × 2-3min, 0 quota)
[ ] ffmpeg transcode mp4→mp3 + concat + loop to TARGET
[ ] ffmpeg compose final.mp4 (ken_burns + looped_music)
[ ] /fk-brand-logo → final_branded.mp4
[ ] /fk-thumbnail
[ ] /fk-youtube-upload → schedule 19:00 ICT
[ ] Verify on YouTube: video appears, thumbnail correct, scheduled time right
[ ] Update upload_history.json
```

## Folder structure per day

```
output/lofi/<slug>/
  ├── visual.png                 # static image from Flow image gen
  ├── ken_burns.mp4              # animated visual (pan/zoom, 1h, 0 quota)
  ├── music/
  │   ├── track_01.mp4           # raw Lyria output
  │   ├── track_01.mp3           # transcoded
  │   ├── track_02.mp4
  │   └── track_02.mp3
  ├── concat_music.mp3           # 2-3 tracks merged
  ├── looped_music.mp3           # looped to target duration
  ├── final.mp4                  # ken_burns + looped_music
  ├── final_branded.mp4          # + intro + logo (upload this)
  ├── thumbnail.png
  └── meta.json                  # project meta + youtube id after upload
```

## Time budget per day

- Step 1-2 (project + images): ~5 min
- Step 3 (video gen + loop): ~15 min (gen) + 5 min (loop)
- Step 4 (music): ~10 min
- Step 5-7 (compose + brand + thumb): ~5 min
- Step 8 (upload): ~10-20 min depending on file size
- **Total:** ~50-60 min/day

Start each day at **13:00 ICT** to ensure ready by 19:00 with buffer for retry.

## Credit budget (revised — no video gen, only image)

Per video estimate:
- Char ref image (if entity): ~5
- Scene image (single static frame): ~5
- ~~Video gen 8s~~: **0** (Ken Burns ffmpeg replaces this)
- Music gen via Gemini Lyria: **0** (browser, free with AI Plus)
- **Total: ~5-10 Flow credits/video**
- **Week total: ~35-70 credits**

70 credits hiện có → đủ cho cả 7 ngày.

## Recovery if a day fails

If render fails on day N:
1. Don't burn more quota — investigate root cause first via `/fk-doctor`
2. If video gen "no operations" → halt-guardrail caught it, check Flow side
3. **Don't skip the day** — upload yesterday's best performer as backup (or re-upload from existing stock in `output/lofi/`)
4. Resume normal schedule day N+1
