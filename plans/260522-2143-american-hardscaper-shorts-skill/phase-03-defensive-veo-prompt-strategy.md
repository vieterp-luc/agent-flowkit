# Phase 03 — Defensive Veo / Imagen Prompt Strategy

## Context Links

- Overview: [plan.md](plan.md)
- Depends on: [phase-02](phase-02-script-and-scene-breakdown.md) (scene shot list)
- Prompt references: `fk-create-project` (Veo 3 formula, safe language), `fk-camera-guide`
- Memory: `feedback-flow-image-orientation-text`, `feedback-flow-quota-safety`

## Overview

- **Priority:** P1
- **Status:** pending
- **Description:** The hardest realism problem — AI-generated hardscaping ACTION
  footage easily looks fake. This phase defines the defensive Imagen prompt
  (start frame) and Veo prompt (motion clip) recipes that mask AI artifacts and
  the Flow quota guardrails for generation.

## Key Insights

- AI fails most visibly at: full-body human motion, tool-material contact physics,
  consistent faces, clean wide shots. It succeeds at: tight close-ups, texture,
  dust/sparks/grit, handheld shake, low light, hands-only / no-face framing.
- Therefore: **frame to AI's strengths.** Close-ups + low angle + handheld +
  partial-body / hands-and-tool shots hide the artifacts the brief warns about.
- `feedback-flow-image-orientation-text`: Flow flakes orientation and bakes text
  — every Imagen prompt MUST force vertical 9:16 + STRICTLY NO TEXT.
- Safe-language table (`fk-create-project`) — "cut/blade/grind" risk filter hits;
  use neutral framing ("masonry blade scoring", "tool passing over surface").

## Requirements

### Functional

- An Imagen prompt recipe (scene start-frame image).
- A Veo prompt recipe (8s motion clip per scene).
- A negative-prompt block applied to every prompt.
- Quota guardrails: pre-flight credits, probe-first, halt-on-quota-error.

### Non-functional

- Every prompt English, 100-150 words for Veo, single continuous shot.
- No real brand names, no people's faces as focal point.

## Architecture

### Artifact-masking framing rules (apply to ALL scenes)

| Rule | Why |
|------|-----|
| Tight close-up or medium-close — tool + material + hands only | AI nails texture, fails full bodies |
| Low-angle camera (near ground) | gritty Hardscaper look + hides background AI errors |
| Handheld / slight shake described | reads as real jobsite footage, not rendered |
| Faces never the focal point; worker shown from behind / cropped at torso / gloved hands | avoids face-drift hallucination (`fk-create-project` face rule) |
| Heavy environmental texture: dust, sparks, grit, wet concrete sheen | distracts the eye, sells realism |
| "Dying light" / harsh low side-light | the brand look AND forgiving on AI artifacts |
| Real jobsite clutter (gravel piles, tool bags) — never staged-clean | brief: "never staged-clean" |

### Imagen start-frame prompt recipe

```
Photoreal RAW jobsite photograph, shot on a gritty handheld camera.
[Close-up | low-angle] of [tool + material + gloved hands] [KB-correct action moment]
at a real residential hardscaping jobsite. [Texture: dust / sparks / wet sheen].
Harsh low-angle late-afternoon side light, long shadows, gritty realistic tones.
VERTICAL PORTRAIT 9:16 framing.
Negative: text, letters, captions, watermark, logo, full body, distant wide shot,
clean studio, cartoon, smooth CGI look, extra fingers.
```

- Mandatory tail per `feedback-flow-image-orientation-text`:
  `VERTICAL PORTRAIT 9:16` + `STRICTLY NO TEXT, NO LETTERS, NO WORDS`.

### Veo motion prompt recipe (per scene, 100-150 words)

```
[Close-up / low-angle] of [tool + gloved hands] [KB-correct action] at a real
hardscaping jobsite. [2-3 sentences of the core 8s action — one continuous motion:
e.g. masonry blade scoring a paver then completing the cut, sparks arcing].
The camera holds low and handheld with a slight organic shake, pushing in slightly.
Harsh low side-light, long shadows, airborne dust catching the light, gritty
realistic color. Real jobsite grit — gravel, tool bags, dust.

Audio: jobsite ambient, wind, distant machinery hum.
SFX: [scene-specific — see Phase 04 SFX layer; Veo native audio is a fallback only].
Negative: subtitles, watermark, text overlay, full-body wide shot, clean studio,
smooth CGI, morphing hands, extra fingers.
```

- Single continuous shot, no "cut to". Map action to 0-2s establish / 2-5s core /
  5-8s peak (`fk-create-project` emotional arc).
- **Safe language:** avoid "cutting through", "grinding", "smashing" → use
  "masonry blade scoring", "blade passing through the paver", "compactor passing
  over the base", "seating the stone". Keeps the UNSAFE_GENERATION filter calm.
- CTA scene (finished result): wider is OK here — a tiered patio glowing in sun
  is a static-friendly hero shot AI handles well; slow push-in or slow pan.

### Per-area Veo cue bank (the skill ships this table)

| Area | Veo action phrasing (realism-safe + KB-correct) |
|------|--------------------------------------------------|
| Paver Cutting | "masonry blade scoring a clean line across the paver, fine sparks arcing, dust drifting" |
| Retaining Wall | "gloved hands seating a heavy wall block onto the level course, tapping it true" |
| Base compaction | "plate compactor passing over the gravel base, dust kicked up in the low light" |
| Polymeric Sand | "stiff broom sweeping fine sand deep into the paver joints, joints filling" |
| Self-reliance | "a lone worker, seen from behind, adjusting a heavy machine, leaning into the effort" |
| CTA payoff | "slow reveal of the finished tiered patio glowing in warm sunlight, clean joint lines" |

### Quota guardrails (MANDATORY — from `feedback-flow-quota-safety`)

1. **Pre-flight:** `GET /api/flow/credits` AND check recent FAILED requests for
   `PER_MODEL_DAILY_QUOTA_REACHED` (the `credits` number alone is not trustworthy).
2. **Images:** generate in 1-2 small waves, never mass-batch (reCAPTCHA risk per
   `feedback-flow-image-gen-per-chapter`). 6-9 images is small — single batch OK
   only if probe passes; otherwise split.
3. **Videos — probe-first:** submit ONLY scene 0; poll; if COMPLETED → batch the
   rest. If FAILED → halt.
4. **Halt-on-quota-error:** on `QUOTA_REACHED | no operations | MODEL_ACCESS_DENIED |
   UNSAFE_GENERATION ×3`, PATCH all PENDING/PROCESSING requests `status=FAILED,
   retry_count=5` to stop the 5× worker auto-retry burn, then `/fk-doctor`.
5. Note for the user: ~20 credits/clip on TIER_ONE → 6-9 clips ≈ 120-180 credits.

## Related Code Files

- All recipes are documented IN `skills/fk-video-hardscaper.md` (Phase 05).
- READ: `fk-create-project.md`, `fk-camera-guide.md`, `fk-gen-videos.md`.
- No standalone code.

## Implementation Steps

1. Write the artifact-masking framing rules table into the skill.
2. Write the Imagen recipe + mandatory vertical/no-text tail.
3. Write the Veo recipe + emotional-arc note + safe-language note.
4. Write the per-area Veo cue bank table.
5. Write the quota-guardrail block (pre-flight, probe, halt, credit estimate).
6. Cross-link to Phase 04 for which SFX accompany which cue.

## Todo List

- [ ] Framing rules table written
- [ ] Imagen recipe written (with vertical + no-text tail)
- [ ] Veo recipe written (with safe-language guidance)
- [ ] Per-area cue bank table written
- [ ] Quota-guardrail block written
- [ ] UNSAFE_GENERATION escalation note added

## Success Criteria

- Every scene prompt produced by the recipe is close-up/low-angle/handheld and
  carries the no-text + vertical guards.
- A test clip from the recipe reads as plausible jobsite footage, not obvious CGI.
- No GENERATE_VIDEO batch is ever submitted without a passing probe.

## Risk Assessment

- **Risk:** AI footage still looks fake. **Mitigation:** close-up-only framing +
  `/fk-review-video` checkpoint before concat; regen weak scenes individually.
- **Risk:** silent quota burn. **Mitigation:** probe-first + halt-on-quota-error.
- **Risk:** UNSAFE_GENERATION on "cut/blade". **Mitigation:** safe-language table;
  escalate per-scene (rephrase → strip → retry).

## Security Considerations

- No real people, no real brand logos, no copyrighted designs in prompts.

## Next Steps

- Phase 04 pairs each cue with SFX and sets beat-synced durations.
