# Phase 4 — Veo Transition Videos (first-frame + last-frame chain)

## Context Links
- Parent: `plan.md`, Phase 3 (consumes `stages/stage_<NN>.jpg`)
- Direct pattern: `skills/fk-gen-chain-videos.md` (start+end frame Veo via `start_end_frame_2_video`)
- Sibling: `skills/fk-create-project.md` (Flow project creation, orientation VERTICAL)
- Memory: `feedback-flow-quota-safety` (probe first), `feedback-flow-image-gen-per-chapter` (sequential pattern)

## Overview
Use Flow + Veo to generate **N transition videos**, one per consecutive stage pair `(stage_k, stage_k+1)`. Each clip is 8s, vertical 1080×1920, with Stage k as start-frame and Stage k+1 as end-frame, producing seamless concat boundaries (same image at both sides of each cut).

## Key Insights
- FlowKit ALREADY does start+end frame chaining via `/fk-gen-chain-videos`. We REUSE that pattern, not re-invent it. DRY.
- The skill creates a one-off Flow project + video with N scenes (one per transition), uploads N+1 stage images as scene start/end images, then runs `/fk-gen-chain-videos` semantics.
- This Flow project is internal-only (not for a YouTube channel) — it's a render workspace. We delete or archive it after concat. Don't pollute the main project list.

## Requirements

### Functional
- Create ephemeral Flow project (orientation VERTICAL, material `realistic`).
- Create one video inside that project.
- For each k in 0..N-1:
  - Upload `stages/stage_<k>.jpg` → get media_id (via `/fk-upload-image` semantics)
  - Upload `stages/stage_<k+1>.jpg` → get media_id (if not already uploaded — reuse cache)
  - Create scene with:
    - `prompt` (image — unused if scene already has start image set via media_id)
    - `video_prompt` = the Veo transition prompt (see template below)
    - `display_order` = k
    - `chain_type` = "ROOT" for k=0, "CONTINUATION" for k>0
    - `parent_scene_id` = previous scene's id (for k>0)
  - PATCH the scene to set `vertical_image_media_id` = stage_k media_id and `vertical_end_scene_media_id` = stage_k+1 media_id
- Submit all N video gen requests via `/api/requests/batch`.
- Poll batch-status every 30s until done.
- On any failed scene: read failure, halt, emit retry hint (`/fk-doctor`).
- Download all N clips → `output/fk_build/<slug>/clips/clip_<NN>.mp4`.

### Non-functional
- Time budget: ≤ 8 min for N=4 (parallel Veo throttled at 5 concurrent server-side).
- Probe pattern: generate clip_00 FIRST as single-request probe; if QUOTA error → halt before batch of N. (Saves credits on quota days.)

## Architecture

### Step 4.1 — Ephemeral Flow project
```bash
curl -X POST http://127.0.0.1:8100/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fk-build-<slug>",
    "description": "Internal render workspace for fk-build",
    "story": "<subject> build timelapse",
    "material": "realistic",
    "characters": []
  }'
# save PID
```

```bash
curl -X POST http://127.0.0.1:8100/api/videos \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<PID>",
    "title": "<slug>",
    "video_story": "Timelapse build",
    "display_order": 0,
    "orientation": "VERTICAL"
  }'
# save VID
```

### Step 4.2 — Upload stage images
For each stage_<NN>.jpg, call `/fk-upload-image` semantics:
```bash
curl -X POST http://127.0.0.1:8100/api/upload-image \
  -F "file=@stages/stage_NN.jpg"
# response → {media_id: "<uuid>", ...}
# cache in clips/.upload_cache.json
```

### Step 4.3 — Create N scenes + wire chain
```bash
# For k = 0..N-1
curl -X POST http://127.0.0.1:8100/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "<VID>",
    "display_order": <k>,
    "prompt": "Transition stage <k> to stage <k+1> of <subject> build.",
    "video_prompt": "<TRANSITION_VIDEO_PROMPT_FROM_TEMPLATE_BELOW>",
    "transition_prompt": "<SAME_AS_VIDEO_PROMPT>",
    "character_names": [],
    "chain_type": "ROOT|CONTINUATION",
    "parent_scene_id": "<previous_scene_id_or_null>"
  }'
# save SID per k
```

Then PATCH each scene to wire image+end_image:
```bash
curl -X PATCH http://127.0.0.1:8100/api/scenes/<SID_k> \
  -H "Content-Type: application/json" \
  -d '{
    "vertical_image_media_id": "<media_id_of_stage_k>",
    "vertical_end_scene_media_id": "<media_id_of_stage_k+1>",
    "vertical_image_status": "COMPLETED"
  }'
```
(Marking `vertical_image_status: COMPLETED` short-circuits image gen — we already have the image.)

### Step 4.4 — Probe + batch submit
```bash
# Probe first scene only
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -d '{"requests":[{"type":"GENERATE_VIDEO","scene_id":"<SID_0>","project_id":"<PID>","video_id":"<VID>","orientation":"VERTICAL"}]}'
# Poll until done; on QUOTA error → halt + emit resume hint

# If probe OK → submit remaining N-1 scenes in one batch
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -d '{"requests":[<scene_1..N-1>]}'
```

### Step 4.5 — Poll + download
Poll `/api/requests/batch-status?video_id=<VID>&type=GENERATE_VIDEO` every 30s until `done: true`. Then download each scene's `vertical_video_url` → `clips/clip_<NN>.mp4`.

### Veo transition video prompt template (per transition k → k+1)
```
8-second hyper-fast timelapse of {{subject_display}} build, phase {{k+1}} of {{N}}
— progressing from {{milestone_from}} ({{percent_from}}%) to {{milestone_to}}
({{percent_to}}%) completion. Camera locked-off, IDENTICAL framing throughout.

{{LAYOUT_MAP}}    ← verbatim
{{INVENTORY_LOCK}}  ← verbatim

CRITICAL during this 8s timelapse:
- Camera does NOT move (locked tripod, identical to first-frame & last-frame images).
- All zones stay at EXACT positions from LAYOUT MAP.
- All components/plants/materials stay the SAME identity per INVENTORY — only
  build-progress/maturity/finish changes.
- Final frame matches the provided end-frame image EXACTLY (Flow first+last frame mode).

Action progression for this phase ({{milestone_name}}):
- {{phase_specific_actions}}
  · house/building: workers hauling materials, scaffolding rising, walls
    forming brick-by-brick, windows snapping in, roof tiles sliding into place
  · garden: clearing → soil → hardscape → planting → blooming (per phase)
  · room: stripping → painting → flooring → furniture → decor (per phase)
  · object/food (cake): mixing, pouring, baking flash, layering, frosting
    sweeps, piping appearing in fast strokes
  · object/furniture: cutting flash, dry-fit, glue + clamp, sanding, staining
  · object/electronics: components snapping together, screen lighting up
  · object/sculpture: chisel chips flying, form emerging, polishing pass
  · object/painting: brush strokes appearing, layers building, details added
  · object/model: pieces clicking together, walls rising, minifigs placed
  · object/instrument: glue + clamp, strings winding on, polish
- Time-passing cue: subtle sun arc / shadow shift (outdoor) OR window light
  shift (interior) OR daylight cycle (object close-up — slight ambient shift)
- Tiny worker/hand figures visible only in mid-phases (small scale)

Audio: {{phase_specific_audio}} — early phases: rough/construction sounds
(hammers, saws, mixing, scraping); mid phases: assembly sounds (clicks,
snaps, water flowing); final phase: lighter ambient + soft uplifting
cinematic swell, building anticipation. NO dialogue. NO music in the
audio track (BGM added in post).

Style: realistic high-end timelapse, fast-motion but stable LOCKED camera,
cinematic color grade, sharp focus, lush saturation increasing toward final
phase. Vertical 9:16 portrait. STRICTLY NO TEXT, NO TYPOGRAPHY, NO LOGOS.

Negative: subtitles, watermark, text overlay, camera movement, multiple shots,
cut to, dialogue.
```

(Veo 3 auto-generates ambient sound from text; per CLAUDE/skills convention we still want zero dialogue and zero music in-clip — music is added cleanly post in Phase 5.)

### Cleanup
After all clips downloaded successfully:
- Mark the ephemeral Flow project for archival (don't delete — keep for re-runs).
- Print Flow project_id + video_id so user can `/fk-status` or `/fk-monitor` if needed.

## Related Code Files
- **Inside skill:** prose dispatch + the Veo prompt template
- **Reuse:** `/fk-gen-chain-videos` pattern (we mimic its API calls; don't call it directly because we need finer control over upload+PATCH)
- **Reuse:** `/fk-upload-image` for stage image uploads
- **Output:**
  - `clips/clip_<NN>.mp4` × N
  - `clips/.upload_cache.json` (media_id ↔ stage_NN mapping)
  - `clips/flow_project.json` (PID, VID, scene IDs — for resume)

## Implementation Steps
1. Write ephemeral project create + video create snippets (orientation VERTICAL).
2. Write per-stage upload loop with cache.
3. Write per-transition scene create + PATCH (set vertical_image_media_id + vertical_end_scene_media_id + mark image_status COMPLETED).
4. Write probe-first batch submit.
5. Write poll + download loop.
6. Write Veo transition prompt template + per-subject phase action snippets.
7. Write cleanup + resume manifest.

## Todo List
- [ ] Ephemeral project bootstrap snippet
- [ ] Stage upload loop with caching
- [ ] Scene wire-up (PATCH with media_ids + status)
- [ ] Probe-first batch submit
- [ ] Poll + download
- [ ] Veo transition prompt template
- [ ] Per-subject phase-action snippets (8 subject variants)
- [ ] Resume manifest

## Success Criteria
- N clips generated successfully, each 1080×1920 vertical, ~8s.
- Each clip's first frame visually matches `stage_k.jpg`; each clip's last frame visually matches `stage_k+1.jpg` (eyeball check).
- Camera does not pan/zoom mid-clip (locked).
- Concat preview shows clean transitions (subject to known ~0.5-0.7s overlap gap — addressed in Phase 5).

## Risk Assessment
- Risk: Veo introduces camera motion despite "locked" instruction. Mitigation: explicit "locked tripod, identical to first-frame & last-frame" + Negative prompt entry.
- Risk: stage_k+1 end-frame too dissimilar to predicted last-frame → Veo struggles. Mitigation: keep each stage transition ≤ 25% progress jump (default N=4 is fine; N=2 may cause issues — document).
- Risk: Flow rejects vertical Veo for some material configs. Mitigation: pre-flight `curl /health` + orientation VERTICAL explicitly set on video.
- Risk: known concat gap (~0.4-0.7s static at chain boundaries) per `fk-gen-chain-videos.md`. Mitigation: Phase 5 trim 0.5s from clip ends.

## Security Considerations
- Don't expose Flow project_id in the user-facing summary if the user wants privacy. (Out of scope for v1; print it.)

## Next Steps
- Phase 5 concats `clips/clip_<NN>.mp4` × N, mixes music, applies brand logo.
