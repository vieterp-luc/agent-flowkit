# Phase 04 — Music + SFX Layer + Beat-Synced Concat/Mix

## Context Links

- Overview: [plan.md](plan.md)
- Depends on: [phase-02](phase-02-script-and-scene-breakdown.md) (durations),
  [phase-03](phase-03-defensive-veo-prompt-strategy.md) (per-scene cues)
- References: `fk-gen-music`, `fk-concat`, `fk-gen-text-overlays`
- Memory: `feedback-music-as-mp3`

## Overview

- **Priority:** P1
- **Status:** pending
- **Description:** The Hardscaper style is music+SFX driven with NO voiceover.
  This phase defines: instrumental-only music gen (copyright-safe), the jobsite
  SFX layer, the beat-sync approach, and the final concat/mix that ties video +
  music bed + SFX + text overlays into one Short.

## Key Insights

- **Copyright:** the user's source doc references real song lyrics — those must
  NOT be used. Solution: AI instrumental-only track via Gemini Lyria, prompt
  prefixed `instrumental only, no vocals, no lyrics, no singing`.
- AI Veo clips have weak/absent authentic machine audio → a dedicated SFX layer
  (saw, hammer, plate compactor) is required for the video to "hit".
- True frame-accurate beat detection needs the rendered track first. KISS
  alternative: **fixed-BPM grid** — generate music at a known BPM, then make every
  scene duration a whole number of bars. Cuts land on bars without onset analysis.
- `feedback-music-as-mp3`: Gemini Lyria returns MP4 (audio-in-video) — transcode
  to MP3 before use.

## Requirements

### Functional

- Generate ONE driving instrumental track ≥ video length.
- Build a per-scene SFX cue track from a small shared SFX library.
- Choose scene durations on a BPM grid so cuts are beat-aligned.
- Produce text overlays (2-4) via `/fk-gen-text-overlays` consumption format.
- Concat scenes + mix music bed + SFX + burn overlays → `<slug>_final.mp4`.

### Non-functional

- Music: NO vocals/lyrics. SFX: punchy, synced to cuts. No copyrighted audio.
- Final audio mean_volume between −16 and −9 dB (loud, energetic, not clipping).

## Architecture

### Step A — Instrumental music (`/fk-gen-music`, Gemini Lyria)

```
POST /api/gemini/browser/generate-music
prompt: "instrumental only, no vocals, no lyrics, no singing — aggressive driving
         hardscaping construction montage track, heavy distorted bass, pounding
         four-on-the-floor drums, industrial percussion, high energy, 128 BPM,
         relentless, no melody peaks, loopable"
model: "Pro"
```

- Transcode MP4 → `music/driving_bed.mp3` (`-vn -c:a libmp3lame -b:a 192k`).
- **Pick a target BPM up front (default 128).** It is the grid for Step C.
- Trim/loop to video length + 0.5s tail.

### Step B — Jobsite SFX layer

- Shared library at `output/_shared/sfx/hardscaper/`:
  `saw.wav`, `hammer.wav`, `plate_compactor.wav`, `broom_sweep.wav`,
  `jobsite_ambient.wav`. (Sourcing = open Q #2 in plan.md.)
- Per scene, the skill maps the Phase 03 cue → an SFX file:

  | Scene cue | SFX |
  |-----------|-----|
  | Paver Cutting (saw blade) | `saw.wav` |
  | Wall block seating | `hammer.wav` (rubber-mallet taps) |
  | Base compaction | `plate_compactor.wav` |
  | Polymeric sand sweep | `broom_sweep.wav` |
  | Self-reliance / hook | `plate_compactor.wav` or `saw.wav` |
  | CTA payoff | `jobsite_ambient.wav` low, fading out |

- Build `sfx/scene_<idx>.wav` = chosen SFX trimmed to scene duration; place the
  SFX hit ON the scene's first downbeat (start of clip).
- A continuous `jobsite_ambient.wav` runs low (~0.2×) under the whole video for glue.

### Step C — Beat-sync via fixed-BPM grid (KISS, no onset detection)

- At BPM `B`, one beat = `60/B`s; one bar (4/4) = `4·60/B`s.
- At 128 BPM: beat ≈ 0.469s, bar ≈ 1.875s.
- **Rule:** every scene duration = a whole number of bars (or half-bars for the
  fast Body cuts). Example 7-scene / ~45s layout at 128 BPM:

  | Scene | Bars | Duration |
  |-------|------|----------|
  | 0 Hook | ~3 bars | 5.6s |
  | 1-5 Body | 3 bars each | 5.6s ×5 = 28.1s |
  | 6 CTA | ~5.5 bars | 10.3s |
  | Total | | ~44s |

- Because each scene spans whole bars, every hard cut lands on a downbeat — the
  montage feels beat-synced without analyzing the audio.
- Veo clips are ~8s native → trim each to its bar-aligned duration (`-t` / `trim`).
- Faster montage option (`--scenes 9`): use 2-bar (3.75s) Body cuts.
- **Refinement (optional, not default):** if precise sync is wanted, run an
  ffmpeg/librosa onset pass on `driving_bed.mp3` and snap cut points — flagged
  as open Q #5; default ships the grid approach.

### Step D — Text overlays (`/fk-gen-text-overlays`)

- Build `overlays/text_overlays.json` keyed by `display_order`, values =
  `[{text, style}]`. Use bold/`name`-style short caps strings from Phase 02.
- 2-4 scenes only (Hook + CTA + ≤2 Body). NO voiceover — overlays carry the words.

### Step E — Concat + mix (extends `/fk-concat` logic)

1. Download + normalize clips (`/fk-concat` Steps 1-6, VERTICAL 720×1280, 24fps),
   each trimmed to its bar-aligned duration.
2. Hard-cut concat in `display_order` (NO xfade — hard cuts are the style).
3. Mix audio with ffmpeg `amix`:
   - `[music] driving_bed.mp3` volume ~0.9
   - `[sfx]` per-scene SFX track volume ~0.7
   - `[ambient] jobsite_ambient.wav` volume ~0.2
   - drop the raw Veo clip audio (unreliable) — `-an` on video, audio = mixed bed.
4. Burn text overlays during the concat/mix pass (reuse `/fk-concat-fit-narrator`
   Step 6b overlay-burn logic, fed by `text_overlays.json`).
5. Output `output/hardscaper/<slug>/<slug>_final.mp4`.
6. Verify: 720×1280, 24fps, duration = target ±1s, mean_volume −16…−9 dB.

## Related Code Files

- Logic documented in `skills/fk-video-hardscaper.md` (Phase 05).
- READ: `fk-gen-music.md`, `fk-concat.md`, `fk-concat-fit-narrator.md`,
  `fk-gen-text-overlays.md`.
- RUNTIME OUTPUT: `music/driving_bed.mp3`, `sfx/scene_*.wav`,
  `overlays/text_overlays.json`, `<slug>_final.mp4`.
- ASSUMES: `output/_shared/sfx/hardscaper/*.wav` exists (open Q #2).

## Implementation Steps

1. Write the Gemini Lyria instrumental prompt (no-vocals prefix, BPM fixed).
2. Write the MP4→MP3 transcode step.
3. Define the SFX library path + cue→file mapping table.
4. Write the fixed-BPM grid math + the default bar layout table.
5. Define `text_overlays.json` build rules.
6. Write the concat + `amix` + overlay-burn recipe.
7. Write the final verification checks.

## Todo List

- [ ] Instrumental music prompt written (no vocals, fixed BPM)
- [ ] MP4→MP3 transcode step documented
- [ ] SFX library path + cue→file mapping written
- [ ] Fixed-BPM grid math + bar layout table written
- [ ] text_overlays.json build rules written
- [ ] Concat + amix + overlay-burn recipe written
- [ ] Final verification checks written

## Success Criteria

- Final Short has driving instrumental music, NO vocals/lyrics, audible synced
  SFX, 2-4 overlays, hard cuts landing on downbeats.
- mean_volume −16…−9 dB; duration within ±1s of target.

## Risk Assessment

- **Risk:** copyrighted music. **Mitigation:** AI instrumental only, no-vocals
  prompt prefix, verify output has no vocals before mixing.
- **Risk:** no SFX assets available. **Mitigation:** open Q #2 — skill aborts
  with a clear message if `output/_shared/sfx/hardscaper/` is empty, or falls
  back to Veo native audio with a warning.
- **Risk:** cuts feel off-beat. **Mitigation:** bar-aligned durations; optional
  onset-detection refinement documented.
- **Risk:** Gemini Lyria quota. **Mitigation:** `/fk-doctor`; `--no-music` flag.

## Security Considerations

- Verify generated music carries no recognizable copyrighted melody (Lyria is
  generative — low risk, but the no-vocals check is mandatory).

## Next Steps

- Phase 05 folds A-E into the skill file as numbered pipeline steps.
