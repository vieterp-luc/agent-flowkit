# fk-reup — Reup Video với Narrator AI + TTS

Pipeline tự động: scene detection → AI tự gen narrator text từng scene → TTS → mix với audio gốc → concat.

Usage: `/fk-reup <video_path> [tts_template] [speed]`

Examples:
```
/fk-reup /Users/vieterp/Downloads/clip.mp4
/fk-reup /Users/vieterp/Downloads/clip.mp4 Anh_Khoi_TTS
/fk-reup /Users/vieterp/Downloads/clip.mp4 Minh_Quan_TTS 0.95
```

---

## Default settings

| Tham số | Default | Note |
|---------|---------|------|
| `tts_template` | `Anh_Khoi_TTS` | Liệt kê qua `GET /api/tts/templates` |
| `speed` | `auto` (1.0) | Min 0.5, max 2.0 |
| `language` | `vi` | Vietnamese |
| `min_scene_duration` | `5.0s` | Scene ngắn hơn sẽ bị merge |
| `sfx_volume` | `0.10` | 10% audio gốc — giảm còn nền nhẹ |
| TTS volume | `1.5` | 150% (cố định trong service) |

**Auto speed:** Nếu user không truyền speed, service dùng 1.0. Có thể adjust bằng cách quan sát video duration / scene count nếu cần.

---

## Bước 1: Verify video file

```bash
ls "<video_path>"
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "<video_path>"
```

Nếu video không tồn tại → ABORT.

## Bước 2: List TTS templates (nếu chưa rõ)

```bash
curl -s http://127.0.0.1:8100/api/tts/templates | python3 -m json.tool
```

Available templates (Vietnamese):
- `Anh_Khoi_TTS` — male, balanced
- `Minh_Quan_TTS` — male, fast/punchy
- `Manh_Dung_TTS` — male
- `Hai_KC_TTS` — male
- `Ngoc_Huyen_TTS` — female
- `Nguyen_Ngoc_Ngan_TTS` — male, narrator style

## Bước 3: Submit Reup job

```bash
curl -X POST http://127.0.0.1:8100/api/reup/jobs \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF
{
  "video_path": "<absolute_path>",
  "tts_template": "<template_name>",
  "speed": <speed>,
  "language": "vi",
  "min_scene_duration": 5.0,
  "sfx_volume": 0.10
}
EOF
```

Response trả về `job_id` (12-char hex).

**JSON encoding cho path có ký tự đặc biệt (`[`, `]`, dấu cách):** dùng Python subprocess + `json.dumps()` + `--data-binary @-`. Không truyền trực tiếp qua shell.

## Bước 4: Poll status

```bash
curl -s http://127.0.0.1:8100/api/reup/jobs/<job_id>
```

Status flow:
```
pending → processing (detecting_scenes → generating_narrator → generating_tts → concat) → completed
```

Poll mỗi 30s. Mỗi scene mất ~25-35s (Claude narrator gen + TTS). Video 5 phút thường có 60-80 scenes → tổng thời gian ~30-45 phút.

## Bước 5: Verify output

```bash
OUT="output/_reup/<job_id>/output.mp4"
ffprobe -v quiet -show_entries stream=width,height -of csv=p=0 "$OUT"
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUT"
ffmpeg -t 10 -i "$OUT" -af "volumedetect" -f null /dev/null 2>&1 | grep mean_volume
```

`mean_volume` nên từ -30 đến -10 dB.

---

## Output structure

```
output/_reup/<job_id>/
├── clips/        # mỗi scene đã trim + mix TTS
├── tts/          # WAV per scene
├── concat.txt    # ffmpeg concat list
└── output.mp4    # final video
```

---

## Pipeline chi tiết (run nội bộ)

1. **Scene detection** — ffmpeg `select='gt(scene,0.4)',showinfo` → cắt theo PTS, merge scenes ngắn hơn `min_scene_duration`
2. **Frame extraction** — lấy frame giữa mỗi scene → base64 JPEG
3. **Narrator gen** — Claude Haiku 4.5 nhận tất cả frames + scene metadata, trả về JSON array narrator texts (max 20 từ/scene cho VN)
4. **TTS gen** — per-scene qua `/api/tts/generate` với `ref_audio` + `ref_text` từ template
5. **Mix per scene** — ffmpeg single pass: trim, normalize size, mix `[bg(SFX) + fg(TTS)] amix duration=first`
6. **Concat** — `ffmpeg -f concat -c copy` → output.mp4

---

## Common issues

| Issue | Fix |
|-------|-----|
| Job stuck ở `generating_tts` | Check Claude CLI hoạt động: `which claude` |
| Output mean_volume = -inf | Audio mất — kiểm tra source video có audio track không |
| `Video not found` | Dùng absolute path, escape ký tự đặc biệt qua Python json.dumps |
| TTS template not found | List templates trước, copy đúng tên (case-sensitive) |
| SFX quá to | Default đã 0.10 (10%), giảm thêm nếu cần |
| Mỗi scene quá ngắn | Tăng `min_scene_duration` lên 7-10s |

---

## Tips

- **Video clip dài >10 phút:** chia nhỏ trước khi reup để tránh job lâu
- **Audio gốc quan trọng:** giữ `sfx_volume` 0.15-0.20 để vẫn nghe được dialogue gốc
- **Chỉ muốn narrator thuần:** set `sfx_volume=0.0`
- **Speed auto recommendation:** Anh_Khoi 0.95, Minh_Quan 0.9
