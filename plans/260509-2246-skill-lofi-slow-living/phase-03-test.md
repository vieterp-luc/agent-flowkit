# Phase 03 — Test & Validate

## Goal

Sản xuất 1 video sample 30min với preset `night_focus` để verify pipeline end-to-end. Đo wall time, file size, audio quality, visual smoothness.

## Test Plan

### Smoke Test 1 — Audio sub-pipeline (no visual)

```bash
# Gen 4 tracks với prompt night_focus
for i in 1 2 3 4; do
  curl -sX POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"chill lo-fi beats, minimalist rhodes piano, 75bpm, cozy atelier night, focus, instrumental","model":"Pro"}' \
    > /tmp/track_$i.json
  cat /tmp/track_$i.json | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])"
done

# Concat 4 tracks → 12min block
ffmpeg -f concat -safe 0 -i list.txt -c:a libmp3lame /tmp/block.mp3
ffprobe -v error -show_entries format=duration /tmp/block.mp3
# Expected: ~720s (12 min)

# Loop to 30min (1800s)
ffmpeg -stream_loop -1 -i /tmp/block.mp3 -t 1800 -c copy /tmp/looped.mp3
ffprobe -v error -show_entries format=duration /tmp/looped.mp3
# Expected: 1800s

# Mix với ambience (rain + vinyl + fireplace)
ffmpeg -i /tmp/looped.mp3 \
  -stream_loop -1 -i assets/ambience/rain_light.wav \
  -stream_loop -1 -i assets/ambience/vinyl_crackle.wav \
  -stream_loop -1 -i assets/ambience/fireplace.wav \
  -filter_complex "[0:a]volume=0.7[m];[1:a]volume=0.1[a1];[2:a]volume=0.1[a2];[3:a]volume=0.1[a3];[m][a1][a2][a3]amix=inputs=4:duration=first[out]" \
  -map "[out]" -c:a libmp3lame -b:a 192k /tmp/mixed.mp3
```

**Pass criteria:**
- 4 tracks generate thành công (~6 min total wall)
- Concat block = 12 ± 0.5 min
- Loop = 30 min ± 1s
- Mixed audio: nghe được music chính + ambience subtle (không lấn át)

### Smoke Test 2 — Visual sub-pipeline

```bash
# Generate 1 cinematic image cho night_focus preset
curl -sX POST http://127.0.0.1:8100/api/projects/<dummy_pid>/generate-thumbnail \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"A warm artist studio at night, dim candlelight, a tea pot and a book on a wooden desk, rainy window, dark indigo and amber, Ghibli style","aspect_ratio":"LANDSCAPE","output_filename":"lofi_night.png"}'

# Ken-burns slow zoom 30min
ffmpeg -loop 1 -i lofi_night.png \
  -vf "scale=2400:-1,zoompan=z='min(zoom+0.0003,1.1)':d=54000:s=1920x1080:fps=30" \
  -t 1800 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 23 /tmp/kenburns.mp4
ffprobe -v error -show_entries format=duration /tmp/kenburns.mp4
# Expected: 1800s
```

**Pass criteria:**
- Image gen không có embedded text (sau fix bug burn-in)
- Image 1280x720 hoặc 1920x1080
- Ken-burns video 30min, 1080p, smooth zoom (no stutter)
- File size ~200-400MB

### End-to-End Test 3 — Full pipeline

```bash
curl -sX POST http://127.0.0.1:8100/api/lofi/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "preset": "night_focus",
    "duration_min": 30,
    "visual_mode": "static"
  }' --max-time 1200
```

**Expected output:**
```json
{
  "ok": true,
  "final_video_path": "output/lofi/night_focus_30min_<ts>/final.mp4",
  "metadata_path": "output/lofi/night_focus_30min_<ts>/youtube_meta.json",
  "breakdown": {
    "music_gen_sec": 380,
    "image_gen_sec": 25,
    "ffmpeg_sec": 90,
    "total_sec": 495
  }
}
```

**Pass criteria:**
- Total wall time < 12 min cho 30min video
- Final mp4 mở được trong VLC/QuickTime
- Audio: music + ambience đều nghe rõ
- Visual: ken-burns smooth, image không bị crop xấu
- YouTube metadata JSON đúng format (title, description, tags)

## Validation Checklist

```
[ ] Bootstrap ambience script chạy thành công, 5 .wav files exist
[ ] /api/lofi/presets trả về 5 entries
[ ] Smoke Test 1 (audio) pass — file mixed.mp3 listenable
[ ] Smoke Test 2 (visual) pass — kenburns.mp4 plays smoothly
[ ] End-to-end test pass — final.mp4 30min, listenable, watchable
[ ] File size hợp lý (< 1GB cho 30min)
[ ] No embedded text trong image (bug từ fix trước)
[ ] Skill markdown chạy được khi user gõ /fk-video-lofi
```

## Edge Cases to Test

| Case | Expected behavior |
|------|-------------------|
| Gemini gen #2 fail giữa chừng | Pipeline rollback hoặc retry; không leave partial files |
| User specify duration ngắn (5min) | Skip loop, dùng 1 track raw |
| User specify duration siêu dài (8h = 480min) | Warning về file size, vẫn proceed |
| Ambience file thiếu | Skip gracefully, log warning, music-only mode |
| Preset không tồn tại | 404 với list of valid preset IDs |
| Concurrent /api/lofi/generate calls | Serialize qua lock (Gemini browser đã có lock) |

## Performance Targets

| Duration | Music gen | ffmpeg | Total |
|----------|-----------|--------|-------|
| 30 min | ~6 min | ~2 min | ~8-10 min |
| 60 min | ~6 min | ~3 min | ~10-12 min |
| 180 min | ~6 min | ~6 min | ~14-16 min |

(Music gen constant vì cùng 4 tracks; chỉ ffmpeg encoding scale với duration.)

## Test Output Location

- Sample video: `output/lofi/night_focus_30min_test/final.mp4`
- Metadata: `output/lofi/night_focus_30min_test/youtube_meta.json`
- Test report: `plans/260509-2246-skill-lofi-slow-living/reports/smoke-test-report.md`

## Phase 03 Success Criteria

- [ ] Sample 30min video sản xuất thành công
- [ ] Subjective listen test: "có thể bật làm focus music thật" — pass
- [ ] Subjective watch test: ken-burns không gây mỏi mắt — pass
- [ ] User approve sample → unlock production use
