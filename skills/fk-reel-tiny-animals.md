# fk-reel-tiny-animals — Short ASMR "Chăm sóc động vật tí hon" bằng Meta AI

Tạo 1 reel **ASMR/thư giãn**: chăm một con vật **tí hon** (thật hoặc fantasy) theo cung
chăm-sóc cozy — **nhạc nhẹ + không lời** (no narration), macro miniature ấm áp. Đúng sweet
spot Meta AI video. 9:16, ~40–50s, 7 scene. Pipeline + nhạc nền đã chốt sẵn.

Usage: `/fk-reel-tiny-animals "<con vật>"`  (vd: "hamster tí hon", "rồng con lòng bàn tay")

> ⚠️ Clip Meta có **watermark + không commercial license** → dùng build view/thử nghiệm.
> Bản monetize nghiêm túc → dùng Veo. Xem [[reference-meta-video-skill]].

> 📁 **Output convention:** MỌI video vào `output/tiny_animals/<slug>/` (gọn, dễ quản lý).
> `tiny_produce.py` tự prefix `tiny_animals/`; chạy script lẻ thì truyền slug dạng
> `tiny_animals/<slug>` (vd `python3 scripts/meta_video_batch.py <vid> tiny_animals/<slug>`).

## Default đã khoá (không hỏi lại)
| Tham số | Giá trị |
|---------|---------|
| Tỉ lệ / độ dài | 9:16 (720×1280), ~40–50s, **7 scene** (slow 1.3× → mỗi clip dài hơn) |
| Âm thanh | **KHÔNG lời** — clip Meta im lặng + **1 lớp BGM cozy lặp** (`output/tiny_animals/_bgm/cozy.mp3`), volume 0.55, fade-out 2s |
| Ghép | scale 720×1280 + `setpts` slow 1.3× + **xfade 0.5s** (xem `scripts/tiny_assemble.py`) |
| Material ảnh | `realistic` |
| Trộn nội dung | **thật + fantasy** xen kẽ (hamster/mèo con thật · rồng con/voi tí hon fantasy) |
| Đồng bộ nhân vật | MỖI tập 1 entity nhân vật chính + ref image → `character_names` trên cả 7 scene → con vật **giống hệt** xuyên suốt ([[feedback-character-consistency-across-scenes]]) |
| Nhạc | MỖI tập 1 track riêng (field `music` trong episode) — gen bằng gemini standalone, vibe hợp con vật |

## Công thức 7 scene — cung "care routine" cozy (giữ retention bằng nhịp dịu)
```
S0 REVEAL  — con vật tí hon trong lòng bàn tay (hero shot, đẹp nhất)
S1 FEED    — cho ăn từ bát/đĩa tí hon
S2 BATHE   — tắm/chải lông nhẹ nhàng
S3 PLAY    — chơi đùa (leo, vờn bóng, sân chơi mini)
S4 HABITAT — pan chậm qua "nhà" miniature ấm cúng
S5 CUDDLE  — rúc vào đầu ngón tay người (âu yếm)
S6 SLEEP   — cuộn tròn ngủ trong giường tí hon (kết bình yên)
```

## Quy tắc nội dung
- **KHÔNG narrator** — đây là format ASMR. Cảm xúc đến từ hình + nhạc, không lời thoại.
- **Image + motion prompt = tiếng Anh.** Ép style:
  `adorable, cozy, macro miniature, soft warm lighting, shallow depth of field, photorealistic, vertical 9:16, no text, wholesome`.
- **Motion phải dịu & animate được từ ẢNH:** camera push-in/pan chậm + chuyển động mềm của
  con vật CÓ trong khung (sniff, blink, nibble, nuzzle, breathe). Tránh hành động phức tạp/nhanh.
  Nếu Meta trả `META_CHAT_ERROR "couldn't animate"` → đổi motion sang camera + cử động cực nhỏ,
  hoặc gen lại ảnh.
- **Né:** chữ trong khung, mặt người cận, cảnh động vật khổ/sợ (format phải wholesome, dễ thương).

## Prerequisites
- Server: `curl -s http://127.0.0.1:8100/health` (extension_connected + Flow credits ra số).
- Meta login 1 lần: `venv/bin/python scripts/meta_bootstrap.py`.
- BGM cozy có sẵn: `output/tiny_animals/_bgm/cozy.mp3` (đừng gen nhạc Gemini song song khi
  đang chạy pipeline — gemini browser dễ làm **kẹt server**).

## Pipeline (mỗi video ~20–40 phút máy chạy)

**Một lệnh (khuyến nghị):**
```bash
nohup python3 scripts/tiny_produce.py ep1 > /tmp/tiny.out 2>&1 &
# orchestrator: create project + 7 scene (NO narrator) → gen ảnh Flow → Meta video → ghép + nhạc
# poll output/tiny_animals/tiny_run.log ; episodes định nghĩa trong scripts/tiny_days.py
```

**Hoặc từng bước (debug / chủ đề mới chưa có trong tiny_days.py):**
1. **Viết 7 scene** theo cung care-routine: mỗi scene = image prompt EN + motion prompt EN (KHÔNG narrator). Thêm vào `EPISODES` trong `scripts/tiny_days.py`.
2. **Create project + 7 ROOT scene** (VERTICAL, realistic) — `tiny_produce.create_episode`. KHÔNG cần PATCH narrator (format không lời).
3. **Gen ảnh Flow** — batch nhỏ 3–4 (tránh reCAPTCHA), poll `done:true`, tải `output/tiny_animals/<slug>/img/scene_NN.jpg`. **Kiểm tra ảnh đứng 9:16, không xoay** trước khi sang Meta.
4. **Meta image→video:** `python3 scripts/meta_video_batch.py <video_id> tiny_animals/<slug>` (timeout 600, gap 30s; re-run để retry scene thiếu).
5. **Ghép + nhạc:** `python3 scripts/tiny_assemble.py tiny_animals/<slug>` → `output/tiny_animals/<slug>/<slug>_final.mp4`.

## Checklist
```
[ ] 7 scene care-routine (reveal→feed→bathe→play→habitat→cuddle→sleep), no narrator
[ ] Create project + 7 ROOT scenes (realistic, VERTICAL)
[ ] Gen ảnh Flow batch nhỏ → tải img/scene_NN.jpg → verify ảnh ĐỨNG
[ ] meta_video_batch.py → clips/scene_NN.mp4 (poll log, retry thiếu)
[ ] tiny_assemble.py (slow 1.3× + BGM cozy, no narration) → final
[ ] (tuỳ) CapCut thêm tiếng động ASMR khớp scene; /fk-gen-caption
```

## Lỗi thường gặp
| Lỗi | Fix |
|-----|-----|
| Ảnh ngang/xoay 90° | Flow glitch → REGENERATE_IMAGE; video sẽ theo ảnh nên phải sửa ảnh trước |
| Meta `couldn't animate` | motion mô tả thứ không có trong ảnh / quá phức tạp → đổi sang camera + cử động nhỏ |
| Meta `VIDEO_TIMEOUT` | timeout 600 + reload-capture (xem `/fk-gen-meta-video`) |
| reCAPTCHA khi gen ảnh | batch nhỏ 3–4; giãn cách giữa các video; dính rồi → user giải captcha trong tab Flow, regen 1 ảnh/lần |
| Server treo (rỗng) sau khi gen nhạc | gemini browser kẹt event loop → kill + restart server, dùng `cozy.mp3` có sẵn (đừng gen nhạc song song) |

## Ý tưởng chủ đề (kho)
**Thật:** hamster · mèo con · cún con · thỏ con · chuột lang · nhím con · vịt con · chim non.
**Fantasy:** rồng con · voi tí hon · kỳ lân mini · phượng hoàng con · griffin baby · slime thú cưng.
Mẹo: xen kẽ 1 thật – 1 fantasy để kênh đa dạng.

## Lỗi thường gặp (bổ sung)
| Lỗi | Fix |
|-----|-----|
| `PUBLIC_ERROR_PER_MODEL_DAILY_QUOTA_REACHED` | Quota gen ảnh theo NGÀY của account cạn (KHÁC "credits"). ~20-25 ảnh/ngày là cạn. Fix: **đổi account Flow khác** (quota theo account) hoặc chờ reset (~nửa đêm Pacific). Đồng bộ nhân vật vẫn giữ qua đổi account (ref media_id còn hạn). |
| Meta gen scene ra 4 biến thể / ảnh tĩnh thay vì 1 clip | Tạo lại riêng clip đó: `POST /api/meta/browser/generate-video` với ảnh + motion prompt sạch (thêm "gentle camera push-in"). |

## Đã làm
| Video | Kind | Đồng bộ | Nhạc | OUTDIR |
|-------|------|---------|------|--------|
| hamster tí hon | real | ✗ (pilot đầu) | cozy_playful | `output/tiny_animals/tiny_hamster` (7/7, 44.5s) |
| rồng con tí hon | fantasy | ✓ | dragon_glow | `output/tiny_animals/tiny_baby_dragon` (7/7, 44.5s) |
| mèo con tí hon | real | ✓ | kitten_play | `output/tiny_animals/tiny_kitten` (7/7, 44.5s) |
| voi tí hon | fantasy | ✓ | elephant_calm | `output/tiny_animals/tiny_mini_elephant` (7/7, 44.5s) |
