# fk-reel-whatif — Short "Nếu... thì sao" (What-if) bằng Meta AI

Tạo 1 reel science-horror dạng **"Nếu X thì sao?"** — viễn cảnh siêu thực + giọng đọc doom,
đúng sweet spot Meta AI video. 9:16, ~40s, 7 scene. Pipeline + giọng/nhịp đã A/B chốt sẵn.

Usage: `/fk-reel-whatif "<chủ đề what-if>"`  (vd: "Nếu đại dương cạn khô?")

> ⚠️ Clip Meta có **watermark + không commercial license** → dùng build view/thử nghiệm.
> Bản monetize nghiêm túc → dùng Veo (`/fk-video-khkd`). Xem [[reference-meta-video-skill]].

> 📁 **Output convention:** MỌI video What-if vào `output/whatif/<slug>/` (gọn, dễ quản lý).
> `whatif_produce.py` tự prefix `whatif/`; nếu chạy script lẻ thì truyền slug dạng
> `whatif/<slug>` (vd `python3 scripts/meta_video_batch.py <vid> whatif/<slug>`).

## Default đã khoá (không hỏi lại)
| Tham số | Giá trị |
|---------|---------|
| Tỉ lệ / độ dài | 9:16 (720×1280), ~38–44s, **7 scene × ~5s** |
| Giọng | **`Phong_Vien_TTS` · speed 0.9** + nghỉ ~0.4s giữa scene (đã A/B — xem [[feedback-whatif-meta-voice-default]]) |
| Ghép | stretch clip→narrator (no freeze) + scale 720×1280 + **xfade 0.4s** + audio `apad` (chống lệch sync) |
| Material ảnh | `realistic` |
| Audio | clip Meta im lặng → chỉ narrator TTS (BGM tuỳ chọn, add sau) |

## Công thức 7 scene (leo thang theo mốc thời gian — giữ retention)
```
S0 HOOK     — "Nếu X?" + hình sốc nhất
S1 Ngay lập tức — chuyện xảy ra trong giây/phút đầu
S2 Leo thang 1  — vài giờ/ngày sau, hệ quả vật lý
S3 Leo thang 2  — vài ngày/tháng sau, hệ quả sinh tồn
S4 Đỉnh điểm    — cảnh tàn khốc/hùng vĩ nhất
S5 Con người    — điều gì xảy ra với loài người
S6 Kết ám ảnh   — câu chốt triết lý / con số lạnh gáy
```

## Quy tắc nội dung
- **Chủ đề:** viễn cảnh siêu thực + **có lõi khoa học thật** (credible, không bịa). Hợp Meta: vũ trụ, thảm hoạ địa cầu, sinh học, body-horror.
- **Narrator VN 18–22 từ/scene**, có dấu câu (TTS tự ngắt). Theo mốc thời gian leo thang.
- **Image + motion prompt = tiếng Anh.** Ép style: `cinematic, hyper-realistic, photorealistic, dramatic atmospheric lighting, epic scale, vertical 9:16, no text`.
- **Né:** chữ trong khung, mặt người cận (Meta méo), hành động phức tạp. Tránh từ bạo lực thô (dùng aftermath/impact/loss) để qua filter.
- **Motion prompt phải animate được từ ẢNH:** mô tả **camera move + chuyển động khí quyển** trên thứ CÓ trong khung (push-in, pan, drift, sương, bụi, gợn sóng). KHÔNG mô tả chuyển động của thứ không có trong ảnh (vd "nước rút cạn" khi ảnh đã là đáy biển khô) → Meta trả `META_CHAT_ERROR "couldn't animate"`. Nếu gặp lỗi đó: đổi motion sang camera/atmospheric, hoặc gen lại ảnh khác.

## Prerequisites
- Server: `curl -s http://127.0.0.1:8100/health` (extension_connected + Flow credits).
- Meta login 1 lần: `venv/bin/python scripts/meta_bootstrap.py`.
- Voice `Phong_Vien_TTS` có trong `output/_shared/tts_templates/`.

## Pipeline (mỗi video ~25–45 phút máy chạy)

**1. Viết script 7 scene** cho chủ đề (theo công thức + quy tắc trên): mỗi scene = narrator VN + image prompt EN + motion prompt EN.

**2. Tạo project + 7 scene ROOT** (VERTICAL, realistic) qua API, rồi **PATCH `narrator_text`** từng scene (POST /api/scenes KHÔNG lưu narrator → bắt buộc PATCH, nếu không TTS lỗi 422). Mẫu: `scripts/whatif_d1_setup.py`.

**3. Gen ảnh Flow** — pre-flight `/api/flow/credits`; submit `GENERATE_IMAGE` theo **batch nhỏ 3–4** (tránh reCAPTCHA), poll `done:true`; rồi **tải ảnh về** `output/<slug>/img/scene_NN.jpg`.

**4. Meta image→video** (tuần tự, headless, timeout 600, gap 30s):
```bash
nohup python3 scripts/meta_video_batch.py <video_id> <slug> > /tmp/whatif.out 2>&1 &
# poll output/<slug>/meta_gen.log tới "DONE n/7"; re-run để retry scene thiếu
```

**5. Ghép (default đã đúng):**
```bash
python3 scripts/meta_assemble.py <video_id> <slug>
# → output/<slug>/<slug>_final_Phong_Vien_TTS_09.mp4
# (đổi giọng/tốc độ: thêm arg [voice] [speed]; đổi nghỉ: sửa BUFFER trong script)
```

**6. Logo (tự động):** `whatif_produce.py` tự gắn logo kênh sau khi ghép →
`<final>_logo.mp4` (góc trên-trái, 13% rộng, 75% trong suốt, `assets/whatif_logo.png`).
Gắn tay: `python3 scripts/add_logo.py <video>`. Đây là bản đăng.

**7. Hậu kỳ thủ công + caption:**
- CapCut/Canva: text hook *"Nếu X?"* + nhãn mốc thời gian (*"8 phút sau", "1 tuần sau"*).
- `/fk-gen-caption <video_id>` → caption + hashtag.

## Checklist
```
[ ] Script 7 scene (hook→leo thang→kết, narrator 18–22 từ, lõi KH thật)
[ ] Create project + 7 ROOT scenes + PATCH narrator_text
[ ] Gen ảnh Flow batch nhỏ → tải img/scene_NN.jpg
[ ] meta_video_batch.py → clips/scene_NN.mp4 (poll log, retry thiếu)
[ ] meta_assemble.py (default Phong_Vien 0.9 + nghỉ 0.4s) → final
[ ] CapCut overlay hook + mốc thời gian; /fk-gen-caption
```

## Lỗi thường gặp
| Lỗi | Fix |
|-----|-----|
| TTS 422 | PATCH `narrator_text` trước (POST không lưu) |
| Audio lệch trước video ~1s | đã fix bằng `apad` trong assemble — đừng bỏ |
| Clip "đơ" trước chuyển | dùng `setpts` stretch, KHÔNG tpad/freeze |
| Meta `VIDEO_TIMEOUT` | timeout 600 + reload-capture (xem `/fk-gen-meta-video`) |
| reCAPTCHA khi gen ảnh (`UNUSUAL_ACTIVITY_TOO_MUCH_TRAFFIC`) | Gen ~40+ ảnh liên tiếp (chạy loạt nhiều ngày 1 mạch) sẽ trip anti-bot. Fix: batch nhỏ 3–4; nếu chạy loạt thì **giãn cách giữa các video**; khi đã dính → user mở tab Flow giải captcha, rồi regen **1 ảnh/lần** (xong hẳn mới ảnh kế, nghỉ ~30s) |

## Ý tưởng chủ đề (kho)
Mặt Trời biến mất · trọng lực mất 5 giây · đại dương cạn · loài người biến mất · Trái Đất ngừng quay · không bao giờ ngủ lại (FFI) · Mặt Trăng rơi · Trái Đất mất từ trường · oxy biến mất 5 giây · Internet sụp toàn cầu.
Plan mẫu 7 ngày: `plans/whatif-1week-plan-260603-0909.md`.

## Đã làm
| Video | OUTDIR |
|-------|--------|
| Nếu Mặt Trời biến mất 24h | `output/neu_mat_troi_bien_mat` (7/7 clip, 40s) |
