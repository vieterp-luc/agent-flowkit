# fk-reup-url — Download URL + Reup với Narrator AI + TTS (1-shot)

Pipeline: URL (YT/TikTok/Bilibili/…) → ReClip download → fk-reup (scene + narrator + TTS) → final MP4. Auto cleanup nguồn.

Usage: `/fk-reup-url <video_url> [quality] [tts_template] [speed]`

Examples:
```
/fk-reup-url https://www.bilibili.com/video/BV17BR4BCED6/
/fk-reup-url https://youtu.be/jNQXAC9IVRw 480p
/fk-reup-url https://www.bilibili.com/video/BV17BR4BCED6/ 1080p Anh_Khoi_TTS 0.95
```

---

## Default settings

| Param | Default | Note |
|---|---|---|
| `quality` | `1080p` | Allow `1080p` hoặc `480p` (fallback nếu không có) |
| `tts_template` | `Anh_Khoi_TTS` | Voice narrator |
| `speed` | `1.0` | 0.5–2.0 |
| Cleanup source | **YES** | Xóa file ReClip download sau khi reup xong |

## Services required

- ReClip: `http://127.0.0.1:8899` (Chrome cookies enabled khuyên dùng cho Bilibili HD)
- Flow Kit: `http://127.0.0.1:8100`

---

## Bước 1: Health check

```bash
curl -s http://127.0.0.1:8100/health
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8899/
```

- Flow Kit không up → ABORT, user khởi động Flow Kit extension
- ReClip không up → start:
  ```bash
  cd /Users/vieterp/code/Research/tools/reclip
  RECLIP_COOKIES_BROWSER=chrome RECLIP_DOWNLOAD_TIMEOUT=900 ./reclip.sh
  ```
  (background; wait đến khi `:8899` trả 200)

## Bước 2: Fetch video info + chọn format_id

```bash
curl -s -X POST http://127.0.0.1:8899/api/info \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"<URL>\"}"
```

Response chứa `formats: [{id, label, height}, ...]`. Logic chọn:
- Tìm format với `height == <chosen_height>` (1080 hoặc 480)
- Không có → lấy format `height` cao nhất ≤ chosen
- Vẫn không có → lấy format đầu tiên (highest available)

## Bước 3: Submit download

```bash
curl -s -X POST http://127.0.0.1:8899/api/download \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"<URL>\",\"format\":\"video\",\"format_id\":\"<id>\",\"title\":\"<safe_title>\"}"
```

→ `{"job_id":"<10-hex>"}`

## Bước 4: Poll ReClip job

```bash
until curl -s http://127.0.0.1:8899/api/status/<job_id> | grep -qE '"status":\s*"(done|error)"'; do
  sleep 5
done
```

- `error` → ABORT, hiển thị error message
- `done` → file ở `/Users/vieterp/code/Research/tools/reclip/downloads/<job_id>.mp4`

## Bước 5: Submit fk-reup job

```bash
SRC="/Users/vieterp/code/Research/tools/reclip/downloads/<job_id>.mp4"
curl -s -X POST http://127.0.0.1:8100/api/reup/jobs \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF
{
  "video_path": "$SRC",
  "tts_template": "<tts_template>",
  "speed": <speed>,
  "language": "vi",
  "min_scene_duration": 5.0,
  "sfx_volume": 0.10
}
EOF
```

→ `{"job_id":"<12-hex>"}`

## Bước 6: Poll fk-reup job (lâu — 30-45 phút cho video 5 phút)

```bash
until curl -s http://127.0.0.1:8100/api/reup/jobs/<job_id> | grep -qE '"status":\s*"(completed|failed)"'; do
  sleep 30
done
curl -s http://127.0.0.1:8100/api/reup/jobs/<job_id> | python3 -m json.tool
```

Status: `pending → processing (detecting_scenes → generating_narrator → generating_tts → concat) → completed`

## Bước 7: Cleanup + report

```bash
# Cleanup nguồn
rm -f "/Users/vieterp/code/Research/tools/reclip/downloads/<reclip_job_id>".*

# Verify output
OUT="/Users/vieterp/code/Research/agent-flowkit/output/_reup/<reup_job_id>/output.mp4"
ffprobe -v quiet -show_entries format=duration:stream=width,height -of default=nw=1 "$OUT"
```

Report cho user:
- Source URL + title
- Quality tải về (resolution thực tế)
- Final output path
- Duration + file size

---

## Common issues

| Issue | Fix |
|---|---|
| ReClip `/api/info` báo `login required` | Bật `RECLIP_COOKIES_BROWSER=chrome` (Bilibili VIP/HD cần) |
| ReClip download stuck `Unknown B/s` lâu | Bilibili rate-limit — đợi, đã set timeout 900s |
| Quality 1080p không có | Skill tự fallback xuống 480p; nếu nguồn không có 480p → highest available |
| `Video not found` ở Flow Kit | ReClip path sai (format khác mp4?) — verify ext bằng `ls downloads/<job_id>.*` |
| Reup job stuck `generating_tts` | `/fk-doctor` — thường Claude CLI hoặc TTS service issue |
| Cleanup xóa nhầm file user | Skill chỉ xóa `downloads/<reclip_job_id>.*` (UUID 10-hex), không đụng file khác |

---

## Tips

- Chỉ muốn tải, không reup → dùng ReClip UI: http://127.0.0.1:8899
- Chỉ muốn reup file local có sẵn → dùng `/fk-reup <path>` thẳng
- Video TikTok/YT Shorts thường <60s, narrator gen nhanh (~2-3 phút tổng)
- Bilibili dài 3-5 phút → tổng pipeline ~30-50 phút
- Giữ source file (skip cleanup): mở skill, comment block `rm -f` ở Bước 7
