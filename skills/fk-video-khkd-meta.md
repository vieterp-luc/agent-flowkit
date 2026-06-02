# fk-video-khkd-meta — Video Khoa Học Kinh Dị (clip bằng Meta AI)

Biến thể của `/fk-video-khkd`: pipeline science-horror TikTok tiếng Việt **giống hệt**, nhưng
bước tạo video dùng **`/fk-gen-meta-video` (Meta AI image→video)** thay cho Google Flow/Veo.

Usage: `/fk-video-khkd-meta "<chủ đề>"`

> ⚠️ Clip Meta có **watermark + không có commercial license** → dùng thử nghiệm/cá nhân.
> Bản thương mại (YouTube monetize) → dùng `/fk-video-khkd` gốc (Veo).

---

## Khác biệt cốt lõi so với /fk-video-khkd

| Bước | /fk-video-khkd (gốc) | /fk-video-khkd-meta (bản này) |
|------|----------------------|-------------------------------|
| Tạo video | `/fk-gen-videos` (Flow/Veo, lưu vào DB) | **Meta image→video** (clip local) |
| Ghép | `/fk-concat-fit-narrator` (kéo clip từ DB) | **Assemble custom** (clip local: stretch + xfade + TTS) |
| Credits | Đốt Flow credits cho video | Video KHÔNG đốt Flow credits (chỉ ảnh) |
| Quota guardrail video | Bắt buộc (probe/halt) | Không cần — Meta không tính Flow credits |

Các bước còn lại (research, create-project, gen-images Flow, TTS, caption) **giữ nguyên**.

---

## Pipeline

```
/fk-create-project  →  /fk-gen-images  →  [Meta image→video batch]  →  TTS  →  [assemble custom]  →  /fk-gen-caption
```

## Bước 0–1: Research + thiết kế (giống /fk-video-khkd)

- Chủ đề: hiện tượng có thật + hàm ý đáng sợ + ít người biết.
- Project: `material: realistic`, `orientation: VERTICAL`, **5–10 scenes**, ngôn ngữ Việt.
- Scenes: arc HOOK → giải thích → chi tiết → tác động → kết ám ảnh. Cho montage macro, để
  **tất cả ROOT** (mỗi scene 1 cảnh riêng → không cần CONTINUATION/refs → gen ảnh đơn giản).
- Narrator VN **20–22 từ/scene** (xem `feedback-narrator-word-count`). Prompt ảnh + motion **bằng tiếng Anh**.
- `narrator_text` **KHÔNG lưu khi POST /api/scenes** — phải **PATCH** sau khi tạo scene
  (`PATCH /api/scenes/<id> {"narrator_text": "..."}`), nếu không TTS sẽ lỗi 422 (text rỗng).

## Bước 2: Gen ảnh scene (Flow)

`/fk-gen-images <PID> <VID>` — tất cả ROOT = `GENERATE_IMAGE`, orientation VERTICAL.
**Pre-flight** `GET /api/flow/credits` (≥ ~15 cho 10 ảnh). Gen theo **batch nhỏ (3–5)** tránh
reCAPTCHA (xem `feedback-flow-image-gen-per-chapter`). Rồi **tải ảnh về local**:
`output/<slug>/img/scene_NN.jpg` (lấy từ `vertical_image_url`).

## Bước 3: Meta image→video (thay /fk-gen-videos)

Pre-flight `/fk-gen-meta-video`: bootstrap login Meta 1 lần (`scripts/meta_bootstrap.py`).

Với MỖI scene, gọi tuần tự (browser khoá → serialize):

```bash
curl -X POST http://127.0.0.1:8100/api/meta/browser/generate-video \
  -d '{"prompt":"<motion prompt EN>","image_path":"output/<slug>/img/scene_NN.jpg","timeout":600,"headless":true}'
# OK → move path → output/<slug>/clips/scene_NN.mp4
```

**Bắt buộc:**
- `timeout: 600` (gen Meta 3–9 phút; capture qua **reload page định kỳ** vì SPA không tự cập nhật).
- **~30s gap** giữa các scene.
- Prompt gửi Meta = câu visual+motion (BỎ dòng Audio/SFX/Negative kiểu Veo — Meta tự sinh audio).
- Chạy **detached** + poll log; re-run để retry scene thiếu (skip clip đã có).

→ Viết driver loop qua các scene (gọi endpoint, move clip về `clips/scene_NN.mp4`, log),
chạy detached + poll log; re-run để retry scene thiếu.
Clip Meta theo tỉ lệ ảnh → ảnh dọc ra **9:16** (vd 464×832), **KHÔNG có audio track**, ~5s.

## Bước 4: TTS narrator

`Anh_Khoi_TTS` · speed `0.95` · full ref_text (template tự nạp). Per-scene:

```bash
curl -X POST http://127.0.0.1:8100/api/tts/generate \
  -d '{"text":"<narrator VN>","template":"Anh_Khoi_TTS","speed":0.95,"output_path":"output/<slug>/tts/scene_NN.wav"}'
```

TTS đúng = 5–7s (VN 20–22 từ, full ref_text). >8s → ref_text bị cắt (xem `feedback-tts-full-ref-text`).

## Bước 5: Assemble custom (thay /fk-concat-fit-narrator)

Clip Meta là file local (không trong DB) → ghép bằng ffmpeg trực tiếp. Per-scene segment:

- **Fit độ dài = TTS + 0.5s buffer.** Clip thường NGẮN hơn narrator → **kéo giãn tốc độ**
  `setpts={target/clip_dur}*PTS` (slow nhẹ, MƯỢT) — **KHÔNG tpad/freeze** (freeze gây "đơ" trước cắt).
- Scale/crop **720×1280**, fps 24.
- Audio = **chỉ TTS** (`volume≈1.4`) vì clip Meta im lặng.
- Concat với **crossfade 0.4s** (`xfade=transition=fade` + `acrossfade`) cho chuyển cảnh mượt.

→ Viết script ffmpeg theo logic trên (per-scene: TTS → setpts-stretch + scale → segment;
rồi xfade-concat tất cả). Output: `output/<slug>/<slug>_final.mp4` (720×1280, H.264, AAC).

## Bước 6: Caption

`/fk-gen-caption <video_id>` — tạo caption + hashtag từ narrator_text đã PATCH.

---

## Checklist nhanh

```
[ ] Research chủ đề + thiết kế 5–10 scene ROOT (narrator VN 20–22 từ)
[ ] /fk-create-project — VERTICAL, realistic
[ ] PATCH narrator_text cho từng scene (POST không lưu)
[ ] /fk-gen-images — batch nhỏ 3–5, pre-flight credits, tải ảnh → img/scene_NN.jpg
[ ] Meta image→video — bootstrap login; tuần tự, timeout 600, gap 30s, headless; → clips/scene_NN.mp4
[ ] TTS — Anh_Khoi_TTS 0.95, → tts/scene_NN.wav
[ ] Assemble — stretch-to-narrator (no freeze) + 720×1280 + xfade 0.4s + TTS audio → <slug>_final.mp4
[ ] /fk-gen-caption
```

## Lỗi thường gặp (đặc thù bản Meta)

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| TTS 422 Unprocessable | `narrator_text` null (POST không lưu) | PATCH narrator_text trước khi gọi TTS |
| `VIDEO_TIMEOUT` Meta | timeout < thời gian gen, hoặc SPA stale | `timeout: 600`; capture đã reload page định kỳ |
| Clip "đơ" trước khi chuyển | freeze frame cuối (tpad) | Dùng `setpts` stretch thay vì tpad |
| `[0:a] matches no streams` | Clip Meta không có audio | Audio segment = chỉ TTS, bỏ mix clip audio |
| Nhiều scene timeout liên tiếp | tưởng throttle | KHÔNG phải — tăng timeout + reload (xem `/fk-gen-meta-video`) |

## Ví dụ đã làm

| Video | OUTDIR | Đặc điểm |
|-------|--------|----------|
| Mạt Demodex | `output/khkd_mat_demodex` | 10 scene, Meta image→video 10/10, stretch+xfade, 57.8s |
