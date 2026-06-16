# fk-phim-khkd — Khoa Học Kinh Dị long-form (storyteller ngôi 3, factual)

Tạo **video khoa học kinh dị long-form ~5–8 phút** kể chuyện **ngôi thứ 3 điện ảnh** về một
chủ đề **động/thực vật có thật** (predator-horror, ký sinh, dị thể). Dùng **engine `/fk-phim`**
(ảnh tĩnh Meta + motion hành động + Ken Burns fallback + ghép local Flow-free), nhưng khoá
default + guardrail riêng cho lane KHKD. **Ngang 16:9 (1280×720)** cho YouTube long-form, ~42–46 scene.

> 🧬 **KHÁC tiểu thuyết:** nội dung là KHOA HỌC THẬT → "không bịa" = **fact phải chính xác**
> (research trước), KHÔNG cần text gốc. → ✅ tự research bằng WebSearch, KHÔNG bịa số liệu/cơ chế.
> 🖥️ **16:9:** `visual_style` PHẢI có `horizontal 16:9 widescreen landscape format` (để Meta sinh ảnh NGANG ~1440×810). `meta_assemble.py` tự nhận diện ngang/dọc từ clip → xuất 1280×720. (Muốn dọc 9:16 thì đổi lại visual_style sang `vertical 9:16 portrait`.)
> ⚠️ Ảnh Meta có watermark + non-commercial → KHÔNG bật kiếm tiền YouTube (giống `/fk-phim`).

## Default đã khoá (không hỏi lại)
| Tham số | Giá trị |
|---------|---------|
| Định dạng | **Long-form ~5–8 phút**, **ngang 16:9 (1280×720)** cho YouTube, **~42–46 scene (1 ảnh/scene)** |
| Giọng | **`Anh_Khoi_TTS` · 0.95** (giọng horror tài liệu KHKD) |
| motion_mode | **`meta_video`** (clip image→video) — pipeline FLOW-FREE (local mode) |
| visual_style | `cinematic nature documentary macro, extreme close-up, dramatic low-key lighting, dark ominous atmosphere, scientific realism, shallow depth of field, eerie horror mood, horizontal 16:9 widescreen landscape format, no text` |
| Narrator | VN ~25–30 từ/scene, ngôi 3 trang trọng + rùng rợn, bám fact |
| Output | `output/phim/<topic_slug>/` (story.json + ep01/) |

## ⛔ CHỐNG TRÙNG + chọn topic (LÀM TRƯỚC TIÊN)
1. **ĐỌC `plans/khkd-produced-topics.md`** — danh sách mọi chủ đề đã làm (reel 40s + long-form). KHÔNG lặp.
2. Ưu tiên **động/thực vật** (user thích). ✅ ký sinh / dị thể cơ thể / predator-horror visceral. Hook "Con X này… nhưng [twist]".
3. ❌ NÉ: mắt+ký sinh (shadowban), vật lý/triết/simulation, địa danh/thảm họa, động vật "thường" (muỗi/sếu), suicide framing, bệnh người nếu user muốn động/thực vật.
4. Đề xuất 3–4 topic FRESH (đã đối chiếu registry) → user chọn. Sau khi làm xong: **GHI vào registry** (mục "Long-form /fk-phim").

## Pipeline (8 bước — chuẩn từ video "Kiến Quân Đội")
1. **Research fact** (WebSearch ≥2 lần): số liệu, cơ chế, hành vi, lịch sử. Phân biệt **sự thật vs lời đồn** (nói rõ "từng được kể là…" nếu là folklore). KHÔNG bịa.
2. **story.json** (`output/phim/<slug>/story.json`): title, genre "khoa học kinh dị", voice Anh_Khoi 0.95, motion_mode meta_video, visual_style (bảng trên), premise, **characters[]+settings[]** (vài subject lặp), hashtags `#khoahockinhdi #...`.
3. **scenes.json** (`<slug>/ep01/scenes.json`, ~42–46 scene): mỗi scene = `{prompt EN, ref, narrator VN ~25–30 từ}`. Cấu trúc: HOOK (1–3 cảnh giật gân nhất) → thân bài (cơ chế/hành vi/lịch sử, mỗi fact 1–2 scene) → cao trào (twist/điểm yếu chết người) → kết + câu chốt ám ảnh.
4. **motions.json** (`<slug>/ep01/motions.json`, mảng theo display_order): **motion HÀNH ĐỘNG cụ thể** mô tả đúng việc đang diễn ra (bầy tràn tới, hàm xé mồi, kiến chúa đẻ…). ĐƠN GIẢN nhưng cụ thể — đừng để default zoom.
5. **Ref** (lần đầu, nếu có subject lặp): `python3 scripts/phim_gen_refs.py <slug>`. (Documentary phần lớn ref=null — xem VARIETY.)
6. **Gen ảnh** (Flow-free): `nohup python3 scripts/phim_produce_ep.py <slug> ep01 &` → img/scene_NN.jpg. Theo dõi `ls <ep>/img|grep -c scene_`.
7. **Gen clip + ghép** (local, KHÔNG Flow):
   ```bash
   nohup python3 scripts/meta_video_batch.py local phim/<slug>/ep01 &      # 45 clip Meta + motion
   python3 scripts/meta_assemble.py local phim/<slug>/ep01 Anh_Khoi_TTS 0.95
   ```
8. **Caption + registry:** `<ep>/caption.txt` (title + mô tả + hashtag) + ghi topic vào `plans/khkd-produced-topics.md`. (Logo KHKD 90px tuỳ chọn: `khkd_brand.py`.)

## 🎨 VISUAL VARIETY — luật quan trọng nhất (bài học từ v1 bị chê trùng)
> v1 kiến quân đội để 1 ref `bay_kien` lặp 16 scene + prompt generic → 6–7 cảnh bầy kiến + 3–4 cảnh cắn mồi GIỐNG HỆT → user chê "thiếu sáng tạo". Sửa:
- **Mỗi scene = 1 bố cục THỊ GIÁC khác hẳn**, kể cả khi narrator cùng chủ đề. Biến hoá: **cỡ cảnh** (macro cực cận ↔ aerial top-down ↔ wide), **góc** (top-down/nghiêng/thấp ground-POV/ngược sáng silhouette/cutaway), **chủ thể** (đổi con mồi cụ thể: muỗm/bọ cánh cứng/ếch/thằn lằn; thêm actor phụ), **bối cảnh** (nền rừng/thân cây/lá/suối/lều đêm/sân làng), **ánh sáng** (bình minh/hoàng hôn/trăng/đèn/backlit).
- **BỎ ref (`null`) cho hầu hết scene** — documentary không có "nhân vật" cần giữ mặt; `visual_style` đã khoá tông; null + prompt giàu chi tiết = ảnh ĐA DẠNG. (Ref chỉ khi cần subject lặp y hệt.)
- Trước khi gen: đếm ref/pattern; nếu lặp >3–4 lần → viết lại cho khác. [[feedback-phim-visual-variety]]

## Lỗi thường gặp
| Lỗi | Fix |
|-----|-----|
| Meta TỪ CHỐI ảnh (da/vết thương/trẻ em) | Đổi prompt: phong cách minh hoạ cổ/sepia, bỏ "wound/cut/blood", "young woman" thay "teenage" ([[reference-meta-image-skill]]) |
| Meta clip treo/timeout/từ chối 1 scene | **Escalation (theo thứ tự):** ①  Rerun batch (skip cái đã có). ② Đọc `meta_gen.log` — nếu có `META_CHAT_ERROR` Meta thường KÈM gợi ý ("try a different motion / create a new image from a different angle") → **LÀM THEO**: đổi motion trong motions.json + (nếu Meta khuyên) gen lại ảnh góc/prompt khác → retry. ③ Vẫn không được → **gen lại ẢNH với prompt khác hẳn** (Meta không animate nổi ảnh đó) + motion đơn giản → retry. ④ Cuối cùng mới fallback Ken Burns ffmpeg zoompan từ ảnh. |
| Clip tĩnh như "ảnh sống" | motions.json phải là HÀNH ĐỘNG cụ thể; chọn topic động vật/bầy (vốn động) hợp hơn người |
| Trùng chủ đề reel cũ | ĐỌC registry trước; ghi lại sau khi làm |
| Bịa số liệu | WebSearch verify; folklore ghi "từng được kể là" |
| 502 Flow / kẹt token | Pipeline đã FLOW-FREE (local mode) — không đụng Flow |

## Liên quan
[[reference-xuyen-khong-skill]] (engine /fk-phim + pipeline Flow-free) · [[feedback-phim-visual-variety]] · [[reference-meta-image-skill]] · [[reference-khkd-produced-topics-registry]] · `/fk-video-khkd-meta` (reel 40s, khác format).
