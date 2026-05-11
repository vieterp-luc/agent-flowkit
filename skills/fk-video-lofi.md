# fk-video-lofi — Tạo Video Lo-Fi Long-Form (Slow Living Channel)

Sản xuất video lo-fi 30min / 1h / 3h cho YouTube channel kiểu "Soft Atelier" — slow living, study, focus, me-time.

Pipeline tự động: `Preset → 4× Gemini Lyria Pro music → concat + loop + mix với ambience → Flow image + ken-burns → final 1080p mp4 + YouTube metadata`.

Usage: `/fk-video-lofi --preset <id> [--duration <min>]`

---

## Prerequisites

```bash
# 1. Agent + Gemini Lyria browser sẵn sàng (xem /fk-gen-music)
curl -s http://127.0.0.1:8100/api/gemini/browser/status
# → {"available":true,"ready":true,...}

# 2. Bootstrap ambience (1 lần đầu, idempotent)
python scripts/lofi_bootstrap_ambience.py
# → 5 .wav files trong assets/ambience/
```

---

## 5 Presets có sẵn

| Preset ID | Vibe | Duration recommend | Ambience |
|-----------|------|--------------------|----------|
| `morning_tea` | Matcha, sunrise piano | 30-60min | coffee_shop, tea_pour |
| `night_focus` | Rhodes, rain, vinyl | 60-180min | rain_light, vinyl_crackle, fireplace |
| `vintage_cafe` | 1940s sax, sepia | 60min | vinyl_crackle, coffee_shop |
| `sunday_reset` | Acoustic guitar, hopeful | 30-60min | rain_light, tea_pour |
| `cozy_evening` | Trumpet, fireplace, golden | 60min | fireplace, vinyl_crackle |

```bash
# List tất cả presets
curl -s http://127.0.0.1:8100/api/lofi/presets | python3 -m json.tool

# Xem detail 1 preset (prompts, colors, tags)
curl -s http://127.0.0.1:8100/api/lofi/presets/night_focus | python3 -m json.tool
```

---

## Quick Generate

```bash
# Default 1h, static visual + ken-burns
curl -X POST http://127.0.0.1:8100/api/lofi/generate \
  -H 'Content-Type: application/json' \
  -d '{"preset":"night_focus","duration_min":60}' \
  --max-time 1800
```

**Response:**
```json
{
  "ok": true,
  "preset": "night_focus",
  "duration_min": 60,
  "final_video_path": "output/lofi/night_focus_60min_<ts>/final.mp4",
  "metadata_path": "output/lofi/night_focus_60min_<ts>/youtube_meta.json",
  "image_path": "output/lofi/night_focus_60min_<ts>/visual.png",
  "breakdown": {
    "music_gen_sec": 380,
    "audio_post_sec": 90,
    "image_gen_sec": 25,
    "kenburns_sec": 180,
    "combine_sec": 30,
    "total_sec": 705
  }
}
```

---

## Output Structure

```
output/lofi/<preset>_<duration>min_<timestamp>/
├── music/
│   ├── track_01.mp4 ~ track_04.mp4   # 4 unique Gemini Lyria tracks
├── concat_music.mp3                   # 4 tracks concat → 12min block
├── looped_music.mp3                   # block lặp đến target duration
├── mixed_audio.mp3                    # music + ambience layer mixed
├── visual.png                         # 1 cinematic image (Flow API)
├── ken_burns.mp4                      # image → ken-burns slow zoom
├── final.mp4                          # ✅ FINAL — upload lên YouTube
└── youtube_meta.json                  # title, description, tags
```

---

## Performance dự kiến

| Duration | Music gen | Audio post | Visual | Total wall |
|----------|-----------|-----------|--------|-----------|
| 30 min | ~6 min | ~1.5 min | ~3 min | ~10-12 min |
| 60 min | ~6 min | ~2 min | ~5 min | ~13-15 min |
| 180 min | ~6 min | ~5 min | ~12 min | ~24-26 min |

(Music gen constant — luôn 4 tracks. Visual + audio post scale theo duration.)

---

## Body params

| Field | Default | Notes |
|-------|---------|-------|
| `preset` | (required) | Một trong 5 IDs ở trên |
| `duration_min` | `60` | 1-480 minutes |
| `visual_mode` | `"static"` | `static` (Phase 2). `slideshow`/`veo` = Phase 3+ |
| `project_id_for_image` | `"lofi-shared"` | PID dùng cho Flow API call (image gen) |

---

## YouTube Upload (sau khi pipeline xong)

```bash
# Đọc metadata + upload
META=$(cat output/lofi/night_focus_60min_<ts>/youtube_meta.json)
TITLE=$(echo "$META" | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")

# Dùng /fk-youtube-upload skill (long-form video, không phải Shorts)
# Set privacy="public" thay vì "private" trước khi upload publishing
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `music_gen_N_failed: LOGIN_EXPIRED` | Gemini session expired | `python scripts/gemini_bootstrap.py` |
| `music_gen_N_failed: MODEL_NOT_AVAILABLE: 'Pro'` | Account không có AI Plus | Upgrade hoặc ghi đè music model trong preset (không khuyến nghị, Nhanh chỉ 30s) |
| `flow_extension_not_connected` | Flow extension offline | Mở Chrome, refresh Flow tab |
| `image_gen_failed` | Flow API quota / 4xx | Retry sau 30s, hoặc check `/health` của extension |
| `Unknown preset 'X'` | Preset ID sai | `curl /api/lofi/presets` để list valid IDs |
| Ambience file thiếu | Chưa bootstrap | `python scripts/lofi_bootstrap_ambience.py` |
| ffmpeg `zoompan` jitter | Duration quá dài | Test với 30min trước, hoặc upgrade ffmpeg |

---

## Tips

- **First generate**: tốn ~3-5s thêm để Gemini browser khởi động lazy
- **Concurrent**: skill auto-serialize qua `asyncio.Lock` của Gemini browser → gọi 2 request song song = chạy tuần tự
- **File size**: 1h@1080p ≈ 500-800MB. 3h ≈ 1.5-2GB. Upload OK lên YouTube
- **Quality check**: nghe thử `mixed_audio.mp3` trước khi accept final.mp4 — đảm bảo music không bị ambience lấn át
- **Loop nhận biết**: với 12min unique block, loop sẽ noticeable sau 24min nếu listener attentive. Cho 1h đa số OK; cho 3h+ nên gen thêm 4 tracks và concat (Phase 3)
- **Image variety**: mỗi generate sinh image khác nhau (Flow non-deterministic). Có thể generate vài lần và pick

---

## Checklist nhanh

```
[ ] Bootstrap ambience: python scripts/lofi_bootstrap_ambience.py
[ ] Verify Gemini ready: curl :8100/api/gemini/browser/status
[ ] Generate: curl POST /api/lofi/generate {preset, duration_min}
[ ] Quality check: mở final.mp4 trong VLC/QuickTime
[ ] (Optional) Upload YouTube với /fk-youtube-upload
```

---

## Customize Preset

Edit `assets/lofi-presets.json`:

- `music_prompt`: dùng vocabulary Suno/Lyria-friendly (instruments, BPM, mood, "instrumental only")
- `ambience`: list of file stems (no `.wav` ext) trong `assets/ambience/`
- `image_prompt`: tham khảo phong cách Ghibli/vintage; có thể test prompt qua `/fk-thumbnail` trước
- `youtube_tags`: 5-7 tags ngắn, low-competition + niche

Sau khi sửa: restart agent (đọc lại JSON mỗi request, không cần restart thực tế — nhưng cẩn thận khi đang có job đang chạy).

---

## Architecture (cho debug)

```
agent/api/lofi.py            FastAPI router (3 endpoints)
agent/services/lofi_pipeline.py   Orchestrator + 7 helper funcs
assets/lofi-presets.json     5 presets schema
assets/ambience/*.wav        5 synth ambience files (CC0-equivalent, ffmpeg-generated)
scripts/lofi_bootstrap_ambience.py   One-shot ambience generator
```
