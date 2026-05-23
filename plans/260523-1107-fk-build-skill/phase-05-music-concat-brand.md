# Phase 5 — Music, Concat, Brand

## Context Links
- Parent: `plan.md`, Phase 4 (consumes `clips/clip_<NN>.mp4` × N)
- Reuse: `skills/fk-gen-music.md` (Path A — Gemini Lyria), `skills/fk-concat.md`, `skills/fk-brand-logo.md`
- Memory: `feedback-music-as-mp3` (transcode Lyria MP4 → MP3)

## Overview
Final assembly: concat the N Veo clips into `final.mp4`, generate (or skip) an instrumental BGM track, mix at 0.18× volume, then apply the channel brand logo overlay to produce `final_branded.mp4`.

## Key Insights
- **NO narrator** — silent timelapse. Audio = (a) clip ambient SFX from Veo + (b) instrumental BGM.
- **Lyria default, Suno fallback.** Lyria "Nhanh" (30s) gives ~32-45s usable track — perfect for our 32-45s video.
- **BGM volume 0.18×** — matches user's brand preference for podcast videos (gentle background, not foreground).
- **Brand logo last** — covers Veo's "V" watermark at bottom-right.

## Requirements

### Functional
- Step A — Concat N clips → `final.mp4` (trim 0.5s off each clip's tail except last, to mitigate known chain-boundary static frames).
- Step B — Generate music (skip if `--no-music`):
  - Lyria "Nhanh" mode, prompt derived from subject
  - Transcode the returned MP4 → MP3 (smaller, audio-only) per `feedback-music-as-mp3`
  - Save to `music/track.mp3`
- Step C — Mix BGM into `final.mp4` → `final_with_music.mp4` (BGM at 0.18× volume; preserve clip SFX at 1.0×; trim/loop BGM to match video duration).
- Step D — Brand (skip if `--no-brand`):
  - Apply `<channel>_icon.png` overlay at bottom-right, size auto from resolution
  - Skip intro/outro (Shorts format — no intro/outro)
  - Output `final_branded.mp4`
- Write `README.md` recap into `output/fk_build/<slug>/`.

### Non-functional
- Total time budget for this phase: ≤ 3 min (concat fast, music ~60s, brand fast).
- All ffmpeg calls use `-preset fast -crf 18` for quality/speed balance.

## Architecture

### Step A — Concat with tail trim
```bash
SRC=output/fk_build/<slug>
N=<num_clips>
> $SRC/clips/concat.txt
for k in $(seq 0 $((N-1))); do
  CLIP=$SRC/clips/clip_$(printf "%02d" $k).mp4
  if [ $k -lt $((N-1)) ]; then
    # All clips except last: trim 0.5s from tail to remove chain static
    DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$CLIP")
    TRIM_DUR=$(python3 -c "print(round(float('$DUR') - 0.5, 2))")
    ffmpeg -y -i "$CLIP" -t $TRIM_DUR -c copy "$SRC/clips/clip_${k}_trim.mp4"
    echo "file 'clip_${k}_trim.mp4'" >> $SRC/clips/concat.txt
  else
    echo "file 'clip_$(printf "%02d" $k).mp4'" >> $SRC/clips/concat.txt
  fi
done
cd $SRC/clips
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy -movflags +faststart ../final.mp4
```

### Step B — Music generation (Lyria default)
Music prompt template (per subject):
```
Slow cinematic instrumental, gentle warm strings + soft piano, building
swell over 30 seconds, satisfying transformation mood, organic and uplifting,
NO drums, NO vocals, NO lyrics, NO percussion. {{subject_specific_color}}
- house/building: industrious + hopeful + accomplished
- garden: organic + earthy + peaceful → blooming joyful
- room: cozy + warm + cinematic reveal
- object/food: playful + appetizing + warm
- object/furniture: artisanal + woody + warm craft
- object/electronics: clean + modern + minimal techno (still no drums)
- object/sculpture: contemplative + classical
- object/painting: dreamy + romantic + impressionistic
- object/model: nostalgic + playful
- object/instrument: warm + craft + melodic
```

```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"<MUSIC_PROMPT>","model":"Nhanh","timeout":120,"headless":true}'
# → {"ok":true,"path":"output/_shared/gemini_music/<file>.mp4", ...}

# Transcode MP4 → MP3 (per feedback-music-as-mp3)
ffmpeg -y -i "<lyria_mp4>" -vn -c:a libmp3lame -q:a 4 \
  output/fk_build/<slug>/music/track.mp3
```

On Lyria failure (`LOGIN_EXPIRED`, `QUOTA_REACHED`, etc.) → fall back to Suno (`fk-gen-music.md` Path B) with the same prompt + `instrumental: true`.

### Step C — Mix BGM
```bash
SRC=output/fk_build/<slug>
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 $SRC/final.mp4)
ffmpeg -y -i $SRC/final.mp4 -i $SRC/music/track.mp3 \
  -filter_complex "[1:a]aloop=loop=-1:size=2e9,atrim=0:$DUR,volume=0.18[bg]; \
                   [0:a]volume=1.0[sfx]; \
                   [sfx][bg]amix=inputs=2:duration=first:dropout_transition=0[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -movflags +faststart \
  $SRC/final_with_music.mp4
```

If `--no-music`: skip Step B + C; rename `final.mp4` → `final_with_music.mp4` (so downstream brand step has consistent input).

### Step D — Brand logo overlay
Reuse `fk-brand-logo.md` Step 6 (logo only — skip intro/outro for Shorts):

```bash
CHANNEL=<channel>
ICON=youtube/channels/${CHANNEL}/${CHANNEL}_icon.png
RES_W=1080  # vertical width
# Map size per phase 5 sub-table:
SIZE=140; PAD=28  # for 1080×1920 vertical

ffmpeg -y -i $SRC/final_with_music.mp4 -i $ICON \
  -filter_complex "[1:v]scale=${SIZE}:${SIZE},format=rgba[icon]; \
                   [0:v][icon]overlay=W-w-${PAD}:H-h-${PAD}" \
  -c:v libx264 -preset fast -crf 18 -r 24 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart \
  $SRC/final_branded.mp4
```

If `--no-brand`: skip Step D; print "Brand skipped — output: final_with_music.mp4".

### Step E — README recap
Write `output/fk_build/<slug>/README.md`:
```
# fk-build · <slug>

- **Subject:** <subject> / <subtype>
- **Stages:** <N>
- **Source image:** source.jpg
- **Final:** final_branded.mp4 (<DUR>s, 1080×1920, vertical)
- **Music:** <track | none>
- **Brand:** <channel | none>
- **Flow project:** <project_id> / video <video_id>
- **Created:** <iso8601>
- **Args used:** <full CLI flags>

## How to re-render
`/fk-build <source.jpg> --slug <slug> --stages <N> [--resume]`
```

## Related Code Files
- **Inside skill:** ffmpeg snippets above + music prompt builder + cleanup
- **Reuse:** Lyria endpoint already in server; brand logo path convention; concat patterns from `fk-concat.md`
- **Output:**
  - `final.mp4`
  - `music/track.mp3`
  - `final_with_music.mp4`
  - `final_branded.mp4`
  - `README.md`

## Implementation Steps
1. Write concat-with-tail-trim snippet.
2. Write music prompt builder (subject-aware) + Lyria call + MP3 transcode.
3. Write Suno fallback path with same prompt + `instrumental: true`.
4. Write BGM mix snippet (loop + trim + 0.18× volume).
5. Write logo-only brand snippet (no intro/outro).
6. Write README recap template.
7. Verify final video: duration, resolution 1080×1920, audio not silent (`volumedetect`).

## Todo List
- [ ] Concat-with-tail-trim
- [ ] Music prompt builder per subject (10 variants)
- [ ] Lyria call + MP3 transcode
- [ ] Suno fallback
- [ ] BGM mix at 0.18×
- [ ] Logo-only brand
- [ ] README recap template
- [ ] Final verify (duration, res, audio)

## Success Criteria
- `final_branded.mp4` exists, plays, has audio, is 1080×1920, duration matches `N × 8s − (N−1) × 0.5s` ≈ 30-44s.
- BGM audible but not overpowering (mean_volume around -22 to -16 dB).
- Brand logo visible at bottom-right covering Veo "V" watermark.
- No static gap > 0.3s at chain boundaries (post-trim).

## Risk Assessment
- Risk: BGM track is shorter than video (Nhanh ~30s vs ~32-44s video). Mitigation: `aloop` filter loops + `atrim` to exact duration.
- Risk: Loud Veo SFX overpowers BGM. Mitigation: BGM at 0.18× and SFX at 1.0× — but if user wants quieter SFX, expose `--bgm-vol 0.3` / `--sfx-vol 0.5` flags in a future iteration (YAGNI v1).
- Risk: Channel icon missing. Mitigation: abort Step D with clear message + skip to `--no-brand` behavior.

## Security Considerations
- None new — all files local under `output/`.

## Next Steps
- Phase 6 writes the actual `skills/fk-build.md` file embedding all of the above as concise prose.
