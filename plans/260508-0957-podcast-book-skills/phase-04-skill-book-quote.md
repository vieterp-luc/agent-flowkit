# Phase 4: /fk-video-book-quote Skill (Shorts TikTok/Reels)

**Priority:** P1
**Status:** ⏳ Pending
**Estimate:** 1-2 ngày
**Depends on:** Phase 1 ✅, Phase 2 ✅
**Parallel-safe with Phase 3:** ✅

## Context Links

- Plan overview: [`plan.md`](plan.md)
- Reference skill: `skills/fk-video-khkd.md` (Shorts pattern, VERTICAL)
- Phase 1: Quote script writer
- Phase 2: Ken Burns + bold typography overlay

## Mục tiêu

Skill orchestrator: tên sách → 3 video Shorts 30-60s với quote + insight.

**Usage:**
```
/fk-video-book-quote "<tên sách>" [--source pdf:/path/to/book.pdf]
                                  [--source manual:"outline text"]
                                  [--count 3]
```

→ 1 lần chạy ra **3 Shorts** (3 quote khác nhau từ cùng 1 sách).

## Pipeline

```
1. Extract quote scripts (Phase 1 API)
   POST /api/book/extract-script {format: "quote", count: 3}
   → 3 quote objects
   ↓
2. Loop từng quote object:
   ↓
3. Create FlowKit project mini (per quote)
   /fk-create-project (VERTICAL 9:16, material: realistic)
   - 3-4 scenes (hook, insight, cta)
   ↓
4. Generate scene images
   /fk-gen-images
   ↓
5. Apply Ken Burns + BOLD typography
   POST /api/ken-burns/clip với text_overlay style "quote_centered"
   - Scene 0: full quote text overlay (3-5s)
   - Scene 1-2: insight visual + keywords overlay
   - Scene 3: CTA "Sách [tên] - [tác giả]"
   ↓
6. Generate TTS
   - Hong_Hanh_podcast_TTS, speed 0.95 (Shorts pace nhanh hơn)
   - 1 file duy nhất (full quote + insight + cta)
   ↓
7. Generate music (Gemini Lyria, 1 track Pro 2-3 min)
   - Trim 60s đoạn climax/drop
   ↓
8. Concat + mix
   - Scenes Ken Burns (cuts ngắn 5-15s mỗi scene)
   - Mix narrator (vol 1.5) + music (vol 0.30) — Shorts cần nhạc hơn
   - Add hook flash effect 0-2s
   ↓
9. Caption + branding
   /fk-gen-caption (TikTok/Reels)
   /fk-brand-logo (corner watermark)
```

## Configuration chuẩn

| Tham số | Giá trị |
|---------|---------|
| Resolution | 1080x1920 (VERTICAL) |
| Material | `realistic` |
| Số scenes | 3-4 |
| Duration tổng | 30-60s |
| Scene duration | Hook 3-5s, Body 15-30s, CTA 5-10s |
| TTS voice | `Hong_Hanh_podcast_TTS` |
| TTS speed | 0.95 |
| Narrator volume | 1.5x |
| Music volume | 0.30x (Shorts nhạc to hơn) |
| Text overlay | BOLD typography, white + black stroke 4px |
| FPS | 30 |
| Codec | h264, yuv420p, aac 192k |

## Cấu trúc Quote script (output Phase 1)

```
Quote (3-5s scene)
  └─ Quote nguyên văn từ sách (text overlay BIG)

Insight (15-30s, 2-3 scenes)
  └─ Lý giải insight + ví dụ

CTA (5-10s, 1 scene)
  └─ "Sách [tên] - [tác giả]. Follow để đọc thêm"
```

## Text Overlay Strategy

| Scene | Text style | Position | Animation |
|-------|-----------|----------|-----------|
| Hook | `quote_centered` (BIG bold) | Center | Fade in |
| Body 1-2 | `bold_caption` keyword | Bottom-third | Slide up |
| CTA | `bold_caption` book name | Center | Fade in |

**Font:** Bundle Inter Bold hoặc Roboto Bold (free, Latin extended)

## Image Prompt Template (English)

```
[Subject conveying quote theme] in [evocative setting].
Cinematic vertical composition, 9:16 portrait frame.
[Mood: powerful / contemplative / dramatic].
Soft cinematic lighting, depth of field, 4K, hyperrealistic photography.
Negative: subtitles, watermark, text, logos.
```

## Implementation Steps

1. **Read patterns** (`fk-video-khkd.md` for Shorts vertical pattern)
2. **Draft skill file** `skills/fk-video-book-quote.md`
3. **Create slash command** `.claude/commands/fk-video-book-quote.md`
4. **Loop wrapper logic:**
   - Extract `count=3` quotes
   - Loop: create project → gen → render
   - Output 3 separate videos (named `quote_01`, `quote_02`, `quote_03`)
5. **Music optimization:**
   - Gen 1 track Gemini Lyria, reuse cho cả 3 quote (cùng vibe sách)
   - Mỗi quote dùng 60s offset khác nhau từ track gốc
6. **Test với 1 sách** (Phase 5)

## Music Prompt Template (Gemini Lyria)

```
SHORTS BGM (Pro mode, 1 track reuse cho 3 quote):
"epic emotional cinematic, building tension into climax, motivational,
modern hip-hop beats with orchestral strings, viral TikTok energy,
60-second peak structure"
```

## Todo List

- [ ] Read fk-video-khkd Shorts pattern
- [ ] Draft `skills/fk-video-book-quote.md`
- [ ] Create slash command file
- [ ] Define Gemini system prompt cho quote extraction
- [ ] Define image prompt template (vertical)
- [ ] Document FFmpeg concat with text overlay
- [ ] Implement loop wrapper (3 quotes per run)
- [ ] Bundle bold font (Inter/Roboto)
- [ ] Manual test với 1 sách → 3 Shorts

## Success Criteria

- ✅ Skill output 3 Shorts riêng từ 1 sách
- ✅ Output 1080x1920, 30fps
- ✅ Quote text BIG readable, không bị crop bởi UI TikTok/Reels
- ✅ Hook 0-3s đủ thu hút (text + music drop)
- ✅ Mỗi Short có CTA rõ ràng (tên sách + tác giả)
- ✅ TTS sync với cuts video

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Quote dài quá → text overlay tràn frame | Auto wrap + scale font theo length |
| 3 Shorts giống nhau (cùng music) | Đa dạng image prompts + motion presets |
| TikTok safe zone bị che bởi UI | Padding bottom 250px, top 200px (avoid UI overlay) |
| Quote bị hallucinate (không có trong sách) | Cite page number, manual review trước khi render |

## Safe Zone Reference (Shorts UI overlay)

```
1080x1920 frame:
  Top 200px:    Avatar + Follow button
  Bottom 350px: Caption + Like/Comment/Share buttons
  Right 150px:  Action sidebar
  → Center safe zone: ~780x1370 (place hero text/quote here)
```

## Next Steps

→ Phase 5: E2E test
→ Future: A/B test hooks, analytics integration
