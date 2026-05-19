# fk-tom-tac-sach — Tóm Tắt Sách (Vietnamese Audio Book Channel)

Status dashboard + book bootstrap pipeline cho channel tóm tắt sách bằng giọng Việt.

**Hybrid format:** tiểu thuyết → long-form chapter-by-chapter (10-15 min/chap), self-help → single summary (5-8 min).
**Voice mặc định:** `Bao_Trung_TTS` (warm storyteller male, natural narration pace). Alternative: `Phap_Van_podcast_TTS` (slow contemplative — chậm hơn ~15-20%).
**Output:** local-only — `output/<book_slug>_vi/` — upload defer cho v2.

**Cấu trúc video chapter format (3-act — KHÔNG có Analysis):**
- Hook (1 scene, ~1 min) — mở đầu + câu hook
- Summary (7-10 scenes, ~8-13 min) — kể cốt truyện chương, mỗi scene bắt đầu bằng từ nối thời gian (Đầu tiên / Sau đó / Bỗng nhiên / Cuối cùng...)
- Outro (1 scene, ~1 min) — CTA + câu hỏi thảo luận + tease chương sau
- Total: 9-12 scenes / ~10-15 min

(Skill /fk-video-lamplit-library cho English audience DỮ Analysis vì quốc tế thích literary criticism. Skill VN bỏ Analysis cho gần với plot-driven storytelling style of Vietnamese YouTube.)

Override per book: thêm `"include_analysis": true` trong roadmap entry nếu muốn 4-act lại.

Usage:
```
/fk-tom-tac-sach                                # status dashboard (default)
/fk-tom-tac-sach --detail                       # per-book/per-ep breakdown
/fk-tom-tac-sach --next                         # ONLY show 3 next actions
/fk-tom-tac-sach --batch <slug> <range>         # produce + build batch

# Bootstrap (smart positional — auto-detect format):
/fk-tom-tac-sach "Truyện Kiều"                            # auto: fiction → chapter-by-chapter
/fk-tom-tac-sach "Đắc Nhân Tâm"                           # auto: self-help → single summary
/fk-tom-tac-sach "Atomic Habits" --type foreign-self-help # explicit
/fk-tom-tac-sach "Số Đỏ" --format chapter --episodes 20   # override

# Voice override:
/fk-tom-tac-sach <book> --voice hong_hanh|podcast_male|narrator_male_vn
```

---

## Data Sources

| File | Purpose |
|------|---------|
| `output/_shared/tom-tac-sach-roadmap.json` | All books + format + entity waves + chapter/theme maps |
| `output/_shared/tts_templates/templates.json` | Available Vietnamese voices |
| `output/<book_slug>_vi/ep*/` | Built episode dirs |
| (No YouTube data — v1 is local-only) |

---

## Default Workflow (status dashboard)

### Step 1: Load roadmap
```
ROADMAP=output/_shared/tom-tac-sach-roadmap.json
```
If missing, create empty template:
```json
{
  "active_book": null,
  "books": {}
}
```

### Step 2: Compute state per book

For each book in roadmap, count:
- `local_built` = number of `output/<slug>_vi/ep*/` dirs containing `*_final_branded.mp4` (or `*_final.mp4` for summary format)
- `pending` = `total_episodes - local_built`
- Wave statuses (entities done/pending per wave)

### Step 3: Output 1-screen summary

```
📖 TÓM TẮT SÁCH  —  Status @ <today's date ICT>

📚 Active: <Book> (<Author>) — <built>/<total> tập đã build
   ├─ Format:        <chapter | summary>
   ├─ Voice:         <voice_template> @ <speed>
   ├─ Aesthetic:     <preset name>
   └─ Entity waves:  <wave statuses>

📅 Backlog cần build:
   ep<N>: <chapter/topic name>
   ep<N+1>: ...
   (max 5 rows)

🎯 NEXT ACTIONS:
   1. <#1 action with command>
   2. <#2 action>
   3. <#3 action>

📖 Books trong roadmap:
   ✅ <slug> (in_progress, <done>/<total>)
   ⏳ <slug> (planned)
```

### Step 4: Next-action decision tree

1. **Wave entities blocking?** → Gen wave trước
2. **Backlog > 0?** → Suggest `--batch <slug> <range>`
3. **Tất cả built?** → Suggest bootstrap book mới hoặc upload (when v2 ready)

---

## Bootstrap New Book Workflow

### Step 0 — Copyright + format detection

**For Vietnamese books:**
- Verify author qua đời > 70 năm OR confirm rights:
  - Trước 1955 (Nam Cao, Vũ Trọng Phụng, Nguyễn Du, Tản Đà...) → PD safe
  - Modern VN (Nguyễn Nhật Ánh, Nguyễn Phong Việt...) → cần check rights
- VN classics PD list: Truyện Kiều, Truyện Lục Vân Tiên, Cung Oán Ngâm Khúc, Chinh Phụ Ngâm, Nhật Ký Trong Tù, Số Đỏ, Lão Hạc, Chí Phèo, Tắt Đèn

**For foreign self-help (Vietnamese narration):**
- Fair-use scope: summary + analysis + critique = transformative use trong nhiều jurisdictions
- Always credit original author + book title trong description
- Do NOT read >10% of original text verbatim
- Examples OK: Atomic Habits, Sapiens, 7 Habits, Think and Grow Rich, How to Win Friends...
- Flag: Sách Việt translation (Đắc Nhân Tâm bản dịch) có thể có copyright trên translation → safer dùng English source + own Vietnamese rewording

**Format auto-detect:**
| Book class | Default format | Default duration |
|------------|----------------|------------------|
| Fiction / novel (Truyện Kiều, Số Đỏ, Atomic Habits novel) | `chapter` | 10-15 min × N chapters |
| Self-help / non-fiction (Đắc Nhân Tâm, Atomic Habits, Sapiens) | `summary` | 5-8 min single video |
| Memoir / philosophy (Nhật Ký Trong Tù) | `summary` OR `chapter` | user pick |
| Short story collection (Lão Hạc, Chí Phèo) | `chapter` (1 story = 1 ep) | 7-10 min × N stories |

User can override với `--format chapter|summary`.

### Step 1 — Aesthetic profile

| Book type | Preset | Visual cues |
|-----------|--------|-------------|
| VN classics 19th c (Truyện Kiều) | `vn_co_dien` | Làng quê Việt, đèn dầu, áo tứ thân, thư pháp, oil painting style |
| VN modern 1930-50 (Nam Cao, Vũ Trọng Phụng) | `vn_1930s_realist` | Làng quê đồng bằng Bắc Bộ, nhà tranh, áo nâu, đèn dầu, 1930s-40s |
| VN miền Nam 1950-75 (Tự Lực Văn Đoàn) | `vn_saigon_vintage` | Sài Gòn vintage, áo dài trắng, xe đạp, kiến trúc Pháp |
| Foreign self-help | `concept_minimal` | Conceptual abstract visuals (núi/đường/cánh cửa) matching key ideas, no characters needed |
| Foreign fiction translated | use book's original culture preset | (e.g., Gatsby → 1920s art deco; Atomic Habits novel → modern minimal) |

Material in Flow: `oil_painting` cho VN classics; `realistic` cho self-help concept; matching preset cho foreign fiction.

### Step 2 — Create Flow project

```bash
POST /api/projects
{
  "name": "<Book slug>_TomTacSach",
  "description": "Tóm tắt + phân tích <Book> bằng giọng Việt. Format: <chapter|summary>.",
  "story": "<2-3 câu giới thiệu sách + bối cảnh + aesthetic>",
  "material": "<oil_painting|realistic>",
  "language": "vi",
  "orientation": "HORIZONTAL"
}
```

### Step 3 — Wave 1 entities

**Fiction (chapter format):** 5-8 entities = main characters + key locations.
- Use English alias names trong Flow (Imagen content policy)
- Description chứa cultural cues (áo dài, nhà tranh, đèn dầu...)

**Self-help (summary format):** 3-5 concept assets only (no characters needed) — e.g., "Thói Quen Cũ" / "Hành Trình Thay Đổi" / "Lựa Chọn Hằng Ngày" as visual_asset entities.

Pause cho user review roster.

### Step 4 — Gen Wave 1 refs

Batch `GENERATE_CHARACTER_IMAGE`, poll until done. Download to `output/<slug>_vi/refs/`.

### Step 5 — Spot-check critical entity

Brand-defining visual (vd Chí Phèo cho Nam Cao series, hoặc concept Hook cho Atomic Habits).

### Step 6 — Extract chapter map OR theme map

**Chapter format (fiction):**
- `POST /api/book/extract-chapters` với mode auto (nếu có PDF) hoặc manual outline
- Output array `{ep, slug, chapter}`

**Summary format (self-help):**
- Skill prompts Gemini directly để identify 5-7 key principles/themes của sách
- Output array `{section, title, key_idea}` — sẽ là 5-7 sections trong 1 video

### Step 7 — Register trong roadmap

```json
{
  "active_book": "<slug>",
  "books": {
    "<slug>": {
      "title": "...",
      "author": "...",
      "format": "chapter|summary",
      "voice": "phap_van",
      "speed": 0.85,
      "aesthetic_preset": "vn_co_dien",
      "flow_project_id": "...",
      "local_dir": "output/<slug>_vi",
      "total_episodes": <N>,
      "status": "in_progress",
      "entity_waves": {...},
      "chapter_map": [...] | "theme_map": [...]
    }
  }
}
```

### Step 8 — Suggest first batch

```
🎉 <Book> bootstrapped.
   Format: <chapter|summary>
   Project: <pid>
   Wave 1: ✅ <N> entities

🎯 NEXT:
   1. Build first <batch_size> tập: /fk-tom-tac-sach --batch <slug> 1-<N>
   2. Test 1 ep trước, review chất lượng narration + visuals
   3. Adjust voice/aesthetic nếu cần trước batch lớn
```

---

## --batch Workflow (produce + build)

```
/fk-tom-tac-sach --batch <slug> <start>-<end>
```

1. Validate slug exists + range OK
2. Per ep trong range:
   - **Fiction (chapter):** Extract chapter script via existing endpoint (extend backend: `format: "chapter_podcast_vi"` — Vietnamese version của English chapter_podcast)
   - **Self-help (summary):** Extract via existing `format: "summary"` (already Vietnamese, 20-22 từ per scene)
3. Create video + scenes trong Flow
4. Mass batch GENERATE_IMAGE
5. Per ep: TTS (phap_van @ 0.85 hoặc speed-per-config) → music → Ken Burns → concat → mix → brand overlay (optional)
6. Output `output/<slug>_vi/ep<NN>/<slug>_final.mp4` (no upload yet)

---

## Pipeline Standard (locked defaults)

| Setting | Value |
|---------|-------|
| Default voice | `Bao_Trung_TTS` (warm storyteller — A/B tested vs phap_van and preferred) |
| Default speed | 0.85 (chapter), 0.90 (summary) |
| Narrator word count | 20-22 từ per sentence (Vietnamese) |
| Resolution | 1920×1080 HORIZONTAL (long-form) |
| FPS | 30 |
| TTS volume | 1.5× |
| Music volume | 0.06× (mix với narrator — giảm 1/2 để narrator clear hơn) |
| Music output | MP3 (transcode Gemini Lyria MP4) |
| Scene count | 7-10 (summary), 10-14 (chapter) |
| Ken Burns motion | Vary per scene, no consecutive repeat |
| Brand overlay | Optional (no default channel yet) — leave room cho future config |
| Cultural visuals | MANDATORY for VN books (làng quê, áo dài, đèn dầu nếu phù hợp era) |
| English text in image | ❌ AVOID — narration là VN audio, image không cần English text |

---

## Voice Options (Vietnamese TTS templates)

| Voice | Style | Best for |
|-------|-------|----------|
| `Bao_Trung_TTS` (default) | Warm storyteller male, natural narration | Long-form fiction, classics, general use |
| `Phap_Van_podcast_TTS` | Slow contemplative podcast male | Philosophical, meditative, slower pace |
| `Hong_Hanh_podcast_TTS` | Warm female podcast | Modern romance, emotional self-help |
| `podcast_male_TTS` | Standard male narrator | Business, self-help neutral |
| `narrator_male_vn` | Young adult male | Action stories, contemporary fiction |
| `Nguyen_Ngoc_Ngan_TTS` | Classic radio storyteller | VN classics, traditional tales |
| `Manh_Dung_TTS` | Brief energetic male | Short snippets, news-style |

User override: `--voice <name>`. Default per A/B test: Bao_Trung_TTS (don't ask unless user explicit).

---

## Aesthetic Profile Detail

### vn_co_dien (VN 19th century classical)
```
Làng quê Việt Nam thế kỷ 19, nhà tranh mái lá, sân vườn cây ăn trái,
đèn dầu, áo tứ thân hoặc áo dài cổ điển, búi tóc, thư pháp Hán Nôm,
phong cảnh sông nước miền Bắc Việt Nam, oil painting cinematic style,
warm amber + deep umber palette, melancholy contemplative mood.
NO modern objects, NO electricity, NO contemporary clothing.
```

### vn_1930s_realist (Nam Cao, Vũ Trọng Phụng era)
```
Làng quê đồng bằng Bắc Bộ Việt Nam 1930-1945, nhà tranh xiêu vẹo,
đường đất, ruộng lúa, áo nâu sòng, dép cao su, nón lá, đèn dầu,
chùa làng, đình làng, xe trâu xe bò, cảnh nghèo khổ, mood ảm đạm,
oil painting realist, deep umber + dusty earth palette, social realism aesthetic.
NO modern items, NO motorcycles, NO electricity.
```

### vn_saigon_vintage (1950-1975 Saigon)
```
Sài Gòn vintage 1950-1975, kiến trúc Pháp colonial, hàng cây me bên đường,
xe đạp xe Vespa cổ, áo dài trắng nữ sinh, áo sơ mi nam, quán cà phê vỉa hè,
chợ Bến Thành, đèn neon mờ, cinematic warm tone, oil painting + cinéma vérité.
NO contemporary cars, NO smartphones.
```

### concept_minimal (foreign self-help)
```
Conceptual minimal abstract visual representing <key idea>,
metaphorical landscape (núi, đường, cánh cửa, ánh sáng, bóng tối),
oil painting cinematic, warm umber + gold palette, contemplative mood,
no specific characters, no text, no logos, no anachronisms.
Style: Edward Hopper meets Caspar David Friedrich.
```

---

## Common Errors

| Error | Fix |
|-------|-----|
| Roadmap không tồn tại | Skill tự tạo empty template |
| Book slug đã tồn tại trong roadmap | Show status thay vì bootstrap; use `--bootstrap` flag để force |
| Wave 1 entities có English text trong image | Add "STRICTLY NO TEXT in image" to all visual entity prompts |
| Narrator sentence > 22 từ | Re-extract script với tighter constraint |
| Voice template không có | List available templates, fall back to phap_van |
| Foreign self-help → image generates Western faces | Set aesthetic = `concept_minimal` (no characters) hoặc adjust entity descriptions |
| Music quá to che narration | Lower music_volume từ 0.06 → 0.04 |

---

## Backend Extension Needed (v1.1)

Backend hiện tại có:
- ✅ `format: "summary"` — Vietnamese 5-8 min, 20-22 từ per scene (works for self-help summary mode)
- ✅ `format: "chapter_podcast"` — ENGLISH 10-15 min/chapter (works for Lamplit)
- ❌ `format: "chapter_podcast_vi"` — Vietnamese 10-15 min/chapter (needed for VN fiction long-form)

**Action item:** When first VN fiction book bootstrapped, extend `agent/services/book_script_writer.py` với function `write_chapter_podcast_script_vi()` — mirror English version nhưng:
- Vietnamese narration 20-22 từ per sentence × ~50-60 sentences total
- Hook mention sách + tác giả + chương + câu hook
- Time connectors Vietnamese: "Đầu tiên / Sau đó / Bỗng nhiên / Trong khi đó / Cuối cùng / Tới cùng"
- Outro CTA Vietnamese tự nhiên (không sound như marketing): "Nếu bạn thấy hay, hãy theo dõi để không bỏ lỡ chương sau..."
- Cultural visual prompts in scene_prompt

---

## v2 Roadmap

- Auto-upload tới chosen YouTube channel (config trong roadmap per book)
- Auto-thumbnail generation với Vietnamese hook text
- Auto-caption .vtt sync
- Multi-language audience targeting (sub vào tiếng Anh nếu muốn reach overseas Việt diaspora)
- Audio-only podcast platform export (Spotify Việt Nam)

---

## Output Length Discipline

**Default = 1 screen.** Show dashboard + 3 actions. No long explanations, no command logs.
**Don't** repeat aesthetic descriptions (user can check this skill file).
**Don't** invoke backend on default — only check roadmap + local files.
