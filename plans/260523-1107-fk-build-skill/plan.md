---
title: "fk-build — Universal 1-image → build/restoration timelapse Shorts skill"
description: "FlowKit skill: 1 input image → auto-classify subject (house/garden/room/building/object) → reverse-engineer N stages → Gemini chained edits → Veo first+last frame timelapse clips → silent instrumental Short."
status: pending
priority: P2
effort: 10h
branch: master
tags: [skill, flowkit, fk-build, timelapse, shorts, vertical, gemini, veo, music]
created: 2026-05-23
---

# fk-build — Plan Overview

Universal orchestrator skill that turns 1 input image of a finished subject into a 9:16 vertical "before → finished" timelapse Short (~32-45s) using:
- Auto-classification → {house, garden, room, building, object}
- Reverse-engineered N stages (default 4) with LOCK BLOCKS for continuity
- Gemini chained stage-image editing (Stage 0 reversed from final; Stage k chained from Stage k-1)
- Veo first-frame+last-frame transition videos via `/fk-gen-chain-videos`
- Instrumental music via `/fk-gen-music` (Gemini Lyria default)
- Concat + brand logo via `/fk-concat` + `/fk-brand-logo`
- **Silent timelapse + music + brand. NO narrator/VO.**

Inspired by but supersedes the four `build-*` Anthropic skills (`build-house`, `build-garden`, `build-room`, `build-building`) — see those at `/Users/vieterp/code/Research/.claude/skills/build-*` for the proven LOCK BLOCK / Stage-0-radical / chained-continuity pattern that this skill must reproduce.

## Phases

| # | Phase | File | Status |
|---|-------|------|--------|
| 1 | Skill spec — CLI, args, identity table, output folder | `phase-01-skill-spec.md` | pending |
| 2 | Vision analysis + auto-classification + LOCK BLOCK builder | `phase-02-vision-classify-locks.md` | pending |
| 3 | Stage image gen (Gemini chained-edit, reverse + N-1 chained) | `phase-03-stage-image-gen.md` | pending |
| 4 | Veo transition videos (first-frame+last-frame chain) | `phase-04-veo-transitions.md` | pending |
| 5 | Music + concat + branding | `phase-05-music-concat-brand.md` | pending |
| 6 | Write `skills/fk-build.md` + setup.py regen + CLAUDE.md row | `phase-06-write-skill-and-register.md` | pending |
| 7 | Checklist + validation + smoke test | `phase-07-validation-and-qa.md` | pending |

## Key Design Choices (locked)

- **Image generator = Google Gemini (via existing `gemini` CLI in `ai-multimodal` skill) — NOT Flow Imagen.** Gemini's chained image-edit ("edit this image to add X") is exactly the proven `build-garden` pattern; Flow Imagen does not chain by editing a prior frame.
- **Video generator = Google Flow + Veo via existing `/fk-gen-chain-videos`** (Flow already exposes start+end frame mode; perfect fit).
- **Project orientation = VERTICAL** (1080×1920) hard-coded.
- **Default N = 4** stages → 4 Veo clips × 8s ≈ 32s + small overhead.
- **Music = Gemini Lyria (Nhanh, 30s)** by default — instrumental cinematic build-up. Suno fallback if Lyria unavailable.
- **Subject classification = Claude built-in vision** (already proven in build-house / build-room / build-building). No external multimodal call needed.
- **Object subject = NEW** — designed in phase-02 with OBJECT/COMPONENT INVENTORY LOCK + sub-types (food, furniture, electronics, sculpture/art, model/lego, instrument).
- **Output root = `output/fk_build/<slug>/`** where slug = `<subject>_<descriptor>_<NNN>` auto-derived.

## Dependencies

- FlowKit server `:8100` healthy + extension connected
- `gemini` CLI installed + logged-in (Google AI Plus) for stage image edits + Lyria
- Veo quota available
- Brand logo channel (default `lamplit-library` or user override `--channel`)

## Out of Scope (YAGNI)

- No narrator / TTS
- No YouTube upload (use `/fk-youtube-upload` after)
- No thumbnail gen (use `/fk-thumbnail` separately)
- No multi-camera / multi-angle variants
- No upscale (already 1080×1920 from Veo VERTICAL)
