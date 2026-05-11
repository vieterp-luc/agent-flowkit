# Phase 01 — Design: Decisions + Preset Schema

## Context Links
- Brand brief: user message ngày 2026-05-09
- Existing music endpoint: `agent/api/gemini.py` → `POST /api/gemini/browser/generate-music`
- Existing image endpoint: `agent/api/projects.py` → `_build_thumbnail_prompt()` (vừa fix bug burn-in text)
- Reference skill: `skills/fk-video-khkd.md` (cấu trúc preset-based)

## Decisions Matrix

### D1 — Video duration

| Option | Pros | Cons | Recommend |
|--------|------|------|-----------|
| 30min default | Nhanh, ít loop noticeable | Hơi ngắn cho study session | 🥈 |
| 1h default | Đúng study/focus session, sweet spot | Cần loop nhạc 20× | ✅ |
| 3h default | Sleep/work full session | Loop quá nhiều, file ~500MB | 🥉 (param) |

→ **Recommend**: default 1h, expose `--duration {30,60,180}` (minutes)

### D2 — Visual mode

| Option | Cost | Look | Recommend |
|--------|------|------|-----------|
| Static image + ken-burns slow zoom | $0 (1 Flow gen) | Pro lo-fi standard | ✅ |
| Veo 5-8s loop × N | ~$0.05/clip × N | Animated, dynamic | Optional flag |
| Multi-image slideshow (3-5 images, slow xfade) | $0 (3-5 Flow gens) | Variety | 🥈 |

→ **Recommend**: default "single image + ken-burns" (KISS). Add `--visual {static,slideshow,veo}` flag.

### D3 — Ambience source

| Option | Quality | Effort | Recommend |
|--------|---------|--------|-----------|
| Bundle 5-8 royalty-free .wav (Freesound CC0) | Cao, consistent | One-time download script | ✅ |
| Generate via Suno per-request | Variable | Tốn credits, prompt khó | ❌ |
| Generate via Gemini Lyria | Lyria không tốt cho pure ambience | ❌ |

→ **Recommend**: bundled. Script `lofi_bootstrap_ambience.py` download 1 lần khi setup.

**Files cần (CC0 từ Freesound / pixabay):**
- `vinyl_crackle.wav` (loop 30s, lặp lại = không lộ)
- `rain_light.wav` (loop 60s)
- `coffee_shop.wav` (loop 60s, có người nói nhỏ xa)
- `fireplace.wav` (loop 30s)
- `tea_pour.wav` (one-shot, optional intro)

### D4 — Music repetition strategy

| Option | UX | Cost | Recommend |
|--------|-----|------|-----------|
| 1 track Gemini Pro (3min) loop 20× | Bị nhận ra loop sau 2-3 lần | $0 | 🥉 |
| 4 different Gemini tracks (3min × 4 = 12min), concat + loop 5× | Variety, ít lộ | $0 (4 gen × ~1.5min) | ✅ |
| Suno V4_5 8min × 2 + concat | 16min unique, loop 4× | ~20 credits | 🥈 |

→ **Recommend**: 4 tracks Gemini, concat → 12min unique block, loop để fill duration. Generate parallel nếu Gemini lock cho phép (hiện tại serialize → ~6min cho 4 tracks).

### D5 — Naming

| Option | Pros | Cons |
|--------|------|------|
| `/fk-video-lofi` | Khớp pattern `fk-video-*` | Generic |
| `/fk-lofi-slowliving` | Brand-specific | Dài |
| `/fk-lofi` | Ngắn | Không phân biệt photo/video |

→ **Recommend**: `/fk-video-lofi` (khớp pattern hiện có).

## Preset Schema (JSON)

Lưu tại `assets/lofi-presets.json`:

```json
{
  "morning_tea": {
    "title": "Morning Tea ☕ Soft Lo-Fi for a Peaceful Start",
    "music_prompt": "lo-fi hip hop, soft jazzy piano, organic percussion, 80bpm, fresh morning tea atmosphere, slow living aesthetic, instrumental",
    "ambience": ["coffee_shop", "tea_pour"],
    "ambience_volume": 0.25,
    "music_volume": 0.75,
    "image_prompt": "A sunlit cozy corner, a cup of Matcha tea with steam rising, a small flower vase on a light oak table, gentle morning light, cinematic soft focus, Ghibli style",
    "color_palette": "sage green, warm wood, cream",
    "youtube_tags": ["lofi", "morning", "matcha", "study", "slow living"]
  },
  "night_focus": {
    "title": "Night Focus 🕯️ Cozy Atelier Lo-Fi for Deep Work",
    "music_prompt": "chill lo-fi beats, minimalist rhodes piano, 75bpm, muffled sound, cozy atelier night ambience, focus music, no vocals",
    "ambience": ["rain_light", "vinyl_crackle", "fireplace"],
    "ambience_volume": 0.30,
    "music_volume": 0.70,
    "image_prompt": "A warm artist studio at night, dim candlelight, a tea pot and a book on a wooden desk, rainy window in the background, cozy and serene atmosphere, dark indigo and amber tones, Ghibli style",
    "color_palette": "indigo, amber, candle warm",
    "youtube_tags": ["lofi", "focus", "study", "night", "deep work"]
  },
  "vintage_cafe": {
    "title": "Vintage Tea Corner 🎷 1940s Lo-Fi Jazz",
    "music_prompt": "vintage lo-fi jazz, 1940s nostalgic, dusty vinyl crackle, slow and sentimental, 70bpm, warm and grainy texture, muted saxophone",
    "ambience": ["vinyl_crackle", "coffee_shop"],
    "ambience_volume": 0.30,
    "music_volume": 0.70,
    "image_prompt": "A vintage 1940s tea cafe corner, warm sepia tones, a steaming cup, gramophone in background, dusty sunlight through lace curtains, vintage film grain aesthetic",
    "color_palette": "sepia, brown, cream",
    "youtube_tags": ["lofi jazz", "vintage", "1940s", "cafe", "study"]
  },
  "sunday_reset": {
    "title": "Sunday Reset ✨ Lo-Fi to Recharge Your Week",
    "music_prompt": "uplifting lo-fi, soft acoustic guitar, mellow brushed drums, 78bpm, sunday morning reset, hopeful warm",
    "ambience": ["rain_light", "tea_pour"],
    "ambience_volume": 0.25,
    "music_volume": 0.75,
    "image_prompt": "A peaceful sunday morning bedroom, sunbeams through linen curtains, an open book and a coffee cup, plants on the windowsill, soft pastel light, Ghibli watercolor style",
    "color_palette": "pastel blue, cream, sage",
    "youtube_tags": ["lofi", "sunday", "reset", "weekly", "calm"]
  },
  "cozy_evening": {
    "title": "Cozy Evening 🌙 Lo-Fi for Tea & Quiet Time",
    "music_prompt": "soft lo-fi, double bass, muted trumpet, brushed snare, 72bpm, evening tea ceremony, intimate and warm",
    "ambience": ["fireplace", "vinyl_crackle"],
    "ambience_volume": 0.30,
    "music_volume": 0.70,
    "image_prompt": "A cozy evening living room, warm fireplace glow, a steaming teacup on a wool blanket, a sleeping cat curled up, golden hour amber light, Ghibli aesthetic",
    "color_palette": "amber, deep brown, golden",
    "youtube_tags": ["lofi", "evening", "tea", "cozy", "relax"]
  }
}
```

## Output Naming Convention

```
output/lofi/<preset>_<duration>min_<timestamp>/
├── music/                  # 4 generated tracks
│   ├── track_01.mp4 (Gemini)
│   ├── track_02.mp4
│   └── ...
├── concat_music.mp3        # 4 tracks concat
├── mixed_audio.mp3         # music + ambience mixed
├── visual.png              # main cinematic image
├── ken_burns.mp4           # image → ken-burns video
├── final.mp4               # final long-form video
└── youtube_meta.json       # title, description, tags
```

## Success Criteria for Phase 01

- [x] All 5 decisions documented with rationale
- [x] Preset schema drafted (5 presets)
- [x] Ambience file list defined
- [x] Output structure decided

## Open Questions for User

1. Đồng ý với 5 decisions trên không (D1-D5)?
2. Có channel name ưa thích từ list 5 gợi ý không, hay tự chọn sau?
3. Cần tích hợp upload YouTube luôn (gọi `/fk-youtube-upload`) hay chỉ produce mp4 + metadata?
4. Có muốn preset khác ngoài 5 cái trên không (ví dụ "Library Reading", "Late Night Drive")?
5. Ambience: tự download 1 lần OK, hay muốn skill auto-download lần đầu run?
