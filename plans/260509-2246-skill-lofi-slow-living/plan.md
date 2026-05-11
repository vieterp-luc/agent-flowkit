# Plan: `/fk-video-lofi` — Lo-Fi Slow Living Channel Skill

> **Brand**: Soft Atelier — không gian yên tĩnh, slow living, study/focus/me-time.

## Goal

Skill mới `/fk-video-lofi` để sản xuất video lo-fi long-form (30min / 1h / 3h) cho YouTube channel kiểu Soft Atelier. Pipeline tự động: chọn preset → generate music + ambience + visual → concat → final mp4 + YouTube metadata.

## Pipeline Overview

```
Preset (Morning Tea / Night Focus / Vintage Cafe / Sunday Reset / Cozy Evening)
   ↓
[Audio Layer]                          [Visual Layer]
  Gemini Lyria Pro (3min) loop N×       Flow image (Ghibli/Vintage style)
  + Ambience .wav (vinyl/rain/cafe)     + ffmpeg ken-burns slow zoom
  Mix: music 75% / ambience 25%         OR Veo loop 5-8s × N
   ↓                                     ↓
              ffmpeg concat → final 1080p mp4
                          ↓
              YouTube SEO metadata (title/desc/tags)
```

## Phases

| # | File | Status |
|---|------|--------|
| 1 | [phase-01-design.md](phase-01-design.md) | Decisions matrix + preset schema |
| 2 | [phase-02-implement.md](phase-02-implement.md) | Skill markdown + audio/visual helpers |
| 3 | [phase-03-test.md](phase-03-test.md) | Produce 1 sample 30min video, validate |

## Reuse (existing endpoints)

| Need | Reuse | Notes |
|------|-------|-------|
| Music gen | `POST /api/gemini/browser/generate-music` (Pro) | 3min instrumental, free with AI Plus |
| Image gen | `POST /api/projects/{pid}/generate-thumbnail` or scene gen | Static cinematic image |
| Loop video | Veo `POST /api/scenes/{sid}/generate-video` | 5-8s × N (optional, expensive) |
| Concat | ffmpeg | already in workflow |
| YouTube SEO | `/fk-youtube-seo` skill | reuse |

## Key Decisions (open — see phase-01)

1. **Default duration**: 30min / 1h / 3h?
2. **Visual mode**: static image + ken-burns (cheap) vs Veo loop (dynamic)?
3. **Ambience source**: bundled .wav library (one-time) vs generate per request?
4. **Music repetition**: same 3min track loop 20× (1h) vs concat 4 different tracks?
5. **Naming**: `/fk-video-lofi` vs `/fk-lofi-slowliving`?

## Critical Files to Modify/Create

| File | Action |
|------|--------|
| `skills/fk-video-lofi.md` | NEW — main skill markdown |
| `agent/services/lofi_pipeline.py` | NEW — orchestrator service |
| `agent/api/lofi.py` | NEW — `POST /api/lofi/generate` endpoint |
| `agent/main.py` | EDIT — register router |
| `assets/ambience/*.wav` | NEW — bundled ambience clips |
| `scripts/lofi_bootstrap_ambience.py` | NEW — download or generate ambience library |

## Success Criteria

- [ ] Single command `/fk-video-lofi --preset "Night Focus" --duration 60` produces final mp4
- [ ] Audio: lo-fi music loop + ambience layer mixed correctly (75/25)
- [ ] Visual: cinematic image + gentle motion (no jarring loops)
- [ ] Final video uploadable to YouTube (1080p, AAC audio, h264)
- [ ] YouTube title/description/tags auto-generated per preset
- [ ] Total wall time < 5 min for 1h video on AI Plus + Flow
