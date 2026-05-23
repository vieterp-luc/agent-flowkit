# Phase 06 — Per-Video Checklist, Errors Table & Smoke Test

## Context Links

- Overview: [plan.md](plan.md)
- Depends on: [phase-05](phase-05-write-skill-file-and-register.md) (skill file exists)
- Reference: `fk-video-khkd` "Checklist nhanh" + "Lỗi thường gặp" sections

## Overview

- **Priority:** P2
- **Status:** pending
- **Description:** Produce the per-video checklist and common-errors table that
  ship inside the skill, then run one real smoke-test Short to validate the whole
  pipeline end-to-end.

## Key Insights

- Every mature FlowKit skill ends with a quick checklist + an errors table —
  consistency matters (khkd, bible-explainer both have them).
- A smoke test is the only way to catch real failures: quota behavior, AI realism,
  beat-sync feel, audio levels.

## Requirements

### Functional

- A per-video checklist (copy-pasteable, one box per pipeline step).
- A common-errors table (symptom → cause → fix).
- One smoke-test Short produced and inspected.

### Non-functional

- Checklist and errors table embedded in `skills/fk-video-hardscaper.md`.

## Architecture

### Per-video checklist (ships in the skill)

```
[ ] Pre-flight: /health ok, Flow credits + daily-quota ok
[ ] Step 0  Framework lock — Hook 5s / Body / CTA 10s, target length set
[ ] Step 1  Scene breakdown — 1 hook + 4-6 body + 1 cta, KB-correct, bar-aligned
[ ] Step 2  /fk-create-project — VERTICAL, realistic, all ROOT scenes
[ ] Step 3  /fk-gen-images — defensive Imagen prompts, vertical + no-text, probe
[ ] Step 4  /fk-gen-videos — PROBE 1 scene → batch rest; halt-on-quota-error
[ ] Step 4.5 /fk-review-video — regen any scene that looks fake/CGI
[ ] Step 5  /fk-gen-music — instrumental ONLY, no vocals, fixed BPM → MP3
[ ] Step 6  SFX layer — per-scene cues from output/_shared/sfx/hardscaper/
[ ] Step 7  /fk-gen-text-overlays — 2-4 punchy caps overlays, NO voiceover
[ ] Step 8  Concat + mix — hard cuts on downbeats, music+SFX+ambient, burn overlays
[ ] Verify final — 720×1280 24fps, length ±1s, mean_volume -16…-9 dB, no vocals
[ ] Step 9  /fk-brand-logo — logo + quality-promise CTA (skip if --no-brand)
[ ] Output  output/hardscaper/<slug>/<slug>_final.mp4 (+ _branded.mp4)
```

### Common errors table (ships in the skill)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Clip looks obviously CGI / fake | Framing too wide, full body shown | Reframe close-up/low-angle/handheld, regen that scene |
| Hands morph / extra fingers | AI hand hallucination | Crop tighter on tool, add `morphing hands, extra fingers` to negative |
| Image came out landscape | Orientation not forced | Add `VERTICAL PORTRAIT 9:16` to image prompt, regen |
| Text baked into image | No-text guard missing | Add `STRICTLY NO TEXT, NO LETTERS`, regen |
| `UNSAFE_GENERATION` on cut/blade | Filter hit violent-ish word | Rephrase to "masonry blade scoring" / "blade passing through"; escalate per scene |
| `no operations` / `QUOTA_REACHED` | Flow quota exhausted | Halt-on-quota-error, PATCH retries=5, `/fk-doctor`, resume after reset |
| Music has vocals/lyrics | Prompt missing no-vocals prefix | Prefix `instrumental only, no vocals, no lyrics`, regen |
| Cuts feel off-beat | Durations not bar-aligned | Recompute durations as whole bars at the chosen BPM |
| Final video silent / quiet | Veo clip audio kept / mix wrong | Drop clip audio (`-an`), use mixed bed; check amix volumes |
| No SFX audible | SFX library missing/empty | Populate `output/_shared/sfx/hardscaper/`; or accept Veo native audio |
| Final too long/short | Scene durations drift | Trim each clip to its bar-aligned `-t`; re-verify sum |

### Smoke test plan

1. Pick a topic, e.g. `"cut pavers fast"` (`--area paver-cutting`).
2. Run `/fk-video-hardscaper "cut pavers fast"` end-to-end.
3. Inspect: AI realism (no obvious CGI), beat-sync feel, SFX audible, music has
   NO vocals, 2-4 overlays present, duration 30-60s, vertical 720×1280.
4. Log any failure → fix the skill → re-run.
5. Record the result in plan.md status.

## Related Code Files

- MODIFY: `skills/fk-video-hardscaper.md` (append checklist + errors table)
- RUNTIME: `output/hardscaper/cut-pavers-fast/` (smoke-test artifacts)

## Implementation Steps

1. Write the per-video checklist into the skill.
2. Write the common-errors table into the skill.
3. Run the smoke test.
4. Fix any issues surfaced; re-run until a clean Short is produced.
5. Update plan.md phase statuses to completed.

## Todo List

- [ ] Per-video checklist written into skill
- [ ] Common-errors table written into skill
- [ ] Smoke test run end-to-end
- [ ] Issues fixed and re-verified
- [ ] plan.md statuses updated

## Success Criteria

- Skill file contains a checklist + errors table.
- Smoke test yields a 30-60s vertical Short: gritty AI footage, driving
  instrumental (no vocals), synced SFX, 2-4 overlays, hard cuts on beat.

## Risk Assessment

- **Risk:** smoke test blocked by Flow daily quota. **Mitigation:** run when
  quota is fresh (resets ~14:00 ICT); project/scene design costs zero quota so
  Steps 0-2 can be validated anytime.
- **Risk:** realism still weak after regen. **Mitigation:** document it as a
  known limitation; tighten framing rules in Phase 03.

## Security Considerations

- None.

## Next Steps

- Skill is production-ready; user resolves the open questions in plan.md
  (channel branding assets, SFX library source).
