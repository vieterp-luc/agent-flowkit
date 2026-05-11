# Phase 3: /fk-video-book-summary Skill (Long-form YouTube)

**Priority:** P1
**Status:** ⏳ Pending
**Estimate:** 2 ngày
**Depends on:** Phase 1 ✅, Phase 2 ✅

## Context Links

- Plan overview: [`plan.md`](plan.md)
- Reference skills: `skills/fk-video-vetranh.md`, `skills/fk-video-khkd.md`
- Phase 1: Source extraction → script JSON
- Phase 2: Ken Burns helper

## Mục tiêu

Skill orchestrator end-to-end: tên sách (hoặc PDF) → video YouTube long-form 5-8 phút.

**Usage:**
```
/fk-video-book-summary "<tên sách>" [--source pdf:/path/to/book.pdf]
                                    [--source manual:"outline text"]
                                    [--target-minutes 7]
```

## Pipeline

```
1. Extract script (Phase 1 API)
   POST /api/book/extract-script {format: "summary"}
   ↓
2. Create FlowKit project
   /fk-create-project (HORIZONTAL 16:9, material: realistic)
   - 1 scene per "section" (5-8 sections)
   - Plus hook scene + outro scene
   ↓
3. Generate scene images (Imagen via Flow)
   /fk-gen-images — 1 image/scene (no chain needed)
   ↓
4. Apply Ken Burns to each image (Phase 2 API)
   POST /api/ken-burns/clip — vary motion per scene
   ↓
5. Generate narrator TTS
   - Concat all narrator_text → 1 long file (Phap_Van_podcast_TTS, speed 0.85)
   - Hoặc 1 TTS per section để dễ sync
   ↓
6. Generate music (3 tracks Gemini Lyria)
   - Intro track (cinematic build-up)
   - Body track (calm ambient piano)
   - Outro track (warm uplifting)
   ↓
7. Concat + mix
   - Concat clips Ken Burns với xfade 0.5s
   - Mix narrator (vol 1.5) + music (vol 0.20-0.25)
   - Add intro/outro music crossfade vào body
   ↓
8. Add branding (optional)
   /fk-brand-logo — channel watermark
   ↓
9. Generate caption + thumbnail (optional)
   /fk-gen-caption + /fk-thumbnail
```

## Configuration chuẩn

| Tham số | Giá trị |
|---------|---------|
| Resolution | 1920x1080 (HORIZONTAL) |
| Material | `realistic` |
| Số scenes | 7-10 (1 hook + 5-7 sections + 1 outro) |
| Scene duration | 30-60s (tùy section length) |
| TTS voice | `Phap_Van_podcast_TTS` |
| TTS speed | 0.85 (long-form podcast pace) |
| Narrator volume | 1.5x |
| Music volume | 0.20-0.25x |
| Xfade duration | 0.5s giữa clips |
| FPS | 30 |
| Codec | h264, yuv420p, aac 192k |

## Cấu trúc script (output Phase 1)

```
Hook (15-30s)
  └─ "Bạn có biết, cuốn sách thay đổi cách hàng triệu người tư duy?"

Section 1 (60-90s) — Ý chính 1
  └─ Setup → ví dụ → bài học

Section 2 (60-90s) — Ý chính 2
  └─ Setup → ví dụ → bài học

... (5-7 sections)

Outro (30-45s)
  └─ Tóm tắt + CTA: subscribe, đọc full sách
```

## Skill File Structure

`skills/fk-video-book-summary.md` follow pattern của `fk-video-vetranh.md`:

```
# fk-video-book-summary — Tóm tắt sách (YouTube long-form)

## Tổng quan pipeline
[ASCII diagram]

## Bước 0: Extract script
[curl example]

## Bước 1: Create project
[config table + entity design]

## Bước 2: Gen images
[wave strategy — 1 wave (no chain)]

## Bước 3: Apply Ken Burns
[motion variation strategy]

## Bước 4: Gen TTS narrator
[Phap_Van + speed 0.85]

## Bước 5: Gen music (3 tracks)
[Gemini Lyria prompts cho intro/body/outro]

## Bước 6: Concat + mix
[FFmpeg command]

## Bước 7: Branding + caption
[/fk-brand-logo, /fk-gen-caption]

## Checklist
[ ] step list

## Lỗi thường gặp
[error table]
```

## Implementation Steps

1. **Read existing skill patterns** (`fk-video-vetranh.md`, `fk-video-khkd.md`)
2. **Draft skill file** `skills/fk-video-book-summary.md`
3. **Create slash command** `.claude/commands/fk-video-book-summary.md`
4. **Define narrator script writer prompt** (Gemini system prompt)
   - Tone: contemplative podcast Vietnamese
   - 20-22 từ/câu (rule từ memory)
   - Section transitions phải mượt
5. **Define image prompt template** (English):
   ```
   [Subject related to book theme] in [setting], [composition].
   [Mood: contemplative / inspiring / dramatic].
   [Style: cinematic photography, soft lighting, depth of field].
   16:9 horizontal frame.
   ```
6. **Test với 1 sách** — validate end-to-end (Phase 5)

## Music Prompts Template (Gemini Lyria)

```
INTRO (Pro mode, ~2-3 min):
"cinematic intro music, building anticipation, deep strings + soft piano,
contemplative and slightly dramatic, podcast opener style, no melody peaks"

BODY (Pro mode):
"calm ambient piano, low energy, podcast background, contemplative,
no melody peaks, gentle pads, suitable for narration overlay"

OUTRO (Pro mode):
"warm uplifting piano, hopeful resolution, gentle strings,
emotional but restrained, podcast closer, fade-friendly ending"
```

## Todo List

- [ ] Read fk-video-vetranh + fk-video-khkd patterns
- [ ] Draft `skills/fk-video-book-summary.md`
- [ ] Create slash command file
- [ ] Define Gemini system prompts (narrator + image prompts)
- [ ] Document FFmpeg concat + mix command
- [ ] Add error table (common issues)
- [ ] Add checklist
- [ ] Manual test với 1 sách demo

## Success Criteria

- ✅ Skill file follows existing patterns (vetranh/khkd)
- ✅ Pipeline end-to-end runnable từ 1 command
- ✅ Output video 1920x1080, 30fps, h264, ~7 phút
- ✅ Narrator clear, music không lấn voice
- ✅ Ken Burns motion variation (không lặp 1 motion liên tiếp)

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| TTS dài hơn music tổng | Loop body track hoặc gen thêm 1 track body |
| Image gen quota Flow | Cache images cho retry, batch tốt |
| Narrator monotone trong 7 phút | Vary speed nhẹ giữa sections (0.80 → 0.90) |
| Ken Burns motion lặp | Random rotation từ 8 presets, no consecutive same |

## Next Steps

→ Phase 4 (skill Shorts) có thể chạy parallel
→ Phase 5: E2E test với sách thật
