# fk-sub-url — Download URL + Burn dual subtitle (CN + VN), giữ nguyên độ dài + audio

Pipeline: URL → ReClip download → Whisper transcribe (zh) → Claude translate (zh→vi) → ffmpeg burn dual sub → output MP4. Giữ NGUYÊN audio gốc + độ dài gốc.

Usage: `/fk-sub-url <video_url> [quality] [model]`

Examples:
```
/fk-sub-url https://www.bilibili.com/video/BV1Xk9NBqErg/
/fk-sub-url https://www.bilibili.com/video/BV1Xk9NBqErg/ 480p small
/fk-sub-url https://www.bilibili.com/video/BV1Xk9NBqErg/ 1080p medium
```

---

## Default settings

| Param | Default | Note |
|---|---|---|
| `quality` | `1080p` | `1080p`/`480p`/`360p` (auto-fallback nếu Bilibili VIP locked) |
| `model` | `small` | Whisper: `tiny`/`base`/`small`/`medium`/`large-v3` |
| `src-lang` | `zh` | Source language (Whisper code) — `zh`/`en`/`ja`/`ko` |
| `tgt-lang` | `Vietnamese` | Translation target |
| Cleanup source | **YES** | Xóa file ReClip download sau khi sub xong |

**Model tradeoff** (Whisper):
- `small` — 250MB, ~3-5x realtime CPU, OK cho thoại rõ
- `medium` — 770MB, ~1-2x realtime, **khuyên dùng** cho thoại nhanh/lẫn nhạc
- `large-v3` — 1.5GB, slow trên CPU, accuracy cao nhất

## Services required

- ReClip: `http://127.0.0.1:8899`
- Claude CLI: `claude` binary on PATH (for translation)
- Python: `faster-whisper`, ffmpeg (system)

---

## Bước 1: Health check + deps

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8899/
which claude ffmpeg
python3 -c "import faster_whisper" 2>&1 | head -1
```

- ReClip không up → start:
  ```bash
  cd /Users/vieterp/code/Research/tools/reclip
  RECLIP_COOKIES_BROWSER=chrome RECLIP_DOWNLOAD_TIMEOUT=900 ./reclip.sh
  ```
- faster-whisper thiếu → `pip3 install --break-system-packages faster-whisper`

## Bước 2: Fetch info + chọn format_id

```bash
curl -s -X POST http://127.0.0.1:8899/api/info \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"<URL>\"}"
```

Pick format: tìm `height == <chosen>` (1080/480/360); fallback xuống thấp hơn nếu locked.

## Bước 3: Download

```bash
curl -s -X POST http://127.0.0.1:8899/api/download \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"<URL>\",\"format\":\"video\",\"format_id\":\"<id>\",\"title\":\"<slug>\"}"
```

→ `{job_id}`. Poll:
```bash
until curl -s http://127.0.0.1:8899/api/status/<job_id> | grep -qE '"status":\s*"(done|error)"'; do
  sleep 5
done
```

**Auto-fallback quality**: nếu báo `Requested format is not available`:
- 1080p → retry 720p → 480p → 360p (lấy format có `height` cao nhất còn lại)

Source path khi `done`: `/Users/vieterp/code/Research/tools/reclip/downloads/<job_id>.mp4`

## Bước 4: Sub pipeline

```bash
SRC="/Users/vieterp/code/Research/tools/reclip/downloads/<job_id>.mp4"
OUT="/Users/vieterp/code/Research/agent-flowkit/output/_sub/<job_id>_subbed.mp4"
mkdir -p "$(dirname "$OUT")"

python3 /Users/vieterp/code/Research/agent-flowkit/scripts/sub_video.py \
  --video "$SRC" \
  --output "$OUT" \
  --model <model> \
  --src-lang <src-lang> \
  --keep-srt
```

Pipeline nội bộ:
1. ffmpeg extract audio → 16kHz mono WAV
2. faster-whisper transcribe với VAD filter, beam_size=5
3. Claude translate chunked (30 lines/batch, claude-haiku-4-5)
4. Generate ASS subtitle: CN top nhỏ (vàng nhạt) + VN bottom lớn (trắng)
5. ffmpeg burn ASS, copy audio nguyên (không re-encode)

## Bước 5: Cleanup + verify

```bash
# Cleanup nguồn ReClip
rm -f "/Users/vieterp/code/Research/tools/reclip/downloads/<reclip_job_id>".*

# Verify
ffprobe -v quiet -show_entries format=duration:stream=width,height -of default=nw=1 "$OUT"
# Duration phải = source. Width/height match.
```

Report cho user:
- Source URL + title
- Output path
- Duration + size + segments count
- Sample 3-5 dialogue translations

---

## Output structure

```
output/_sub/<reclip_job_id>_subbed.mp4    # video với dual sub burn
output/_sub/<reclip_job_id>_subbed.srt    # SRT (nếu --keep-srt) — chỉ VN
```

ASS subtitle styling:
- **VN** (bottom): Arial 6% video height, white, black outline 2.4px
- **CN** (top): Arial 3.8% video height, light yellow, black outline 1.6px

## Common issues

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: faster_whisper` | `pip3 install --break-system-packages faster-whisper` |
| `certifi has no attribute 'where'` | `pip3 install --break-system-packages --ignore-installed --no-deps certifi` |
| Whisper slow (>5x realtime) | Dùng `--model small` thay vì `medium`/`large` |
| Translation empty / partial | Script đã chunk 30 lines + strip markdown fence; nếu vẫn fail, giảm chunk_size trong `translate_batch()` |
| Sub không hiện trên video | Verify ass file: `cat /tmp/.../subs.ass`; check ffmpeg log có ass filter error không |
| Sub size quá to/nhỏ | Adjust `fs_vn`/`fs_cn` trong `scripts/sub_video.py::write_ass` |
| ASR thoại lẫn nhạc nền sai nhiều | Upgrade `--model medium` (chậm hơn ~3x nhưng chính xác hơn) |
| Bilibili video chỉ 480p (locked HD) | Auto-fallback — nếu cần 1080p, login Bilibili VIP qua Chrome rồi retry |

## Tips

- **Test model nhỏ trước**: chạy `--model small` để check transcription thô; nếu sai nhiều thoại → upgrade `medium`
- **Chỉ muốn SRT, không burn**: comment dòng `burn(...)` cuối `main()` trong `sub_video.py`, dùng `--keep-srt`
- **Đổi style sub**: edit `write_ass()` trong script — font/size/color tự do
- **Multi-language source**: `--src-lang en` cho video tiếng Anh, `ja` cho tiếng Nhật, vv
- **Pipeline mất bao lâu**: video 3 phút → ~1 phút whisper small / ~3 phút medium + ~30s translate + ~20s burn
- **Output giữ nguyên audio gốc**: KHÔNG bị re-encode (codec `-c:a copy`)
