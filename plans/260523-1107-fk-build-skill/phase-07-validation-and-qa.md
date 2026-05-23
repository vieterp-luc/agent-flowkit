# Phase 7 — Validation, QA Checklist, Smoke Test

## Context Links
- Parent: `plan.md`, depends on Phases 1-6
- Memory: `feedback-flow-quota-safety`, `feedback-flow-image-gen-per-chapter`

## Overview
Define the smoke test and acceptance criteria for the v1 skill. One pass per subject (or one per available test image) ensures the LOCK BLOCK pattern survived translation from build-* into the unified `fk-build` skill.

## Smoke Test Matrix
Pick 1 image per subject (5 minimum) + 2-3 object subtypes for coverage:

| # | Test image | Subject | Subtype | Expected slug | Expected duration |
|---|-----------|---------|---------|---------------|-------------------|
| 1 | sample images/villa.jpg | house | — | house_modern_villa_001 | ~30s |
| 2 | sample images/zen-garden.jpg | garden | — | garden_zen_pond_001 | ~30s |
| 3 | sample images/scandi-living.jpg | room | — | room_scandi_living_001 | ~30s |
| 4 | sample images/condo-tower.jpg | building | — | building_modern_tower_001 | ~30s |
| 5 | sample images/cake.jpg | object | food | object_food_cake_001 | ~30s |
| 6 | sample images/lego-castle.jpg | object | model | object_model_lego_001 | ~30s |
| 7 | sample images/oak-chair.jpg | object | furniture | object_furniture_chair_001 | ~30s |

(User provides the images; skill should still pass on any of the 7.)

## Acceptance Checklist (per test)

### Inputs
- [ ] Input image exists and is readable
- [ ] Server `:8100/health` returns `extension_connected: true`
- [ ] `gemini` CLI authenticated (`gemini status` no errors)
- [ ] Channel icon exists at `youtube/channels/<channel>/<channel>_icon.png`

### Phase A — Vision
- [ ] `analysis.json` written with correct subject
- [ ] LAYOUT MAP block has ≥ 5 zones, each with position + orientation
- [ ] INVENTORY block lists every distinct visible component/plant/material
- [ ] Stage 0 archetype matches subject + feels DRAMATIC vs final

### Phase B — Stages
- [ ] N+1 stage files exist (stage_00..stage_N)
- [ ] stage_00 is the wasteland/raw-materials state (no overlap with final's finished features)
- [ ] stage_<N> is byte-equal to source.jpg
- [ ] All stages 1080×1920 (or auto-cropped to ratio)
- [ ] Camera angle identical across all stages (manual eyeball, OR auto: imagemagick `compare` perceptual diff > threshold ONLY at content regions)
- [ ] No species/material/component drift between adjacent stages

### Phase C — Veo clips
- [ ] N clips exist (clip_00..clip_<N-1>)
- [ ] Each clip 1080×1920, ~8s
- [ ] No mid-clip camera motion (eyeball)
- [ ] Veo "V" watermark present at bottom-right (will be covered in Phase D)

### Phase D — Assembly
- [ ] `final.mp4` exists, duration ≈ N × 8s − (N−1) × 0.5s
- [ ] `music/track.mp3` exists (or `--no-music` skipped cleanly)
- [ ] `final_with_music.mp4` audio not silent (`volumedetect` mean_volume between -28 and -10 dB)
- [ ] `final_branded.mp4` exists, Veo watermark covered by brand logo
- [ ] `README.md` written with subject + slug + paths + flags

### End-to-end
- [ ] Total wall-clock ≤ 25 min for N=4 happy path
- [ ] No QUOTA error halts the pipeline (probe pattern caught it cleanly if hit)
- [ ] `--resume` on a partial run skips completed phases

## Common Error Table (verify each is documented in skill)

| Error | Where | Skill resume hint |
|-------|-------|---------|
| `extension_connected: false` | Pre-flight | `/fk-doctor` then re-run |
| `LOGIN_EXPIRED` (Gemini) | Phase B / D | `venv/bin/python scripts/gemini_bootstrap.py` |
| `QUOTA_REACHED` (Gemini) | Phase B / D | wait or fall back to Suno for music |
| `QUOTA`-like (Flow / Veo) | Phase C | wait + `--resume` |
| reCAPTCHA | Phase B/C | sequential pattern should prevent; if hit, run probe alone |
| `MUSIC_TIMEOUT` | Phase D | retry with `headless: false` for debug |
| Channel icon missing | Phase D | place icon at `youtube/channels/<channel>/` |
| Input image wrong ratio | Phase A | warn + auto-crop center-9:16, or user provides 9:16 |
| Stage drift (species swap) | Phase B | regenerate Stage k with stronger INVENTORY block + explicit "DO NOT change identity at position X" |
| Camera moves mid-clip | Phase C | regenerate clip with stronger "locked tripod" Veo prompt |
| Chain boundary gap > 0.7s | Phase D | increase tail-trim from 0.5s to 0.7s |

## Implementation Steps
1. Prep 7 sample images under `sample images/fk_build/`.
2. Run `/fk-build` once per image with all defaults.
3. Tick the checklist for each run.
4. For any failure, capture the prompt + output and tune the relevant Phase 2-5 template.
5. Re-run until 6/7 pass cleanly (expect 1-2 retries on Veo/quota randomness).
6. Document any newly discovered failure modes in the skill's Common Errors section.

## Todo List
- [ ] Gather 7 sample images
- [ ] Run smoke test #1 (house)
- [ ] Run #2 (garden)
- [ ] Run #3 (room)
- [ ] Run #4 (building)
- [ ] Run #5 (object/food)
- [ ] Run #6 (object/model)
- [ ] Run #7 (object/furniture)
- [ ] Tune templates from any failures
- [ ] Update Common Errors table in skill from real-world findings

## Success Criteria
- ≥ 6 of 7 smoke tests pass the full checklist on first attempt.
- All 7 pass after at most 1 retry per scene.
- Each `final_branded.mp4` looks coherent: same camera throughout, dramatic before→after arc, no obvious species/component drift.
- Total credits per run logged ≤ N × Veo + N × Gemini-edit + 1 × Lyria.

## Risk Assessment
- Risk: object subtypes have higher AI-realism artifacts than wide outdoor shots (close-up macro is unforgiving). Mitigation: defensive prompt at end "photorealistic, ultra-detailed, no artifacts, sharp focus"; document in Common Errors.
- Risk: Veo refuses VERTICAL for some prompts. Mitigation: orientation set on Flow project + video; if Veo still horizontal-defaults, retry with explicit "vertical 9:16 portrait" in prompt.

## Security Considerations
- Test images may contain personal/PII content — keep test set local, gitignored.

## Next Steps
- Once v1 passes smoke test → announce skill to user, add to README, optionally ship a 30s demo video.
