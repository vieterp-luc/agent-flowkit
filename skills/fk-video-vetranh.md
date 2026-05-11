# fk-video-vetranh — Tạo Video Vẽ Tranh + Đạo Lý

Full pipeline tạo video vẽ tranh sơn dầu từng lớp kèm narrator đọc câu đạo lý xuyên suốt.

Usage: `/fk-video-vetranh "<tên project>"`

---

## Tổng quan pipeline

```
/fk-upload-image  →  /fk-create-project  →  /fk-gen-images (4 waves)  →  /fk-gen-videos  →  TTS đơn  →  Concat full + mix  →  /fk-gen-caption
```

**Điểm khác biệt so với KHKD:**
- Không cần `/fk-gen-refs` — entity dùng ảnh tranh đã upload
- TTS **1 file duy nhất** cho cả video (không per-scene trim)
- Concat full scenes → mix TTS overlay (narrator nói xuyên suốt)
- Material: `oil_painting`
- 4 scenes = 1 chain liên tục (ROOT + 3 CONTINUATION)

---

## Bước 0: Upload ảnh tranh (`/fk-upload-image`)

```bash
curl -X POST http://127.0.0.1:8100/api/flow/upload-image \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/painting.jpg", "file_name": "descriptive_name.jpg"}'
# Lưu lại media_id UUID trả về
```

---

## Bước 1: Thiết kế dự án (`/fk-create-project`)

### Cấu hình chuẩn

| Tham số | Giá trị |
|---------|---------|
| Material | `oil_painting` |
| Orientation | `VERTICAL` |
| Số scenes | 4 scenes |
| Language | Vietnamese |
| Entities | 1 visual_asset (bức tranh) |

### Entity duy nhất: bức tranh

```json
{
  "name": "Tên Bức Tranh",
  "entity_type": "visual_asset",
  "description": "Mô tả chi tiết bức tranh bằng tiếng Anh: subject, style, colors, composition",
  "media_id": "<UUID từ bước 0>"
}
```

**Sau khi tạo project**, patch media_id vào entity nếu chưa có:
```bash
curl -X PATCH http://127.0.0.1:8100/api/characters/<ENTITY_ID> \
  -d '{"media_id": "<UUID>"}'
```

### Thiết kế 4 scenes theo arc vẽ tranh

| Scene | Giai đoạn | Chain type | Image prompt |
|-------|-----------|-----------|-------------|
| 0 | ~20% — Nền (núi/bầu trời) | ROOT | Canvas trắng, brush strokes đầu tiên lộ dần |
| 1 | ~50% — Mid-ground (cầu/suối) | CONTINUATION ← S0 | Chi tiết trung cảnh xuất hiện |
| 2 | ~75% — Foreground (nhà/cây) | CONTINUATION ← S1 | Lớp tiền cảnh được vẽ thêm |
| 3 | 100% — Hoàn chỉnh | CONTINUATION ← S2 | Bức tranh đầy đủ, camera lùi ra |

### Narrator text (4 câu đạo lý, ~20-21 từ/câu)

Viết 4 câu độc lập theo chủ đề. Các câu sẽ được **ghép thành 1 đoạn** để gen TTS duy nhất.

```
[Câu 1: setup — mở đề về thiên nhiên/cuộc sống]
[Câu 2: hình ảnh cụ thể — núi, suối, cây dạy gì]
[Câu 3: áp dụng vào con người — hạnh phúc, giản dị]
[Câu 4: kết — thông điệp tổng quát]
```

**Patch narrator_text vào từng scene** (để lưu reference), nhưng TTS sẽ gen từ đoạn ghép.

### Prompts (LUÔN bằng tiếng Anh)

**⚠️ Lưu ý quan trọng khi viết prompts:**

1. **Bối cảnh vẽ tranh phải nhất quán xuyên suốt tất cả scenes.** Nếu scene 0 vẽ trong phòng studio thì tất cả các scene sau phải giữ nguyên bối cảnh trong phòng đó. Nếu vẽ ngoài bãi cỏ thì toàn bộ vẫn là bãi cỏ. Chỉ được thay đổi góc quay (zoom in/out, pan, tilt), không được đổi location.

2. **Chuyển động tay họa sĩ phải đồng bộ với sự thay đổi bức tranh.** Khi bức tranh hiện thêm chi tiết mới (ví dụ: cây xuất hiện), tay/cọ phải đang vẽ đúng vùng đó. Mô tả rõ trong video prompt: tay đang vẽ vùng nào, brush stroke hướng nào, chi tiết nào đang được hoàn thiện.

**Image prompt — canvas painting-in-progress:**
```
[Setting: e.g. "in a warmly lit studio" / "outdoors on a grassy field"] —
[Stage description] oil painting canvas, [elements appearing] through brush strokes,
[completion level: half-finished / three-quarters complete / completed],
visible paint texture and layers, [camera: medium shot / close-up / wide shot].
```

**Video prompt — brush strokes animation:**
```
[Shot] of oil painting canvas [in the same setting as previous scenes — e.g. "in the studio"]
as [specific elements] emerge through [brush/palette knife] strokes.
[Artist's hand/brush moves across the canvas adding {specific detail being painted}.]
The camera [slowly zooms in / pans / tilts] as paint fills in [details].
[Warm/soft] [studio/outdoor] lighting illuminates the wet paint, thick impasto texture visible.

Audio: quiet [studio/outdoor] ambiance.
SFX: [brush on canvas / palette knife scraping].
Negative: subtitles, watermark, text overlay.
```

---

## Bước 2: Generate scene images (`/fk-gen-images`)

**4 waves tuần tự** (chain phụ thuộc nhau):

| Wave | Scene | Request type |
|------|-------|-------------|
| 1 | Scene 0 (ROOT) | `GENERATE_IMAGE` |
| 2 | Scene 1 | `EDIT_IMAGE` sau Wave 1 |
| 3 | Scene 2 | `EDIT_IMAGE` sau Wave 2 |
| 4 | Scene 3 | `EDIT_IMAGE` sau Wave 3 |

Poll từng wave 10s/lần. Submit wave tiếp theo chỉ khi wave trước `done: true`.

**Nếu có ghost scene trùng display_order:** DELETE trước khi gen.

---

## Bước 3: Generate videos (`/fk-gen-videos`)

- Submit tất cả 4 scenes 1 batch
- Poll 30s/lần
- Verify tất cả `COMPLETED` với UUID media_id

---

## Bước 4: Generate TTS (1 file duy nhất)

**Ghép 4 câu đạo lý thành 1 đoạn, gen 1 file TTS duy nhất:**

```bash
curl -X POST http://127.0.0.1:8100/api/tts/generate \
  -d '{
    "text": "<câu 1>. <câu 2>. <câu 3>. <câu 4>.",
    "ref_audio": "output/_shared/tts_templates/Anh_Khoi_TTS.wav",
    "ref_text": "Năm hai nghìn không trăm hai mươi tư...",
    "speed": 0.7,
    "output_path": "output/{slug}/tts/narrator_full.wav"
  }'
```

**Voice template chuẩn:** `Anh_Khoi_TTS` · Speed `0.7` (chậm, thấm)

**Kiểm tra duration:**
- TTS phải ngắn hơn video ít nhất 1s (breathing room cuối)
- Video full = `(số scenes × 7s) - (xfade overlap)` ≈ 26s với 4 scenes
- TTS target: ~20-25s

---

## Bước 5: Concat full + mix TTS

### 5a. Download và concat full scenes (không trim theo TTS)

```bash
# Download từng scene (ss 1, giữ 7s)
ffmpeg -ss 1 -i <video_url> -t 7 -c:v libx264 -crf 18 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 24 -pix_fmt yuv420p -c:a aac -ar 48000 -ac 2 \
  output/{slug}/raw/scene_{IDX}.mp4

# xfade concat 4 scenes
ffmpeg -i s0 -i s1 -i s2 -i s3 \
  -filter_complex "[xfade chain with 0.5s crossfade][acrossfade chain]" \
  -map [vout] -map [aout] output/{slug}/concat_full.mp4
```

**xfade offset formula:**
```python
XFADE = 0.5
cum = dur[0]
for i in range(N-1):
    offset = round(cum - XFADE, 3)
    # build filter...
    cum = offset + dur[i+1]
```

### 5b. Mix TTS vào concat video

```bash
ffmpeg -i concat_full.mp4 -i narrator_full.wav \
  -filter_complex "[0:a]volume=0.3[bg];[1:a]volume=1.5[fg];[bg][fg]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  output/{slug}/{slug}_full_narrator.mp4
```

**Key flags:**
- `duration=first` — audio theo độ dài video (TTS kết thúc trước, không extend)
- `-c:v copy` — không re-encode video, nhanh hơn
- SFX 30%, TTS 150%

### Output

```
output/{slug}/concat_full.mp4          # video thuần (không TTS)
output/{slug}/{slug}_full_narrator.mp4 # video + TTS hoàn chỉnh
output/{slug}/tts/narrator_full.wav    # TTS file
```

---

## Bước 6: Tạo caption (`/fk-gen-caption`)

Sau khi có `{slug}_full_narrator.mp4`, chạy `/fk-gen-caption` để tạo caption từ narrator text.

```
/fk-gen-caption <video_id>
```

---

## Checklist nhanh

```
[ ] /fk-upload-image  — upload ảnh tranh, lưu media_id
[ ] /fk-create-project — 4 scenes, VERTICAL, oil_painting, 1 visual_asset entity
[ ]   Patch media_id vào entity nếu chưa tự link
[ ]   Patch narrator_text vào từng scene (reference)
[ ] /fk-gen-images    — 4 waves tuần tự (GENERATE → EDIT → EDIT → EDIT)
[ ] /fk-gen-videos    — 1 batch, poll 30s
[ ]   Gen TTS đơn: 4 câu ghép, Anh_Khoi_TTS, speed 0.7
[ ]   Download raw scenes, xfade concat → concat_full.mp4
[ ]   Mix TTS vào concat_full → {slug}_full_narrator.mp4
[ ]   Verify: TTS dur < video dur, mean_volume -30 đến -10 dB
[ ] /fk-gen-caption       — tạo caption từ narrator text
```

---

## Ví dụ đã làm

| Video | OUTDIR | Đặc điểm |
|-------|--------|----------|
| Tranh ngôi làng bên núi | `output/tranh_ngoi_lang_ben_nui` | Alpine village oil painting, 4 scenes chain, TTS 24.85s/26.6s video |

**Narrator texts mẫu (chủ đề Thiên nhiên & Tâm hồn):**
```
Sống giữa thiên nhiên, lòng người dần trở nên trong sáng và thanh thản hơn giữa bao bộn bề cuộc sống.
Suối chảy dạy ta sự buông bỏ — hãy để muộn phiền trôi đi như dòng nước trong lành mỗi ngày.
Mái nhà giản dị giữa núi rừng nhắc ta rằng hạnh phúc thật sự đến từ những điều đơn giản nhất.
Hòa mình vào thiên nhiên là cách mang về một tâm hồn trong sáng, bình yên giữa cuộc sống bộn bề.
```

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| Entity `media_id=none` sau create | API không link tự động | PATCH `/api/characters/<ID>` với media_id |
| Ghost scene trùng display_order | API tạo duplicate | DELETE scene thừa trước Wave 1 |
| TTS dài hơn video | 4 câu quá dài ở speed thấp | Rút ngắn mỗi câu 1-2 từ hoặc tăng speed lên 0.75 |
| xfade stall | `apad` trong filter | Dùng `duration=first`, không dùng `apad` |
| Bối cảnh thay đổi giữa scenes | Prompt thiếu location anchor | Thêm setting cố định vào mỗi prompt: "in the same studio", "on the same grassy field" |
| Tay họa sĩ vẽ sai vùng | Video prompt không chỉ rõ vùng đang vẽ | Mô tả rõ: "brush moves across the [upper-left / foreground / sky area]" |
| mean_volume = -inf | Audio mất | Kiểm tra không có `-an`, dùng `-ar 48000 -ac 2` |
| JSON parse error khi gen TTS | Em-dash trong text | Dùng Python `json.dumps()` để escape |
