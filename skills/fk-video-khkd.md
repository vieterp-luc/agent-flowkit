# fk-video-khkd — Tạo Video Khoa Học Kinh Dị (Science+Horror TikTok)

Full pipeline từ ý tưởng đến video hoàn chỉnh cho kênh TikTok/Facebook khoa học kinh dị tiếng Việt.

Usage: `/fk-video-khkd "<chủ đề>"`

---

## Tổng quan pipeline

```
/fk-create-project  →  /fk-gen-refs  →  /fk-gen-images  →  /fk-gen-videos  →  /fk-gen-narrator  →  /fk-concat-fit-narrator  →  /fk-gen-caption
```

---

## Bước 0: Nghiên cứu chủ đề

Trước khi thiết kế, xác định rõ:

1. **Sự thật khoa học cốt lõi** — cơ chế thật sự giải thích hiện tượng là gì?
2. **Hook mở đầu** — câu hỏi kinh dị/gây sốc nhất để mở video (0-8s)
3. **Arc khoa học** — setup → giải thích → kết luận gây ám ảnh
4. **Visual ấn tượng nhất** — cảnh nào sẽ dừng ngón tay người xem?

**Chủ đề hiệu quả nhất:** Hiện tượng có thật + hàm ý đáng sợ + ít người biết.

---

## Bước 1: Thiết kế dự án (`/fk-create-project`)

### Cấu hình chuẩn cho kênh KHKD

| Tham số | Giá trị |
|---------|---------|
| Material | `realistic` |
| Orientation | `VERTICAL` (TikTok/Reels) |
| Số scenes | 5 scenes |
| Language | Vietnamese |

### Thiết kế 5 scenes theo arc chuẩn

| Scene | Vai trò | Chain type | Mục đích |
|-------|---------|-----------|----------|
| 0 | **HOOK** | ROOT | Câu hỏi/hình ảnh gây sốc — dừng ngón tay |
| 1 | **Giải thích khoa học** | ROOT | Cơ chế thật sự là gì |
| 2 | **Chi tiết khoa học** | CONTINUATION ← S1 | Đào sâu hơn, macro/closeup |
| 3 | **Tác động con người** | ROOT | Hệ quả thực tế với người |
| 4 | **Kết luận ám ảnh** | ROOT | Câu hỏi triết học/đóng video |

**Chain S1→S2:** CONTINUATION cho phép EDIT_IMAGE từ parent — giữ visual continuity cho cùng subject (ví dụ: đá bazan → root xoắn quanh đá, não bộ → synapse bị đứt).

### Entities chuẩn

- **2 characters tối đa** — chỉ tạo khi cần human element
- **1-2 locations** — setting chính của video
- **1-2 visual assets** — props/objects khoa học (brain scan, compass, cell...)
- Mỗi entity description ngắn gọn, tập trung visual appearance

### Narrator text (Vietnamese, CỨNG ở 20-22 từ)

```
[Sự thật viewer KHÔNG thấy được: context/stakes]. [Cơ chế/hệ quả]. [Câu ngắn gây ám ảnh.]
```

**Đếm từ:** Python `split()` tính cả dấu `—` là 1 token → thực tế viết 21-22 từ, sau khi tính dấu câu thường ra 22-23 tokens. Chấp nhận đến 23 tokens nếu dấu câu là nguyên nhân.

**Tránh:**
- Mô tả những gì viewer đang thấy: `"Chúng ta thấy một khu rừng"`
- Quá dài: >22 từ thật → TTS bị cắt ở giây 7
- Quá ngắn: <18 từ → dead air

### Prompts (LUÔN bằng tiếng Anh)

**Image prompt formula:**
```
[Subject] [action] [at/in Location]. [Specific detail]. [Camera/composition].
```

**Video prompt formula (100-150 words):**
```
[Shot type] of [subject] [action] in [setting]. [Camera movement sentence].
[Lighting]. [Atmosphere/mood detail].

Audio: [ambient sound].
SFX: [specific sound effects].
Negative: subtitles, watermark, text overlay.
```

**CRITICAL — tránh bị filter:**
- Không dùng: attack, kill, death, blood, destroy, explosion, weapon
- Thay bằng: aftermath, impact, loss, disrupt, flash, equipment

---

## Bước 2: Tạo reference images (`/fk-gen-refs`)

- Submit tất cả entities trong 1 batch call
- Poll 15s/lần đến khi `done: true`
- Verify tất cả có `media_id` UUID

---

## Bước 3: Generate scene images (`/fk-gen-images`)

**2 waves:**

| Wave | Scenes | Request type |
|------|--------|-------------|
| 1 | Tất cả ROOT scenes | `GENERATE_IMAGE` |
| 2 | CONTINUATION scenes (S2) | `EDIT_IMAGE` sau khi Wave 1 xong |

Poll Wave 1 → 15s/lần. Submit Wave 2 ngay khi Wave 1 `done: true`.

---

## Bước 4: Generate videos (`/fk-gen-videos`)

> ⚠️ **Quota safety** — đây là bước đốt credits nhiều nhất. Worker auto-retry `MAX_RETRIES=5` lần mỗi scene → 1 lần failure systemic = **5 scenes × 5 retries = 25 submissions** burn quota im lặng. Bắt buộc 3 guardrails dưới.

### 4.1 Pre-flight quota check (BẮT BUỘC)

```bash
curl -s http://127.0.0.1:8100/api/flow/credits
```

**Abort nếu:**
- `credits` field thiếu hoặc < 30 → quota chưa đủ cho 5 scenes (mỗi scene ~5-15 credits)
- `userPaygateTier` không khớp với project

Nếu credits thấp → báo user, KHÔNG submit. Resume sau khi reset.

### 4.2 Probe-first (1 scene → wait → 4 scenes còn lại)

**Không submit batch 5 ngay.** Probe 1 scene để verify pipeline OK trước:

```bash
# Submit chỉ scene 0
POST /api/requests/batch  { requests: [{ scene_id: <S0>, ... }] }

# Poll 30s/lần, MAX 4 phút
# Nếu COMPLETED → submit 4 scenes còn lại
# Nếu FAILED → STOP, đi qua 4.3
```

### 4.3 Halt-on-quota-error (chặn auto-retry)

Khi error message chứa **bất kỳ** pattern dưới:
- `QUOTA_REACHED`
- `no operations`
- `MODEL_ACCESS_DENIED`
- `UNSAFE_GENERATION` (3 lần liên tiếp)

**NGAY LẬP TỨC** chặn worker auto-retry tất cả PENDING/PROCESSING requests của video này:

```bash
# Force terminal (retry_count = MAX_RETRIES) cho tất cả pending requests
for rid in $(curl -s "/api/requests?video_id=<VID>&type=GENERATE_VIDEO" | jq -r '.[] | select(.status=="PENDING" or .status=="PROCESSING") | .id'); do
  curl -X PATCH "/api/requests/$rid" -d '{"status":"FAILED","retry_count":5}'
done
```

Sau đó diagnose → fix prompt/config → reset 1 scene → submit lại như 4.2.

### 4.4 Normal flow (sau khi probe OK)

- Submit 4 scenes còn lại 1 batch
- Poll 30s/lần (video gen lâu hơn image)
- Nếu 1 scene `FAILED`: chạy 4.3 trước, KHÔNG resubmit ngay
- Verify tất cả `COMPLETED` với UUID media_id

---

## Bước 5: Generate TTS (`/fk-gen-narrator`)

**Voice template chuẩn:** `Anh_Khoi_TTS` · Speed `0.95`

> ⚠️ **CRITICAL — full ref_text bắt buộc.** `ref_text` PHẢI bằng chính xác transcript trong `output/_shared/tts_templates/templates.json` (3 câu, không cắt). Truncated ref_text → voice cloning sai prosody → TTS chậm gấp 2x (10-17s thay vì 5-7s) → narrator bị cắt giữa câu trong scene 7s. Đọc transcript bằng:
> ```bash
> jq -r '.Anh_Khoi_TTS.text' output/_shared/tts_templates/templates.json
> ```

```
REF_AUDIO: output/_shared/tts_templates/Anh_Khoi_TTS.wav
REF_TEXT:  "Năm hai nghìn không trăm hai mươi tư, thế giới thay đổi mãi mãi. Các quốc gia hưng thịnh và sụp đổ, anh hùng xuất hiện từ bóng tối, và những người bình thường đối mặt với thử thách phi thường."
```

**Output path chuẩn:**
```
output/{slug}/tts/scene_{IDX3}_{scene_id}.wav
```

**Kiểm tra TTS duration ngay sau gen** (BẮT BUỘC):
```bash
for f in output/{slug}/tts/scene_*.wav; do
  ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f"
done
```

**TTS duration đúng (speed 0.95, full ref_text, VN 18-22 từ):** **5-7s** — nằm trong usable window 7s.

| Symptom | Likely cause | Fix |
|---|---|---|
| TTS > 8s | `ref_text` bị truncate (chỉ 1 câu) | Reload full 3-câu transcript từ `templates.json`, regen TTS |
| TTS > 7s nhưng < 8s | Narrator > 22 từ thật | Rewrite narrator ngắn lại |
| TTS < 4s | Narrator < 18 từ → dead air | Bổ sung câu kết |

---

## Bước 6: Concat + trim (`/fk-concat-fit-narrator`)

### Cấu hình trim

| Tham số | Giá trị |
|---------|---------|
| Buffer | 0.5s sau TTS |
| `-ss` seek | 1s (bỏ frame đầu tĩnh) |
| SFX volume | 0.3 (30%) |
| TTS volume | 1.5 (150%) |
| FPS | 24 |
| Resolution | 720×1280 (VERTICAL) |

### Chain xfade (scenes 1+2)

Scenes 1+2 là CONTINUATION chain → áp dụng xfade crossfade 0.5s trước khi concat.

```
Segments: [S0] [chain_001: S1→S2 xfade] [S3] [S4]
```

### Output

```
output/{slug}/{slug}_narrator_cut.mp4
```

**Verify:** `mean_volume` phải từ -30 đến -10 dB (không phải -inf).

---

## Bước 7: Tạo caption (`/fk-gen-caption`)

Sau khi có file `{slug}_narrator_cut.mp4`, chạy `/fk-gen-caption` để tạo caption từ narrator text đã có.

```
/fk-gen-caption <video_id>
```

---

## Checklist nhanh

```
[ ] /fk-create-project — 5 scenes, VERTICAL, realistic, narrator texts 20-22 từ
[ ] /fk-gen-refs       — 4 entities, 1 batch, poll 15s
[ ] /fk-gen-images     — Wave 1 ROOT, Wave 2 CONTINUATION (EDIT_IMAGE)
[ ] Pre-flight quota check (/api/flow/credits ≥ 30)
[ ] /fk-gen-videos     — PROBE 1 scene → verify OK → submit 4 còn lại; halt-on-quota-error trước khi worker auto-retry 5×
[ ] /fk-gen-narrator   — Anh_Khoi_TTS speed 0.95, output tts/scene_IDX3_SID.wav
[ ] /fk-concat-fit-narrator — download 4k, trim, xfade S1+S2, concat
[ ] /fk-gen-caption        — tạo caption từ narrator text
```

---

## Ví dụ đã làm

| Video | OUTDIR | Đặc điểm |
|-------|--------|----------|
| Zombie Khoa Hoc | `output/zombie_khoa_hoc_vn` | Ophiocordyceps, 5 scenes |
| Simulation Theory | `output/simulation_theory_vn` | Physics, 5 scenes |
| Sieu Sinh Vat VN | `output/sieu_sinh_vat_vn` | Spider colony, 5 scenes |
| Capgras VN | `output/capgras_vn` | Neurology, 5 scenes |
| Aokigahara VN | `output/aokigahara_vn` | Geology+psychology, 5 scenes |

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| TTS bị cắt giữa câu | >22 từ thật | Viết lại ngắn hơn |
| Dead air cuối scene | <18 từ | Thêm câu kết |
| `GENERATE_VIDEO` skip FAILED | Status chưa reset | PATCH `vertical_video_status: PENDING` trước |
| Quota burn 25× im lặng | Worker auto-retry MAX_RETRIES=5/scene × 5 scenes | Probe-first (4.2) + halt-on-quota-error (4.3) trước khi batch |
| "Video gen returned no operations" | Thường mask QUOTA_REACHED hoặc Flow filter | Check `/api/flow/credits` ngay; nếu credits OK → simplify prompt (remove violently/motionless/no movement) |
| JSON parse error | Em-dash trong narrator_text | Dùng Python subprocess + `ensure_ascii=False` |
| Scene bị trùng display_order | API tạo duplicate | DELETE scene thừa trước khi gen images |
| mean_volume = -inf | Audio track bị mất | Kiểm tra `-an` flag, luôn dùng `-ar 48000 -ac 2` |
