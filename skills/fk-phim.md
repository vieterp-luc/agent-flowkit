# fk-phim — Kể truyện thành phim long-form (storyteller ngôi 3) — ĐA THỂ LOẠI

Engine **chung** tạo video long-form **~5–6 phút/tập** kể truyện theo **ngôi thứ 3 điện ảnh** —
dùng cho **mọi loại truyện** (cổ trang VN, tiên hiệp/xianxia, ngôn tình, kiếm hiệp, hiện đại…).
**Ảnh tĩnh Meta (truyền ref nhân vật) + Ken Burns + lời kể liên tục.** Dọc 9:16, ~22–28 ảnh/tập.

> 🎯 **Mỗi bộ truyện = 1 CONTEXT riêng** lưu ở `output/phim/<story_slug>/story.json` (tên, thể loại,
> visual style, nhân vật + ref prompt, kế hoạch tập, voice, hashtag). Skill ĐỌC context này mỗi tập →
> **không sửa skill khi đổi truyện**. Truyện mới = tạo story.json mới.

Usage: `/fk-phim "<story_slug> Tập N — <mô tả/đoạn truyện>"`

> ⚠️ Ảnh Meta có **watermark + không commercial** → KHÔNG bật kiếm tiền YouTube. Monetize → đổi nguồn ảnh sang Flow Imagen (`/fk-gen-images`), giữ nguyên Ken Burns build.
> ⚠️ **Cần text truyện gốc** từng tập để viết script chính xác — KHÔNG bịa tình tiết. Không có text → dừng & hỏi.

## Default đã khoá (engine — không hỏi lại)
| Tham số | Giá trị |
|---------|---------|
| Định dạng | **Long-form ~5–6 phút/tập**, dọc 9:16 (720×1280), **~22–28 scene (1 ảnh/scene)** |
| Giọng | **`Nguyen_Ngoc_Ngan_TTS` · 0.95** (storyteller huyền thoại) — override per-story trong story.json |
| Chuyển động | **2 chế độ** (đặt `motion_mode` trong story.json): `ken_burns` (mặc định — zoom/pan ảnh tĩnh, nhanh ~5–10′) **hoặc** `meta_video` (animate mỗi scene thành clip Meta image→video — sống động, chậm ~1.5–2h/tập) |
| Ghép | `ken_burns` → **`phim_longform_build.py`** ; `meta_video` → gen clip **`meta_video_batch.py`** + ghép **`meta_assemble.py`** (kéo clip khớp lời kể + xfade) |
| Ảnh | **Meta AI** — text→image cho ref + **image→image truyền `--ref`** cho scene. Ép `"vertical 9:16 portrait format"` |
| Narrator | VN ~35–45 từ/scene, ngôi 3 trang trọng, kể liền mạch, bám sát text gốc |
| Logo | `khkd_brand.py` 90px góc dưới-phải |
| Output | `output/phim/<story_slug>/` |

## STORY CONTEXT — `output/phim/<story_slug>/story.json` (tạo 1 lần/truyện)
Khi bắt đầu một bộ truyện mới, tạo file context này; mọi tập đọc lại nó:
```json
{
  "title": "Tên truyện",
  "author": "Tác giả",
  "genre": "tiên hiệp | cổ trang VN | ngôn tình | kiếm hiệp | hiện đại …",
  "chapters": 1194,
  "voice": "Nguyen_Ngoc_Ngan_TTS", "speed": 0.95,
  "visual_style": "EN style string ép vào MỌI image prompt (xem bảng style bên dưới)",
  "characters": [
    {"key": "ten_nv", "name": "Tên NV", "ref_prompt": "EN mô tả NV base, vertical 9:16 portrait, no text"}
  ],
  "settings": [
    {"key": "ten_boi_canh", "name": "Tên địa điểm", "ref_prompt": "EN mô tả bối cảnh lặp lại (từ đường, làng, núi, đại điện…), vertical 9:16, no text"}
  ],
  "episode_plan": "vd: 20 tập × ~8 chương; hoặc season-based nếu truyện dài",
  "hashtags": "#... #..."
}
```

### Visual style theo thể loại (điền vào `visual_style`)
| Thể loại | Style string (EN) |
|----------|-------------------|
| **Cổ trang VN** | `cinematic historical drama, ancient Vietnam, authentic Vietnamese costume áo giao lĩnh, NOT Chinese hanfu, realistic, dramatic lighting, vertical 9:16, no text` |
| **Tiên hiệp / xianxia** | `cinematic Chinese xianxia cultivation, flowing Daoist robes, misty immortal mountains, glowing spiritual energy, ancient sect halls, ethereal, vertical 9:16, no text` |
| **Kiếm hiệp (wuxia)** | `cinematic wuxia, ancient Chinese martial world, robes, bamboo forests, inns, dramatic, vertical 9:16, no text` |
| **Ngôn tình hiện đại** | `cinematic modern romance drama, contemporary city, soft lighting, realistic, vertical 9:16, no text` |

## REF NHÂN VẬT + BỐI CẢNH — gen 1 lần bằng Meta, lưu `output/phim/<story_slug>/ref/`, dùng cả bộ
> Consistency = **gen ref 1 lần** (cả `characters[]` lẫn `settings[]`) rồi **truyền `--ref` vào Meta khi gen ảnh scene** (image→image).
>
> **Gen TẤT CẢ ref trong 1 lệnh** (đọc story.json, tuần tự, skip ref đã có):
> ```bash
> python3 scripts/phim_gen_refs.py <story_slug>       # vd: huyen_giam → gen mọi characters[]+settings[]
> ```
> Gen lẻ 1 ref (nếu cần làm lại): `python3 scripts/meta_image_gen.py "<ref_prompt + cinematic, vertical 9:16, no text>" output/phim/<story>/ref/<key>.jpg`
> Lưu ý: ref helper chỉ ghép **đuôi style sạch** (cinematic + 9:16), KHÔNG nhồi cả `visual_style` cảnh (tránh lẫn núi/đạo bào vào ảnh 1-chủ-thể).
> **Chọn ref cho mỗi scene (Meta image→image chỉ nhận 1 ref tốt):**
> - Scene **cận/trung nhân vật** → truyền ref **nhân vật** chính (ưu tiên — mặt quan trọng nhất).
> - Scene **đại cảnh/thiết lập địa điểm** (không có/ít nhân vật) → truyền ref **bối cảnh**.
> - Scene nhân vật TRONG bối cảnh lặp → ref nhân vật + **mô tả địa điểm trong prompt** (bám theo ref bối cảnh đã gen để tả nhất quán).

## Công thức 1 TẬP (~22–28 scene, mỗi scene 1 ảnh + ~12–18s lời kể)
> ⏱️ **Độ dài narrator theo motion_mode:** `ken_burns` → ~35–45 từ/scene thoải mái (ảnh tĩnh kéo bao lâu cũng được). `meta_video` → **~25–30 từ/scene** vì clip Meta chỉ ~5s, narrator dài làm meta_assemble kéo clip 1.5–2.2× (slow-mo trôi). Narrator dài hơn → tăng số scene thay vì kéo clip.
```
HOOK (1–2)   — cảnh giật gân/bí ẩn nhất tập + câu mở theo tông truyện
RECAP (1)    — (từ tập 2) nhắc nhanh chuyện trước
THÂN BÀI (18–22) — kể tuần tự diễn biến tập: mỗi tình tiết/đối thoại/bước ngoặt = 1–2 scene (bám text)
CAO TRÀO (2–3) — đỉnh điểm tập
KẾT + HOOK (1–2) — chốt + "Đón xem tập sau"
```

## Pipeline 1 tập — input gọn trong `scenes.json`, chạy bằng 3 script (resumable)
**Input chuẩn:** `output/phim/<story>/<ep>/scenes.json` = `{title, scenes:[{prompt, ref, narrator}]}` (prompt EN không cần kèm visual_style — producer tự ghép; `ref` = key trong `ref/` hoặc `null`; `narrator` VN). meta_video cần thêm `<ep>/motions.json` = mảng motion ĐƠN GIẢN theo display_order.

1. **Đọc `story.json` + text tập** (user cấp — KHÔNG bịa) → viết `scenes.json` (~22–28 scene) + (nếu `meta_video`) `motions.json`. Chọn `ref` mỗi scene: cận/trung NV → ref nhân vật; đại cảnh/thiết lập địa điểm → ref bối cảnh; cảnh mới → `null`.
2. **Ref (CHỈ lần đầu truyện):** `python3 scripts/phim_gen_refs.py <story>` → gen mọi `characters`+`settings` qua Meta → `output/phim/<story>/ref/<key>.jpg`. Tập sau dùng lại (bối cảnh mới → thêm vào `settings` + gen lúc đó).
3. **Gen ảnh scene** (FLOW-FREE — chỉ Meta, skip ảnh đã có):
   ```bash
   nohup python3 scripts/phim_produce_ep.py <story> <ep> &   # gen 22-28 ảnh Meta (+ref) → img/scene_NN.jpg
   ```
   Theo dõi: `ls <ep>/img | grep -c scene_` (stdout buffered).
4. **Ghép** (theo `motion_mode`) — tham số đầu = **`local`** → đọc narrator/motion từ JSON, **KHÔNG gọi Flow**:
   - `ken_burns`: `python3 scripts/phim_longform_build.py local phim/<story>/<ep> <voice> <speed>`.
   - `meta_video`: `nohup python3 scripts/meta_video_batch.py local phim/<story>/<ep> &` (gen clip Meta từ ảnh + motion; tuần tự ~1.5–2h, skip clip đã có; scene từ chối → fallback) → `python3 scripts/meta_assemble.py local phim/<story>/<ep> <voice> <speed>`.
   > 🔌 **BỎ FLOW:** narrator nằm trong `scenes.json`, motion trong `motions.json` (optional — thiếu thì dùng rotation zoom/pan mặc định). Loader `phim_scene_source.load("local", slug)` đọc trực tiếp → pipeline meta_video không còn đụng API Flow (hết kẹt token). `<vid> UUID` vẫn dùng được (path API cũ).
5. **Logo + caption + SEO:** logo RIÊNG mỗi truyện (`khkd_brand.py` chỉ là KHKD — ĐỪNG dùng cho truyện khác; huyen_giam chưa có logo → tạm bỏ logo) → `caption.txt` (title + mô tả + hashtag story.json) + `/fk-youtube-seo`.

## Checklist
```
[ ] story.json đã có (motion_mode đúng) + text tập này (KHÔNG bịa)
[ ] scenes.json (~22–28 scene: prompt/ref/narrator) (+ motions.json nếu meta_video)
[ ] (lần đầu) phim_gen_refs.py → output/phim/<story>/ref/
[ ] phim_produce_ep.py <story> <ep> → img/scene_NN.jpg (Flow-free, đủ scene)
[ ] Ghép theo motion_mode → final
[ ] logo RIÊNG truyện (đừng dùng logo KHKD) + caption.txt + /fk-youtube-seo
```

## Lỗi thường gặp
| Lỗi | Fix |
|-----|-----|
| Mặt nhân vật đổi giữa scene | Truyền **--ref** đúng nhân vật chính; giữ `ref/` cố định cả bộ |
| Meta bắt nhầm ảnh UI (rsrc.php) | `_image_srcs` đã lọc chỉ host `scontent-*` ([[reference-meta-image-skill]]) |
| Style sai thể loại (vd VN ra giống Trung) | Sửa `visual_style` trong story.json cho khớp thể loại; ép rõ trong mọi prompt |
| Ảnh không 9:16 | Thêm "vertical 9:16 portrait format" → Meta ra 810×1440 |
| TTS 422 | PATCH `narrator_text` trước |
| Meta gen ảnh/clip fail 1 scene | Re-run (`phim_produce_ep.py`/`meta_video_batch.py` skip cái đã có); đổi prompt/motion nếu bị từ chối ([[feedback-meta-chat-error-follow-suggestion]]) |
| Clip meta_video bị slow-mo trôi | Narrator quá dài → rút còn ~25–30 từ/scene HOẶC tăng số scene (motion đơn giản: "slow gentle zoom in" + chủ thể cụ thể) |
| Brand nhầm logo KHKD lên truyện khác | Mỗi truyện 1 logo riêng; chưa có → bỏ logo, đừng chạy `khkd_brand.py` |
| Muốn monetize | Đổi nguồn ảnh sang Flow Imagen, giữ Ken Burns build |

## Lấy text + script hàng loạt (nhiều tập)
- **Fetch text:** `python3 scripts/phim_fetch_chapters.py <story> "<url_with_{n}>" <start> <end>` — curl + UA trình duyệt (vượt 403/Cloudflare nhiều trang reader), trích `chapter-content`, lưu `source/chuong-NN.txt`. (vd thuviensachpdf.com OK.)
- **Registry 1 lần:** 1 subagent đọc cả bộ `source/chuong-*.txt` → `source/_registry.json` {characters[], settings[] (key+ref_prompt), chapters[] (summary+key_beats)}. Tạo `story.json` từ đây (visual_style theo thể loại + voice + motion_mode).
- **Fan-out script:** mỗi tập = 1 subagent đọc `chuong-NN.txt` → viết `epNN/scenes.json` (storyteller ~25-30 từ, ref keys từ registry). Chạy theo wave ~7 agent song song.
- ⚠️ **TEXT FILE là chân lý, KHÔNG phải registry summary:** registry chapters[] có thể **lệch số chương** (split/merge) → khi script từng tập, dặn agent **bám `chuong-NN.txt`, chỉ dùng registry để map NAME→ref key**. Sau đó verify keyword file vs nội dung tập (vài tập lệch thì rewrite).

## Truyện đã có context
| story_slug | Truyện | Thể loại | motion |
|------------|--------|----------|--------|
| `huyen_giam` | Huyền Giám Tiên Tộc (Quý Việt Nhân) | tiên hiệp | meta_video |
| `ngo_hai_tung_le` | Ngọ Hải Tụng Lễ (Phù Cẩn) | ngôn tình/healing | meta_video |

## Liên quan
[[reference-meta-image-skill]] · [[reference-meta-video-skill]] · `/fk-tom-tac-sach` · `/fk-van-vo` · reel ngắn 45s → `/fk-reel-whatif`.
