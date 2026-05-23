---
title: "fk-video-hardscaper — American Hardscaper Shorts Producer"
description: "New FlowKit skill: one command → one finished 9:16 hardscaping Short (AI Veo footage, instrumental music, SFX, beat-synced)."
status: pending
priority: P2
effort: 7h
branch: master
tags: [flowkit, skill, shorts, hardscaper, veo, vertical-video]
created: 2026-05-22
---

# fk-video-hardscaper — American Hardscaper Shorts Producer

A new FlowKit skill that produces ONE finished vertical Short (9:16, 30-60s) per
invocation in the "American Hardscaper" style — gritty AI-generated hardscaping
action (paver cutting, retaining walls, polymeric sand) set to driving
instrumental music with synced jobsite SFX and minimal punchy text overlays.

## Scope (LOCKED)

- **Producer only** — one command → one Short. NO channel/dashboard/backlog layer.
- **Footage = AI-generated** via Google Flow (Veo motion clips / Imagen stills). Not real footage editing.
- **Output** = vertical 9:16 Short, 30-60s, for TikTok / Reels / YouTube Shorts.
- Skill name confirmed: `fk-video-hardscaper` → file `skills/fk-video-hardscaper.md`.

## Design Pillars

- **DRY** — reuse `/fk-create-project`, `/fk-gen-images`, `/fk-gen-videos`,
  `/fk-gen-music`, `/fk-gen-text-overlays`, `/fk-concat`, `/fk-brand-logo`,
  `/fk-doctor`. The skill orchestrates; it does not reinvent.
- **KISS** — single MODE B style pipeline (no MODE A dashboard). 6-9 scenes max.
- **Defensive-by-default** — Veo prompts engineered to mask AI artifacts; Flow
  quota guardrails (probe-first, halt-on-quota-error) baked in.

## Phases

| # | Phase | Status | Effort | File |
|---|-------|--------|--------|------|
| 1 | Skill spec — command, args, identity, output structure | pending | 1h | [phase-01](phase-01-skill-spec-and-identity.md) |
| 2 | Script & scene-breakdown logic (Hook/Body/CTA framework) | pending | 1.5h | [phase-02](phase-02-script-and-scene-breakdown.md) |
| 3 | Defensive Veo/Imagen prompt strategy | pending | 1.5h | [phase-03](phase-03-defensive-veo-prompt-strategy.md) |
| 4 | Music + SFX layer + beat-synced concat/mix | pending | 1.5h | [phase-04](phase-04-music-sfx-beat-sync.md) |
| 5 | Write `skills/fk-video-hardscaper.md` + registration | pending | 1h | [phase-05](phase-05-write-skill-file-and-register.md) |
| 6 | Per-video checklist, errors table, smoke test | pending | 0.5h | [phase-06](phase-06-checklist-and-validation.md) |

## End-to-End Pipeline (summary)

```
/fk-video-hardscaper "<topic>"
  → 0  Topic intake + framework lock (Hook 5s / Body 20-40s / CTA 10s)
  → 1  Scene breakdown (6-9 scenes, beat-synced durations)
  → 2  /fk-create-project — VERTICAL, realistic, entities + scenes
  → 3  /fk-gen-images — per-wave, probe-first (defensive Imagen prompts)
  → 4  /fk-gen-videos — probe-first + halt-on-quota (defensive Veo prompts)
  → 5  /fk-gen-music — instrumental-only driving track (NO vocals/lyrics)
  → 6  SFX layer build (saw / hammer / plate compactor library)
  → 7  /fk-gen-text-overlays — 2-4 punchy overlays (NO voiceover)
  → 8  Beat-synced concat + mix (music bed + SFX + overlays)
  → 9  /fk-brand-logo — logo + quality-promise CTA frame
  → done → output/hardscaper/<slug>/<slug>_final.mp4
```

## Key Dependencies

- FlowKit server `:8100` healthy (`/health` → `extension_connected: true`).
- Flow account with image + video gen quota (per-model daily quota, not just `credits`).
- Gemini Lyria browser login bootstrapped (for instrumental music).
- A small reusable jobsite SFX library (saw, hammer, plate compactor, ambient) —
  Phase 4 defines how to source/store it under `output/_shared/sfx/hardscaper/`.

## Unresolved Questions

See end of `plan.md` consumers — full list in **Unresolved Questions** section below.

## Unresolved Questions (for the user)

1. **Channel/branding identity** — `/fk-brand-logo` needs a channel dir under
   `youtube/channels/<name>/` with an icon PNG. Is there an "American Hardscaper"
   channel folder + logo already, or should branding be optional (`--no-brand`)
   default-on until assets exist?
2. **SFX library source** — Phase 4 assumes a small royalty-free SFX set
   (saw / hammer / plate compactor / jobsite ambient) stored at
   `output/_shared/sfx/hardscaper/`. Does the user already have these files, or
   should the skill generate them (Veo native audio extraction / external pack)?
   No FlowKit SFX-gen endpoint exists today.
3. **Text overlay vs zero text** — brief says "minimal punchy text overlays
   instead of voiceover", but project memory `feedback-no-text-overlay-podcast`
   bans overlays on podcast videos. Confirm overlays ARE wanted here (different
   format) — plan assumes YES, 2-4 short bold overlays.
4. **Video model / account tier** — TIER_ONE has no free video model
   (`veo_3_1_i2v_s_fast_portrait` ~20 credits/clip). 6-9 clips ≈ 120-180 credits
   per Short. Confirm the account tier and acceptable per-Short credit budget.
5. **Beat-sync precision** — true frame-accurate beat detection needs the music
   track first. Plan uses a "fixed-BPM grid" approach (generate music at a known
   BPM, cut scenes to bar lengths). Confirm that approximation is acceptable vs
   building an onset-detection step.
6. **Length target** — 30-60s is a wide range. Default assumed = ~45s
   (Hook 5s + Body ~30s + CTA 10s). Confirm or pin a tighter default.
