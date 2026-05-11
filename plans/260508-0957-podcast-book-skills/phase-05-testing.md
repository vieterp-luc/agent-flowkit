# Phase 5: E2E Test với sách đầu tiên

**Priority:** P1
**Status:** ⏳ Pending
**Estimate:** 1 ngày
**Depends on:** Phase 1, 2, 3, 4 ✅

## Context Links

- Plan overview: [`plan.md`](plan.md)

## Mục tiêu

Validate full pipeline với 1 sách thật. Chỉnh sửa prompts/parameters dựa trên output thực tế.

## Test Plan

### Sách test đề xuất

| Option | Lý do |
|--------|-------|
| **Đắc Nhân Tâm** (Dale Carnegie) | Self-help phổ biến, có nhiều quote nổi tiếng, dễ visual |
| **Nhà Giả Kim** (Paulo Coelho) | Story-telling, visual phong phú |
| **Tony Buổi Sáng** | Vietnamese native, văn phong gần gũi |
| **Cà Phê Cùng Tony** | Tương tự, audience trẻ |

→ **User chọn** trước khi chạy.

### Output target

1. **1 long-form 7 phút** (`/fk-video-book-summary`)
   - 1920x1080, h264
   - Narrator: Phap_Van_podcast_TTS
   - Music: 3 tracks Gemini Lyria
   - Branding: logo + caption

2. **3 Shorts 30-60s** (`/fk-video-book-quote`)
   - 1080x1920 mỗi video
   - Narrator: Hong_Hanh_podcast_TTS
   - Music: 1 track reuse 3 lần
   - Text overlay BOLD readable

## Validation Checklist

### Audio quality

- [ ] Narrator volume = 1.5x, không clip (peak < -3dB)
- [ ] Music volume = 0.20-0.30x, không lấn voice
- [ ] Mean volume mix = -16 đến -10 dB (LUFS chuẩn YouTube/TikTok)
- [ ] Không có dead air > 2s
- [ ] TTS không bị cắt cuối câu

### Visual quality

- [ ] Resolution chính xác (1920x1080 hoặc 1080x1920)
- [ ] FPS = 30 stable
- [ ] Ken Burns smooth, không jitter
- [ ] Crossfade mượt giữa scenes
- [ ] Text overlay readable, không bị tràn
- [ ] Image gen đúng tone sách (không hallucinate)

### Sync

- [ ] Narrator sync với cuts (không lệch > 0.3s)
- [ ] Music intro/outro crossfade đúng vị trí
- [ ] Total duration khớp target (±5s cho long-form, ±2s cho Shorts)

### Content quality

- [ ] Narrator text 20-22 từ/câu (Vietnamese rule)
- [ ] Hook 0-15s đủ thu hút
- [ ] CTA rõ ràng cuối video
- [ ] Quote chính xác từ sách (không hallucinate)
- [ ] Không vi phạm safe zone Shorts (UI overlay không che text)

### Technical

- [ ] File size hợp lý (long-form < 200MB, Shorts < 30MB)
- [ ] Codec compatible (h264 + aac)
- [ ] Faststart enabled (`-movflags +faststart`)
- [ ] Metadata title/author đúng

## Test Steps

1. **Chọn sách** (user input)

2. **Run long-form**
   ```bash
   /fk-video-book-summary "Đắc Nhân Tâm" --target-minutes 7
   ```
   - Time the run, record cost (Gemini API + Imagen + Lyria credits)

3. **Run Shorts (3 quotes)**
   ```bash
   /fk-video-book-quote "Đắc Nhân Tâm" --count 3
   ```

4. **Manual review** (use `/fk-review-video` if applicable)
   - Watch full long-form
   - Watch 3 Shorts
   - Note issues theo checklist

5. **Iterate** (nếu có lỗi)
   - Fix prompt templates
   - Adjust FFmpeg params
   - Re-run failed segments only (cache scenes)

## Metrics to record

| Metric | Long-form | Shorts (×3) |
|--------|-----------|-------------|
| Tổng thời gian render | ~? phút | ~? phút |
| Gemini API cost | ~$? | ~$? |
| Imagen credits | ~? | ~? |
| Lyria browser gen time | ~? phút | ~? phút |
| Output file size | ~? MB | ~? MB |
| User satisfaction (1-10) | ? | ? |

## Iteration Log

```
Iteration 1: [date]
  Issue: ...
  Fix: ...

Iteration 2: [date]
  Issue: ...
  Fix: ...
```

## Todo List

- [ ] Chốt sách test với user
- [ ] Run long-form full pipeline
- [ ] Run Shorts pipeline (3 quotes)
- [ ] Validation checklist (audio + visual + sync + content)
- [ ] Record metrics
- [ ] Document issues + fixes
- [ ] Update prompt templates dựa trên kết quả
- [ ] Final review với user → approve hay iterate

## Success Criteria

- ✅ Toàn bộ pipeline chạy không lỗi từ command đầu tới video cuối
- ✅ Long-form video pass tất cả validation checklist
- ✅ Ít nhất 2/3 Shorts đạt chất lượng publish-ready
- ✅ User approve output → ready để scale production

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Output không đạt chất lượng | Iterate prompts; document gotchas; fallback voice/music |
| API quota hit khi test | Stagger requests; chia test thành 2 ngày |
| Lyria browser hang | Test với `headless: false` để debug |
| User không hài lòng tone | Allow custom system prompt override |

## Next Steps (sau khi pass)

- Update `docs/development-roadmap.md` với 2 skill mới
- Update `CLAUDE.md` skills table
- Tạo journal entry trong `docs/journal/` về pipeline learnings
- Train batch 5-10 sách đầu để test scale
- Collect view metrics sau khi publish → feedback loop vào prompts
