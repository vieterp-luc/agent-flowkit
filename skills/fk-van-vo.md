# fk-van-vo — Tóm Tắt Văn Học Phong Cách "Văn Vở" (Gen Z Slang)

Long-form chapter-by-chapter video tóm tắt tác phẩm văn học VN/foreign theo phong cách kênh **Văn Vở** —
slang Gen Z + internet meme + chương đặt tên phim bom tấn + ads hài + đắc nhân tâm chốt cuối.

**Tone:** "Lầy lội nhưng nhân văn". Kể trung thành cốt truyện nhưng dán nhãn nhân vật/sự kiện qua lăng kính internet 2020s.
**Format mặc định:** chapter-by-chapter (mỗi chương / arc lớn = 1 video 10-15 min), 11-15 scenes.
**Voice mặc định:** `Thang_QC_TTS` @ speed `0.9` — locked sau demo test trên Sơn Tinh Thủy Tinh. Không A/B nữa trừ khi user explicit override `--voice`.
**Output:** local-only — `output/van_vo/<book_slug>/ep<NN>/` (centralized under van_vo/ for management) — upload defer v2.

Khác biệt với `/fk-tom-tac-sach` (cùng long-form VN nhưng tone nghiêm túc):
- Script: slang dictionary + commentary "vô tri" — **NO ad break** (user explicit rejected)
- Chapter name: map sang title phim bom tấn (Fight Club / Endgame / No Way Home...)
- Image: nhân vật phiên bản "boi phố" (oversized hoodie, undercut moi, sneakers) trên nền classical
- Voice: locked Thang_QC_TTS @ 0.9 (trẻ năng lượng cao, A/B'd qua Sơn Tinh demo)
- Ken Burns motion: face-safe rule (static/pan/zoom_out cho character scenes, zoom_in only cho atmospheric)

Usage:
```
/fk-van-vo                                    # status dashboard
/fk-van-vo --detail                           # per-book/per-ep breakdown
/fk-van-vo --next                             # 3 next actions
/fk-van-vo --batch <slug> <range>             # produce + build batch

# Bootstrap:
/fk-van-vo "Dế Mèn Phiêu Lưu Ký"              # auto-detect fiction → chapter format
/fk-van-vo "Số Đỏ" --episodes 20              # override episode count

# Voice override (default Thang_QC_TTS @ 0.9 — không cần A/B nữa):
/fk-van-vo <slug> --voice <name> --speed 0.9
```

## Production Pipeline (automated)

Pipeline module: `scripts/vanvo_render_pipeline.py` + `scripts/vanvo_books_data.py`.

```bash
python scripts/vanvo_render_pipeline.py            # batch all books in BOOKS dict
python scripts/vanvo_render_pipeline.py <slug>     # single book
```

Pipeline auto-handles: project create → 15 scenes (intro+14) → batch image gen → TTS → Ken Burns → concat → mix → thumbnail + caption. Resumable via `_project.json` marker.

To add new book: **STEP 1 — define character constants** at top of book block (see "Character Consistency Rule" below), THEN append to `BOOKS` dict in `vanvo_books_data.py` with fields: slug, title, story_summary, scripts[14], image_prompts[14] (built via f-string referencing constants), motions[15], caption_hook/bullets/moral.

---

## Data Sources

| File | Purpose |
|------|---------|
| `output/_shared/van-vo-roadmap.json` | All books + chapter/movie-title map + voice + ad slots |
| `output/_shared/tts_templates/templates.json` | Available Vietnamese voices |
| `output/van_vo/<book_slug>/ep*/` | Built episode dirs (centralized under van_vo/) |
| `scripts/vanvo_books_data.py` | All book configs (scripts + image prompts + motions) |
| `scripts/vanvo_render_pipeline.py` | Automated pipeline module |

Separate roadmap from `tom-tac-sach-roadmap.json` — different tone/format/audience.

---

## Default Workflow (status dashboard)

Same skeleton as `/fk-tom-tac-sach` — load roadmap, count built eps, output 1-screen summary. Don't duplicate logic here.

Dashboard format:
```
🎤 VĂN VỞ  —  Status @ <today ICT>

📚 Active: <Book> (<Author>) — <built>/<total> tập đã build
   ├─ Voice:         Thang_QC_TTS @ 0.9 (locked default)
   ├─ Aesthetic:     vanvo_modern
   ├─ Chapter map:   <N> chương → movie-title mapped
   └─ Slang density: ~1 term/scene (locked threshold)

📅 Backlog:
   ep<N>: <Ch.X — "Movie Title (Year)"> e.g. "Fight Club (1999)"
   ep<N+1>: ...

🎯 NEXT:
   1. ...
   2. ...

📖 Books trong roadmap:
   ✅ <slug> (in_progress, <done>/<total>, voice=<locked>)
   ⚠️  <slug> (voice A/B pending)
   ⏳ <slug> (planned)
```

Decision tree:
1. Backlog > 0? → Suggest `--batch <slug> <range>`
2. All built? → Suggest book mới

---

## Bootstrap New Book

### Step 0 — Copyright + suitability check

Same PD rules as `/fk-tom-tac-sach` Step 0. Văn Vở style fits BEST với:
- Truyện thiếu nhi/phiêu lưu có nhân vật phi-người (Dế Mèn, Truyện Cổ tích)
- Tiểu thuyết hiện thực có nhân vật mưu mẹo (Số Đỏ, Tắt Đèn)
- Sử thi/anh hùng ca có combat (Truyện Kiều fight scenes, Tây Du Ký)
- Truyện ngắn có twist (Lão Hạc, Chí Phèo, Vợ Nhặt)

KHÔNG phù hợp:
- Thơ trữ tình thuần (Tản Đà, Nguyễn Bính lyric)
- Triết học (Nhật Ký Trong Tù — mood sai)
- Self-help (không có nhân vật để slang hóa)

### Step 1 — Chapter → Movie title mapping

Skill prompts Gemini với system instruction:
```
Map từng chương/arc của <book> sang 1 tên phim bom tấn Hollywood/quốc tế
có chủ đề/nội dung tương đồng. Format:
{
  "ep": 1,
  "chapter_original": "Chương 1: Tôi sống độc lập",
  "movie_title": "The Pursuit of Happyness (2006)",
  "rationale": "Cả 2 đều là arc 'self-made độc lập tuổi trẻ'"
}
```

Tham khảo bản map cho **Dế Mèn Phiêu Lưu Ký** (canonical reference):
| Ch | Movie Title | Theme |
|----|-------------|-------|
| 1 | The Pursuit of Happyness (2006) | Ra ở riêng, tự lập |
| 2 | Fight Club (1999) | Đánh nhau với Dế Choắt arc |
| 3 | Spider-Man: No Way Home (2021) | Trở về sau biến cố |
| 4 | The Revenant (2015) | Bị bắt, sống sót |
| 5 | The Hangover (2009) | Phiêu lưu hỗn loạn cùng Dế Trũi |
| 11 | Avengers: Endgame (2019) | Đại chiến cuối — kiến vs châu chấu |

User review map → adjust if mismatched → save vào roadmap.

### Step 2 — Aesthetic profile

Single preset: `vanvo_modern`. Không có alternative — đặc trưng của brand.

```
vanvo_modern preset (validated qua Sơn Tinh + Dế Mèn samples):
Modern Vietnamese street fashion x classical literature setting hybrid,
nhân vật phiên bản "boi phố" 2020s:
- Mặc: oversized hoodie / áo khoác bomber, jeans rách, sneakers (Air Force 1, Yeezy slide),
  hoặc áo polo + quần short streetwear — SOLID COLOR ONLY, no graffiti, no printed pattern, no logo
- Tóc: undercut, moi style (hai bên cạo, đỉnh dài), tóc nhuộm bạch kim / bordeaux / xanh
- Phụ kiện: dây chuyền vàng cỡ lớn, kính mát aviator, đồng hồ Casio, AirPods Pro
- Bối cảnh: vẫn giữ era gốc (làng quê 1930s / cung đình 19th c) NHƯNG nhân vật anachronistic streetwear
- Style: anime/manhwa Hàn Quốc colored, vibrant neon palette, dramatic rim lighting,
  comic book panel framing, dynamic action poses
- Pose: NATURAL confident stance (hands in pockets, leaning, walking, sitting squat)
  — AVOID gym flex pose, AVOID bodybuilder arm pose, AVOID muscle pose
- Mood: ironic juxtaposition — boi phố walking through áo nâu sòng làng cảnh
- Palette lock (series consistency): cyan + gold + neon magenta accent
- STRICTLY NO TEXT in image, NO logos, NO graffiti/printed letters on clothing, NO subtitles
- VERTICAL/HORIZONTAL per video orientation
```

Side note: với nhân vật phi-người (Dế Mèn = côn trùng), apply anthropomorphic-streetwear — humanoid body + giữ đặc trưng loài (râu, mắt to, body color), trang phục SOLID COLOR (no graffiti/print), pose tự nhiên không gym flex. Vd Dế Mèn: hoodie đen solid + cargo shorts + chunky sneakers + gold chain + aviator sunglasses + tóc bạc moi, pose ngồi xổm hàng rào.

### Step 3 — Create Flow project

```bash
POST /api/projects
{
  "name": "<Book slug>_VanVo",
  "description": "Tóm tắt <Book> phong cách Văn Vở — Gen Z slang + modern hybrid visuals.",
  "story": "<2-3 câu giới thiệu sách + bối cảnh + dòng chữ 'aesthetic vanvo_modern hybrid'>",
  "material": "realistic",
  "image_style": "Modern Vietnamese street fashion hybrid với era gốc của tác phẩm. Anime/manhwa Korean color, vibrant cyan + gold + neon magenta palette, dramatic rim lighting, comic book panel framing. Clothing SOLID COLOR ONLY — no graffiti, no printed pattern, no logo, no letters. Natural confident pose — AVOID gym flex/bodybuilder/muscle pose. STRICTLY NO TEXT, NO subtitles, NO signs. HORIZONTAL 16:9 cinematic.",
  "language": "vi",
  "orientation": "HORIZONTAL"
}
```

### Step 4 — Character Bible (MANDATORY — đồng bộ xuyên suốt mạch truyện)

**Rule cốt lõi:** mỗi nhân vật/quái vật/địa điểm có tên = 1 constant string DUY NHẤT, định nghĩa MỘT LẦN ở đầu book block trong `vanvo_books_data.py`, reuse qua f-string trong MỌI scene image_prompt. **Không bao giờ re-describe** trong từng scene riêng.

Pattern (canonical, xem `vanvo_books_data.py` THẠCH SANH / TẤM CÁM):
```python
# ===== BOOK X: <TÊN> =====
THACH_SANH = _char("Thạch Sanh", "young Vietnamese man, kind orphan hero: brown cargo shorts + cream solid hoodie no print, white sneakers, gold chain, undercut blonde hair, gentle confident face")
LY_THONG   = _char("Lý Thông",   "middle-aged scheming Vietnamese man: black bomber jacket solid no print + dark jeans, aviator sunglasses, slick black hair, sly smirk")
CONG_CHUA  = _char("Princess công chúa", "...")
# ... rồi mới đến THACH_SANH_BOOK = {...}
```

Constant string PHẢI lock đủ visual identifiers (audience cần nhận ra nhân vật khắp 14 scene):
1. **Age + build** ("young / middle-aged / elderly", "tall thin / stocky")
2. **Clothing** — top + bottom + footwear, SOLID COLOR (vd "cream solid hoodie no print + brown cargo shorts + white sneakers")
3. **Hair** — style + color (vd "undercut blonde / slick black / silver bun")
4. **Signature accessory** — gold chain / aviator sunglasses / Apple Watch / hair pin
5. **Default expression / pose tag** ("gentle confident face" / "sly smirk" / "scolding angry hands on hips")

Mỗi scene image_prompt build qua f-string interpolation, KHÔNG copy-paste description:
```python
# ĐÚNG ✅
f"Village marketplace scene: {LY_THONG} approaching {THACH_SANH} with fake friendly grin..."

# SAI ❌ — re-describe → drift visual
f"Village scene: Lý Thông (middle-aged man in blue jacket) approaching Thạch Sanh (young man in green shirt)..."
```

5-8 nhân vật chính + 2-3 quái vật/sinh vật + 1-2 địa điểm signature. Personality slang tag (boi phố / idol quốc dân / ông trùm / scammer) ghi vào commentary trong narrator, KHÔNG ghi vào constant (constant = thuần visual).

**Variant rule:** khi story cần nhân vật thay outfit (vd Sọ Dừa head → handsome man, hoặc cưới hỏi áo cưới), define `<NAME>_VARIANT = _char(...)` riêng — KHÔNG mutate constant gốc. Vd `SO_DUA_HEAD` vs `SO_DUA_MAN` trong book 2.

Pause cho user review roster + visual lock trước khi viết image_prompts.

### Step 5 — Gen reference images (optional, spot-check only)

Pipeline thực tế (`scripts/vanvo_render_pipeline.py`) **không** dùng Flow entity ref system — character consistency 100% relies on constant-reuse pattern Step 4. Nếu muốn pre-validate 1 character trước khi render full episode: gen ảnh test với constant string riêng → spot-check → adjust constant nếu drift, RỒI mới mass batch 14 scenes.

### Step 6 — Extract chapter map + slang assignment

Per chapter, Gemini extract:
```json
{
  "ep": 1,
  "movie_title": "...",
  "key_events": ["...", "..."],
  "slang_tags_per_event": {
    "event_1": ["tân thủ", "gói bảo hộ tân thủ"],
    "event_2": ["combat", "wombo combo"]
  },
  "moral_wrap_up": "Bài học: ..."
}
```

Map vào roadmap entry.

### Step 7 — Register trong roadmap

```json
{
  "active_book": "<slug>",
  "books": {
    "<slug>": {
      "title": "...",
      "author": "...",
      "voice": "Thang_QC_TTS",
      "speed": 0.9,
      "aesthetic_preset": "vanvo_modern",
      "slang_density": "high",
      "flow_project_id": "...",
      "local_dir": "output/<slug>_vanvo",
      "total_episodes": <N>,
      "status": "in_progress | done",
      "chapter_map": [
        {"ep": 1, "movie_title": "...", "key_events": [...], "slang_tags_per_event": {...}, "moral_wrap_up": "..."}
      ],
    }
  }
}
```

### Step 8 — Suggest first batch

```
🎉 <Book> bootstrapped (Văn Vở style).
   Chapter map: ✅ <N> chương mapped to movie titles
   Wave 1: ✅ <N> entities (boi phố hybrid)
   Voice: Thang_QC_TTS @ 0.9 (default)

🎯 NEXT:
   1. Build batch: /fk-van-vo --batch <slug> 1-5
   2. Test 1 ep trước → review flow + slang density → adjust nếu cần
```

---

## --batch Workflow (produce + build)

```
/fk-van-vo --batch <slug> <start>-<end>
```

Per ep:

### Stage 1: Script generation (Gemini in-skill, NOT backend yet)

System instruction template cho Gemini call:
```
Bạn viết kịch bản cho video YouTube tóm tắt văn học phong cách kênh "VĂN VỞ".

INPUT:
- Sách: <title>, tác giả <author>
- Chương <X>: <chapter_original_name> (mapped → "<movie_title>")
- Key events: <list>
- Slang tags assigned: <map>
- Moral wrap-up: <text>

CONSTRAINTS:
- **Scene 0 (INTRO — MANDATORY first scene):** narrator = "Chào mừng anh em đến với seri cổ tích thời gen z." image_prompt = branding intro card storybook + magical neon swirls. Motion = static.
- **Hook (2 scenes max, 25-35s tổng):** Scene 1 = greeting + giới thiệu truyện (~40-50 từ). Scene 2 = plot tease nhanh (~40-50 từ). Hook TRÁNH English slang dày (no "main character energy", "combat hero" etc) — VN-leaning: dân chơi, drama, lầy lội.
- **KHÔNG dùng câu "Câu chuyện này giải nén kiểu phim..." trong bất kỳ scene nào** — movie title mapping chỉ dùng nội bộ (`chapter_map.movie_title` cho image_prompt poster scene + thumbnail), KHÔNG đề cập trong narrator text. Audience không cần biết mapping → narrator tập trung kể truyện thuần Việt.
- **Body (11 scenes):** mỗi scene 3-5 câu (60-100 từ) — kể CHI TIẾT. **PHẢI bao gồm iconic phrases verbatim** khi có (vd "Đàn kêu tích tịch tình tang, ai mang công chúa dưới hang trở về" / "bống bống bang bang lên ăn cơm vàng cơm bạc" / "khắc nhập khắc nhập" / "ăn một quả trả một cục vàng"). Cho phép >100 từ nếu cần chỗ cho iconic phrase.
- Scene duration target 15-30s/scene → total video 5-15 min long-form
- NO AD BREAK scene
- Scene 1 (Hook, ~1 min = 3 narrator sentences):
  - Mở bằng nhận xét "giang hồ" hoặc so sánh xã hội hiện đại
  - Dán title "<movie_title>" như poster phim
- Scene 2-3 (recap "Previously" — SKIP nếu ep1)
- Scene 4-12 (Body, 8-9 scenes):
  - Kể trung thành sự kiện
  - Bắt buộc dùng slang tag được assign mỗi 1-2 câu
  - Chèn 1-2 câu commentary "vô tri" mỗi scene (tone hài, không quá dài)
  - Time connectors: "Đầu tiên / Sau đó / Bỗng nhiên / Trong lúc đó / Cuối cùng"
- Scene 13 (Climax/resolution event ~1 scene)
- Scene 14 (Moral wrap-up "Thuật đắc nhân tâm", 2-3 narrator sentences):
  - Chốt bài học cuộc sống nghiêm túc
  - Tone shift: từ lầy lội → sâu sắc
  - Format: "Câu chuyện <chương> dạy ta rằng... <bài học>. Đây không chỉ là <slang reference> mà còn là <giá trị nhân văn>."

SLANG DICTIONARY — RULE: density ~1 slang/scene (max). Quá dày → "cringe overload". Audio scene Moral wrap-up = 0 slang.

ALLOWED (mainstream VN, phổ thông hiểu ngay):
- Nhân vật: boi phố chính hiệu, dân chơi, idol quốc dân, ông trùm
- Combat: combat, combo, hành gà, nắc cho thân tàn ma dại
- Exit/thua: AFK, đành chịu thua, hàng tạm, đăng xuất
- Psychological: tâm lý vỡ vụn, sang chấn, cười xỉu, đứng hình
- Scam/lừa: scam, lừa đảo trắng trợn
- Locations: biệt thự triệu đô, view thoáng đét, tã, lầy lội
- Status: flex, lú, cực kỳ bá

BANNED (niche/cringe / user explicit reject — KHÔNG dùng):
khét lẹt, siêu phèn, đại boss,
PTSD, NPC, OP, top server, inventory full, one-shot, ez game, wombo combo,
gank, GG, full bão tố, nerf, buff, stun, tutorial mode, gói bảo hộ tân thủ,
main character energy, mid, trauma dump

FLOW RULE — narrator text phải đọc tự nhiên, KHÔNG over-chop:
- `?` chỉ khi câu hỏi GENUINE (không rhetorical)
- `!` chỉ khi cảm thán climax thật (không cho từng câu đơn)
- `—` em-dash max 1-2/scene, dùng cho định danh ("Mị Nương — idol quốc dân")
- `...` ellipsis chỉ khi suspense thật, không filler
- Mặc định dùng `,` `.` cho nhịp tự nhiên
- Total special punctuation max 2/scene
- Anti-pattern: "Tâm lý vỡ vụn. PTSD nặng. Nuôi hận muôn đời." (chặt vụn)
- Đúng: "tâm lý vỡ vụn, sang chấn nặng nề, nuôi hận muôn đời" (gộp liền)

OUTPUT JSON:
[
  {
    "scene": 1,
    "narrator_text": "...",
    "scene_prompt": "<image prompt theo aesthetic vanvo_modern, mô tả cảnh + nhân vật hybrid streetwear>",
    "is_ad": false,
    "is_moral_wrap_up": false
  },
  ...
]
```

### Stage 2: Create video + scenes in Flow

Standard `POST /api/videos` + scenes append.

### Stage 3: Mass batch GENERATE_IMAGE

Standard. Aesthetic preset đã set ở project level.

### Stage 4: Per-ep audio + concat

- TTS: `Thang_QC_TTS` @ speed=0.9 (locked default), volume 1.5×
- Music: **NONE** (user explicit reject — no BGM, narrator-only mix)
- Ken Burns motion (FACE-SAFE — DEFAULT static, only deviate when img composition supports it):
  - DEFAULT all scenes: `static` (safest, never crops)
  - `zoom_in`: ONLY atmospheric/landscape scenes (NO characters at all)
  - `zoom_out`: wide reveal scenes / magical reveals (safe — starts close ends wide)
  - `pan_*`: ONLY if composition matches direction (char đi từ trái → phải = pan_right OK; tránh nếu char ở edge cùng direction)
  - **AVOID `zoom_in` + `pan_*` cho bất kỳ scene character static-pose** (crops face)
  - Variety < Safety. Khi nghi ngờ → static.
- Concat → `output/van_vo/<slug>/ep<NN>/ep<NN>_final.mp4`
- Narrator concat: 1.0s silence between scenes (fits well-paced Ken Burns motion buffer)
- NO brand overlay (v1, local-only)

### Stage 5: Thumbnail + Caption (MANDATORY)

**Thumbnail** (1280×720, ffmpeg drawtext — no ImageMagick):
- Base: `scene_02.png` (movie-poster style — best base)
- Top bar text: "SERI CỔ TÍCH THỜI GEN Z" cyan #00f0ff, 48pt
- Bottom bar text: "<TÊN TRUYỆN>" gold #ffd700, 140pt
- Semi-transparent dark bars (0.55/0.65 opacity) for legibility
- Font: `/Library/Fonts/Arial Unicode.ttf` (full Vietnamese diacritics)
- Output: `thumbnail.png`

```bash
ffmpeg -y -i scene_02.png -vf "
scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,
drawbox=x=0:y=0:w=1280:h=170:color=black@0.55:t=fill,
drawbox=x=0:y=550:w=1280:h=170:color=black@0.65:t=fill,
drawtext=fontfile='/Library/Fonts/Arial Unicode.ttf':text='SERI CỔ TÍCH THỜI GEN Z':fontcolor=#00f0ff:fontsize=48:x=(w-text_w)/2:y=58:shadowcolor=black:shadowx=3:shadowy=3,
drawtext=fontfile='/Library/Fonts/Arial Unicode.ttf':text='<TÊN TRUYỆN>':fontcolor=#ffd700:fontsize=140:x=(w-text_w)/2:y=580:shadowcolor=black:shadowx=4:shadowy=4
" -frames:v 1 -update 1 thumbnail.png
```

**Caption** (`caption.txt`):
- Header: `🎬 SERI CỔ TÍCH THỜI GEN Z — <TÊN TRUYỆN> 🎬`
- Hook 1-2 câu Gen Z slang grabbing attention
- Bullet "Trong tập này" liệt kê 5-7 plot points hấp dẫn
- Closing CTA "Theo dõi để nghe tiếp series..."
- Hashtags: `#cotich #<book> #vanhoc #vietnam #genzliterature #vanvo #vietnamesefolktale #podcast`

---

## Pipeline Standard (locked defaults)

| Setting | Value |
|---------|-------|
| Default voice | `Thang_QC_TTS` (locked from Sơn Tinh demo) |
| Default speed | 0.9 (down from initial 0.95 — user feedback prefers slower) |
| Narrator length | 3-5 câu/scene (60-100 từ) — kể CHI TIẾT có dialogue + magical phrases; NOT 1-câu tóm tắt |
| Resolution | 1920×1080 HORIZONTAL (long-form default) |
| FPS | 30 |
| TTS volume | 1.5× |
| Background music | **DISABLED** (user explicit reject — narrator-only audio) |
| Scene count | 11-14 per ep (Hook=1-3 + Recap=0-2 + Body=8-9 + Moral=1-2) — NO ad break |
| Ad break | **REMOVED** (user explicit reject) |
| Moral wrap-up | Mandatory (non-negotiable — defining feature) |
| Aesthetic | `vanvo_modern` only (no alternatives) |
| Image text policy | STRICTLY NO TEXT (defensive prompt from memory) |
| Brand overlay | OFF (v1 local-only) |

---

## Slang Dictionary (Quick Reference — Mainstream Only)

**Rule khắc: max 1 slang/scene. Moral wrap-up = 0 slang.** Source-of-truth là threshold lưu trong memory `feedback-van-vo-slang-threshold.md`.

ALLOWED:
| Concept | Slang |
|---------|-------|
| Nhân vật chính tự tin | boi phố chính hiệu, dân chơi |
| Nhân vật quyền lực | idol quốc dân, ông trùm |
| Đánh nhau | combat, combo |
| Thắng dễ dàng | hành gà, ngon ơ, một phát ăn ngay |
| Đánh tàn nhẫn | nắc cho thân tàn ma dại |
| Chết/thua/rút lui | AFK, đành chịu thua, hàng tạm, đăng xuất |
| Bị choáng | đứng hình, cười xỉu |
| Trauma | tâm lý vỡ vụn, sang chấn nặng nề |
| Bị lừa | scam, lừa đảo trắng trợn |
| Nhà giàu | biệt thự triệu đô, view thoáng đét |
| Nhà nghèo | tã, lầy lội |
| Khoe khoang | flex |
| Trạng thái | lú, cực kỳ bá |

BANNED (KHÔNG dùng — user explicit reject + niche/cringe):
**khét lẹt, siêu phèn, đại boss** (rejected 2026-05-19 — overused/cringe trong các book trước),
PTSD, NPC, OP, top server, inventory full, one-shot, ez game, wombo combo,
gank, GG, full bão tố, nerf, buff, stun, tutorial mode, gói bảo hộ tân thủ,
main character energy, mid, trauma dump, phishing.

---

## Movie Title Mapping (Reference Patterns)

Common arc → movie suggestion (Gemini extends khi bootstrap):

| Arc pattern | Suggested movies |
|-------------|------------------|
| Origin / coming of age | Batman Begins, X-Men: First Class, Spider-Man: Homecoming, Lady Bird |
| Self-discovery độc lập | The Pursuit of Happyness, Eat Pray Love, Wild |
| First fight / training | Karate Kid, Rocky, Fight Club, Cobra Kai |
| Adventure khởi đầu | The Hobbit, LOTR: Fellowship, Pirates of Caribbean |
| Bị bắt / khủng hoảng | The Revenant, 127 Hours, The Shawshank Redemption |
| Trở về | Spider-Man: No Way Home, LOTR: Return of King, Homeward Bound |
| Phản bội | The Godfather, Game of Thrones (Red Wedding), Star Wars: Revenge of Sith |
| Tình yêu | La La Land, Titanic, Eternal Sunshine, Notebook |
| Đại chiến cuối | Avengers: Endgame, Star Wars: Rise of Skywalker, LOTR: Return of King |
| Phiêu lưu hỗn loạn | The Hangover, Inception, Mad Max: Fury Road |
| Tragedy | A Star Is Born, Schindler's List, Manchester by the Sea |
| Heist / mưu mẹo | Ocean's 11, Catch Me If You Can, The Sting |
| Twist ending | The Sixth Sense, Shutter Island, Gone Girl |

Năm phát hành phải accurate — checked qua web nếu cần. Gemini có thể hallucinate năm.

---

## Voice (Locked)

Default: `Thang_QC_TTS` @ speed `0.9`. A/B'd qua Sơn Tinh Thủy Tinh demo (`output/_demo/vanvo_son-tinh_thang-qc_v5.wav`).

Override per book (rare): `/fk-van-vo <slug> --voice <name> --speed 0.9`. Phải có lý do (vd nhân vật nữ chính → cần voice nữ Hong_Hanh_podcast_TTS).

---

## Common Errors

| Error | Fix |
|-------|-----|
| Slang quá dày → text quá dài > 22 từ | Drop slang xuống max 1/scene, re-extract |
| Slang dùng từ BANNED list | Re-extract với constraint mạnh hơn về dictionary |
| Narrator TTS ngắt giật cục | Check punctuation — bỏ `?!—...` thừa, gộp câu bằng `,` |
| Image gen ra text (chữ hoodie, biển hiệu) | Defensive prompt "STRICTLY NO TEXT" + "SOLID COLOR clothing only" — nếu vẫn ra graffiti giả, regen với prompt nhấn mạnh hơn |
| Nhân vật đổi outfit/màu tóc/mặt giữa các scene (character drift) | Re-check `vanvo_books_data.py`: nhân vật ĐÃ ĐƯỢC define thành constant ở đầu book block chưa? Mọi image_prompt liên quan ĐÃ dùng `{CONSTANT}` interpolation chưa? Nếu chưa → refactor về pattern Step 4 ngay, regen scene affected. KHÔNG re-describe nhân vật inline. |
| Cần nhân vật mặc outfit khác cho 1 scene đặc biệt (vd áo cưới, biến hình) | Define `<NAME>_VARIANT = _char(...)` constant mới (vd `SO_DUA_HEAD` vs `SO_DUA_MAN`), KHÔNG mutate constant gốc. Reference variant chỉ trong scene đó. |
| Image gen ra pose gym flex/bodybuilder | Add "natural confident stance, hands in pockets / leaning / walking, AVOID muscle pose" |
| Clothing có graffiti pattern ngẫu nhiên | Re-prompt: "clothing solid color only, no print, no graffiti, no graphic" |
| Image gen sai hybrid (full classical OR full modern) | Re-prompt explicit: "Character wears 2020s streetwear, background remains <era>" |
| Movie title hallucinated năm sai | Web search verify trước khi save roadmap |
| Moral wrap-up tone vẫn lầy lội (không shift được) | Manual edit narrator_text scene cuối, Gemini sometimes fails tone shift |
| Ken Burns zoom_in crop mặt nhân vật | Đổi sang `static` (portrait/close-up) / `pan_*` (medium) / `zoom_out` (wide). zoom_in chỉ dùng cho atmospheric no-character scenes |
| Ad break placeholder vẫn xuất hiện trong script | Re-prompt Gemini với explicit "NO AD BREAK scene" — user rule absolute |

---

## Pre-flight Checks (Flow quota safety)

Before --batch (Flow quota safety from memory):
1. Check `extension_connected: true`
2. Pre-flight credits qua `/api/account/credits` — abort nếu insufficient
3. Probe 1 scene image gen trước batch — abort nếu QUOTA error
4. Halt worker auto-retry on QUOTA / no-operations errors

Same pattern as `/fk-podcast-book` and `/fk-tom-tac-sach`.

---

## Backend Extension (v1.1+, deferrable)

Skill v1 dùng Gemini in-skill cho script gen (không cần backend extend).

V1.1 (nếu sản xuất scale > 5 books): extend `agent/services/book_script_writer.py` với
`write_chapter_vanvo_script_vi()` — bake slang dictionary + movie-title + ad break vào server-side để
script gen deterministic + cache-able. Until then, in-skill Gemini là OK.

---

## v2 Roadmap

- Channel branding (logo Văn Vở, intro/outro animation)
- Auto-upload YouTube + cross-post TikTok cut-down (extract scene 6-8 cao trào → Shorts)
- Optional sponsor integration (per-user opt-in only, NOT default — current rule = no ads)
- Multi-voice dialogue (nhân vật khác nhau = voice khác nhau — thay vì 1 narrator kể tất)
- Slang freshness tracker — slang outdate sau 6-12 tháng, skill ping warn nếu dictionary cần update

---

## Output Length Discipline

**Default = 1 screen.** Dashboard + 3 actions, no logs, no long explanations.
**Don't** repeat slang dictionary trong response — user check skill file.
**Don't** invoke backend on default — chỉ check roadmap + local files.
