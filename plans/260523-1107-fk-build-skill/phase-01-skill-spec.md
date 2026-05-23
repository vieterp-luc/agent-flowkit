# Phase 1 — Skill Spec (CLI, args, identity, output)

## Context Links
- Parent: `plan.md`
- Inspirations: `/Users/vieterp/code/Research/.claude/skills/build-{house,garden,room,building}/SKILL.md`
- Sibling orchestrators: `skills/fk-video-bible-explainer.md`, `skills/fk-van-vo.md`, `skills/fk-podcast-book.md`

## Overview
Define the public API of the new `fk-build` skill — how the user invokes it, what args it takes, where output lands, and the front-matter / identity table that the skill's SKILL.md file will expose.

## Requirements

### Functional
- Single command: `/fk-build <image_path> [flags]`.
- Accept input image as local path OR URL (URL → download to `/tmp/fk_build_in_<hash>.jpg`).
- Flags:
  - `--stages N` (int, 2-8, default `4`)
  - `--slug SLUG` (override auto-slug)
  - `--output DIR` (override `output/fk_build/`)
  - `--no-music` (skip BGM)
  - `--no-brand` (skip logo overlay)
  - `--channel NAME` (default `lamplit-library`)
  - `--subject {auto,house,garden,room,building,object}` (override auto-classify)
  - `--object-subtype {auto,food,furniture,electronics,sculpture,model,instrument,painting}` (force when subject=object)
  - `--start-state NAME` (override Stage 0 archetype — passed through to subject's reverse rules)
  - `--dry-run` (analyze + print prompts only; do not call Gemini/Veo)
  - `--resume` (skip stages where output already exists)
- Idempotent: re-running with same input + slug reuses cached stage images and clip files.

### Non-functional
- Total wall-clock for N=4 happy path: ~12-18 min (Gemini chained edits + 4 × Veo + concat).
- Quota-safe: probe-first (generate Stage 0 alone, halt on QUOTA error). See `feedback-flow-quota-safety` memory.

## Architecture

### CLI dispatch (inside SKILL.md, prose pseudocode)
```
1. Parse args; resolve image path; abort if file missing or > 10 MB.
2. Compute slug + create output dir: output/fk_build/<slug>/
3. PHASE A: vision-analyze → classify subject + sub-type → build LOCK BLOCKS → write analysis.json
4. PHASE B: Stage image gen
   - Stage 0 (reverse from final via Gemini edit, input = original image)
   - Stage 1..N-1 (Gemini chained, input = Stage k-1 image)
   - Stage N = original input (no gen needed)
   - All saved to output/fk_build/<slug>/stages/stage_<NN>.jpg
5. PHASE C: Veo transition videos (N clips, each first-frame stage_k + last-frame stage_k+1)
   - Submit via /fk-gen-chain-videos pattern; orientation VERTICAL
   - Save to output/fk_build/<slug>/clips/clip_<NN>.mp4
6. PHASE D: Music (Lyria 30s instrumental, prompt from subject)
   - Save to output/fk_build/<slug>/music/track.mp3
7. PHASE E: Concat clips → mix music → brand overlay → final_branded.mp4
8. Print summary + path; warn on common issues.
```

### Identity table (paste into SKILL.md front-matter section)

| Item | Value |
|------|-------|
| Skill ID | `fk-build` |
| Skill file | `skills/fk-build.md` |
| Description | "Universal 1-image → vertical timelapse Short. Auto-classifies subject (house/garden/room/building/object), reverse-engineers N build stages, generates Gemini chained stage images + Veo transition videos, mixes instrumental BGM, brands. Silent timelapse, no narrator." |
| Default N | 4 |
| Orientation | VERTICAL 1080×1920 |
| Default channel | `lamplit-library` |
| Total ~duration | 32-45s (≈ 8s × N stages) |
| Output root | `output/fk_build/<slug>/` |

### Output folder structure
```
output/fk_build/<slug>/
  meta.json                  # subject, subtype, N, source_image_hash, args used
  analysis.json              # LAYOUT MAP + INVENTORY + scene-context (LOCK BLOCKS source-of-truth)
  source.jpg                 # copy of input image (Stage N)
  prompts/
    stage_00_image_prompt.txt
    stage_01_image_prompt.txt
    ...
    transition_00_video_prompt.txt
    ...
  stages/
    stage_00.jpg             # Stage 0 wasteland / raw materials
    stage_01.jpg
    ...
    stage_<N-1>.jpg
    stage_<N>.jpg            # = source.jpg (final)
  clips/
    clip_00.mp4              # 8s: stage_00 → stage_01
    clip_01.mp4
    ...
    clip_<N-1>.mp4           # 8s: stage_<N-1> → stage_<N>
  music/
    track.mp3                # 30s instrumental (or .mp4 from Lyria → transcoded)
  final.mp4                  # concat of N clips
  final_with_music.mp4       # final.mp4 + BGM at 0.18× volume
  final_branded.mp4          # + brand logo overlay (Veo "V" watermark cover)
  README.md                  # quick recap auto-written by skill at end
```

### Slug derivation
```
slug = "<subject>_<subtype-or-style>_<3-digit-counter>"
e.g. "house_modern_villa_001", "garden_zen_pond_001", "object_food_cake_001",
     "object_model_lego_001", "room_scandi_living_001"
```
Counter = next-available integer scanning existing `output/fk_build/<subject>_*/`.

## Related Code Files
- **Create:** `skills/fk-build.md`
- **Create:** plan-derived helper scripts (optional — see Phase 3/4) under `scripts/fk_build_*.py` if pure-bash dispatch becomes unwieldy
- **Modify:** `CLAUDE.md` → add `/fk-build` row to skills table
- **Modify (auto):** `.claude/commands/fk-build.md` (re-generated by `setup.py --tool claude`)
- **No edit:** server / worker / Flow extension (uses existing endpoints)

## Implementation Steps
1. Lock the identity table above into the front-matter of `skills/fk-build.md` (Phase 6 will actually write it).
2. Define args + dispatch order in plain prose (skills are prose-driven, not Python).
3. Decide slug template + counter mechanic — implement as a small `bash + python3 -c` snippet in the skill.
4. Specify `meta.json` keys.
5. Specify return summary format printed at end (project name, output path, duration, resolution, N, total credits used, warnings).

## Todo List
- [ ] Finalize flag list (review with user — see Unresolved Qs)
- [ ] Lock identity table values
- [ ] Lock output folder structure
- [ ] Write slug derivation snippet

## Success Criteria
- Skill spec doc is unambiguous — a fresh agent can read it and dispatch correctly.
- `/fk-build path/to/image.jpg` runs end-to-end with all defaults.
- All flags map cleanly to behavior changes; no flag combination produces undefined behavior.

## Risk Assessment
- Risk: too many flags → user confusion. Mitigation: list only essential flags in skill header; document advanced flags in a separate section.
- Risk: slug collisions when two different houses get same descriptor. Mitigation: 3-digit counter + warn on collision.

## Security Considerations
- Input image path validation (absolute path, file size cap, MIME check) to prevent path traversal or oversized memory loads.
- URL download: HTTPS only, size cap, timeout.

## Next Steps
- Phase 2 (vision analysis) consumes the args + image path defined here.
