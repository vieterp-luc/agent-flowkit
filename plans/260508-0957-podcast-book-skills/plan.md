# Plan: Podcast Book Skills

**Date:** 2026-05-08
**Status:** Planning → Ready to implement
**Owner:** Sang

## Mục tiêu

Tạo 2 skill FlowKit cho video podcast đọc sách, sử dụng **Phương án A: Still Image + Ken Burns** (cost ~$0/video):

| Skill | Format | Platform | Voice | Length |
|-------|--------|----------|-------|--------|
| `/fk-video-book-summary` | Tóm tắt sách | YouTube long-form | Phap_Van_podcast_TTS (nam) | 5-8 phút |
| `/fk-video-book-quote` | Quote + Insight | TikTok/Reels Shorts | Hong_Hanh_podcast_TTS (nữ) | 30-60s |

## Stack

| Component | Tool | Cost |
|-----------|------|------|
| Source → Outline | Gemini API (PDF/EPUB extract) hoặc input thủ công | ~$0.01 |
| Script writer | Gemini API | ~$0.01 |
| Image gen | Imagen via Google Flow | $0 |
| Visual effects | FFmpeg Ken Burns helper (local) | $0 |
| Music BGM | Gemini Lyria via `/fk-gen-music` | $0 |
| TTS | Templates đã có | $0 |
| Concat + mix | FFmpeg | $0 |
| **Total/video** | | **~$0.02** |

## Phases

| # | Phase | File | Status |
|---|-------|------|--------|
| 1 | Source extraction (PDF/EPUB → Outline → Script) | [phase-01-source-extraction.md](phase-01-source-extraction.md) | ⏳ Pending |
| 2 | Ken Burns FFmpeg helper (reusable) | [phase-02-ken-burns-helper.md](phase-02-ken-burns-helper.md) | ⏳ Pending |
| 3 | `/fk-video-book-summary` skill (long-form) | [phase-03-skill-book-summary.md](phase-03-skill-book-summary.md) | ⏳ Pending |
| 4 | `/fk-video-book-quote` skill (Shorts) | [phase-04-skill-book-quote.md](phase-04-skill-book-quote.md) | ⏳ Pending |
| 5 | E2E test với sách đầu tiên | [phase-05-testing.md](phase-05-testing.md) | ⏳ Pending |

## Dependencies

- ✅ FlowKit GLA server (`http://127.0.0.1:8100`)
- ✅ Google Flow + AI Plus (image gen + Gemini Lyria)
- ✅ TTS templates: `Phap_Van_podcast_TTS`, `Hong_Hanh_podcast_TTS`
- ✅ FFmpeg installed locally
- ⚠️ Cần thêm: `pypdf` hoặc `pdfplumber` cho PDF extract; `ebooklib` cho EPUB

## Decisions chốt

1. **Visual style**: 100% Ken Burns (no Veo3, no img2vid)
2. **Voice mapping**: Phap_Van (long-form), Hong_Hanh (Shorts)
3. **Music**: Gemini Lyria duy nhất (không Suno)
4. **Script source**: Hỗ trợ cả PDF/EPUB extract VÀ input thủ công (tên sách + outline)
5. **Pipeline**: Auto end-to-end nhưng có checkpoint review giữa các step lớn

## Câu hỏi chưa giải đáp

- Sách đầu tiên test? (cần để validate prompt template)
- Tên kênh + branding (logo intro/outro)?
- Có cần thumbnail tự động cho YouTube long-form không? (tận dụng `/fk-thumbnail`)

## Liên kết

- Reports: [`reports/`](reports/)
- Research: [`research/`](research/)
- Visuals: [`visuals/`](visuals/)
