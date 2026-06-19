# KHKD Long-form #1 — "Top 10 Ký Sinh Trùng Kinh Dị Nhất Trái Đất"

> **Status: CHƯA SẢN XUẤT.** Video dài ~6–7 phút, đổi gió khỏi reel ngắn. **Tái dùng 10 reel ĐÃ LÀM**
> (bản branded có logo) + chỉ sản xuất mới: VO dẫn + card thứ hạng + nhạc nền + ghép.
> Định dạng dọc 9:16 (đăng FB/Reels dài + YouTube). Kênh: Khoa Học Kinh Dị.

## Vì sao chọn format này
- Rẻ + nhanh: không gen lại ảnh/clip Flow/Meta — chỉ ghép.
- Tận dụng lại content cũ (re-monetize), giữ người xem lâu → thuật toán đẩy mạnh hơn reel.
- Lane ký sinh trùng là lane VIRAL nhất của kênh (theo data FB).

## Bảng xếp hạng (10 → 1) + asset tái dùng

| Hạng | Loài | Twist 1 câu | Asset | Dur |
|------|------|-------------|-------|-----|
| 10 | **Sacculina** | Hà ký sinh thiến cua, biến cua đực thành "mẹ nuôi" | `output/khkd_video/sacculina_vn/video.mp4` | 28s |
| 9 | **Cymothoa** | Rận ăn lưỡi cá rồi THÀNH cái lưỡi | `output/khkd_video/cymothoa_vn/video.mp4` | 26s |
| 8 | **Phorid fly** | Ruồi đẻ vào đầu kiến, đầu kiến tự rụng | `output/khkd_video/phorid_fly_vn/video.mp4` | 30s |
| 7 | **Botfly** | Ấu trùng lớn lên trong da thú rừng | `output/khkd_video_3006_0907/khkd_botfly_thu_rung/video.mp4` | 45s |
| 6 | **Hairworm** | Giun ép dế nhảy xuống nước tự sát | `output/khkd_video/hairworm_vn/video.mp4` | 30s |
| 5 | **Ribeiroia** | Sán làm ếch mọc 8 chân để dễ bị chim ăn | `output/khkd_video_3006_0907/khkd_ech_tam_chan/video.mp4` | 44s |
| 4 | **Glyptapanteles** | Sâu bướm bị ép canh gác kén kẻ ăn mình | `output/khkd_video/glyptapanteles_vn/video.mp4` | 28s |
| 3 | **Hymenoepimecis** | Nhện bị ép dệt "nhà" cho ấu trùng ong | `output/khkd_video/hymenoepimecis_vn/video.mp4` | 30s |
| 2 | **Toxoplasma** | Ký sinh điều khiển hành vi, lây sang người nuôi mèo | `output/khkd_video/toxoplasma_vn/video.mp4` | 31s |
| 1 | **Cordyceps** | Nấm zombie chiếm não kiến, mọc xuyên đầu | `output/khkd_video/cordyceps_vn/video.mp4` | 30s |

Tổng clip ≈ 322s (5.4 phút). + intro/card/outro → **~6.5–7 phút.**
Dự phòng nếu cần dài hơn: thêm Massospora (ve sầu zombie) / Sán lá gan.

## Cấu trúc video

```
[INTRO ~25s]  Hook VO + montage 4–5 cảnh giật gân từ các reel + tiêu đề "TOP 10"
   │
[HẠNG 10] card 3s ("HẠNG 10 — SACCULINA" + VO 1 câu) → reel Sacculina (audio gốc)
[HẠNG 9 ] card 3s → reel Cymothoa
   │ … (giảm dần tới HẠNG 1)
[HẠNG 1 ] card 4s ("HẠNG 1 — CORDYCEPS") → reel Cordyceps
   │
[OUTRO ~20s]  CTA comment "bạn sợ loài nào nhất?" + theo dõi xem phần 2 + logo
```

- **BGM**: 1 track lo-fi/horror ambient chạy xuyên suốt, **ducking** xuống khi có narration reel.
- **Card thứ hạng**: nền tối + số hạng lớn + tên loài (ffmpeg drawtext), hoặc frame blur từ reel + text. Có sound "whoosh" chuyển cảnh.
- Reel giữ nguyên audio gốc (đã có narrator + đã branded logo).

## Sản xuất mới (chỉ 4 thứ)
1. **VO dẫn** (`Anh_Khoi_TTS` 0.95): 1 đoạn intro (~50 từ) + 10 câu card (~12–15 từ/câu) + 1 outro (~30 từ). Gen qua `/api/tts/generate`.
2. **Card thứ hạng** ×10 + intro/outro title (ffmpeg drawtext hoặc gen ảnh).
3. **BGM**: lấy 1 track có sẵn (`output/_shared`) hoặc gen `/fk-gen-music`; transcode mp3.
4. **Ghép** (ffmpeg): chuẩn hóa mọi clip về 720×1280/24fps → concat intro + (card+reel)×10 + outro; mix BGM ducking; xfade 0.3s giữa các block.

→ Viết script `scripts/khkd_longform_build.py` (đọc danh sách hạng + asset, gen card, mix, concat). Tái dùng convention 720×1280 như `meta_assemble.py`.

## Tiêu đề + caption (gợi ý)
- Tiêu đề: **"Top 10 Ký Sinh Trùng Kinh Dị Nhất Trái Đất | Khoa Học Kinh Dị"**
- Hook thumbnail: ảnh kiến nhiễm cordyceps + chữ "TOP 10" + "#1 SẼ ÁM ẢNH BẠN".
- Caption: liệt kê nhanh 10 loài + câu hỏi comment-bait + hashtag.

## KPI
- Mục tiêu giữ chân: ≥3 phút avg view (long-form). Test xem format dài có outperform reel về watch-time tổng không → quyết định có làm series "Top 10" định kỳ.

## Câu hỏi chưa chốt
- Card thứ hạng: **drawtext đơn giản** (nhanh) hay **gen ảnh đẹp** (lâu hơn)? (đề xuất: drawtext cho bản đầu)
- BGM: lấy track có sẵn hay gen mới qua Suno/Lyria?
- Đăng đâu trước: FB (dọc) hay cắt ngang cho YouTube?
