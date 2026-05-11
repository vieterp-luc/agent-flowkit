# fk-video-book-quote — Tạo Video Shorts từ Trích Dẫn Sách (TikTok/Reels)

Chuyên biến trích dẫn ý nghĩa từ sách thành Shorts vertical podcast-style 2-3 phút với visual cinematic và narration sâu sắc (pure audio + rotating images, NO text overlay, không CTA sách). Hỗ trợ series mode từ list chương sách để tạo podcast multi-episode.

Usage: `/fk-video-book-quote "<tên sách>" [--topic "<chủ đề/chương cụ thể>"] [--source pdf:/path/to/book.pdf] [--source manual:"outline text"] [--target-seconds 150] [--count 3]`

---

## Workflow Series (nhiều video từ 1 sách)

Để làm series podcast từ 1 sách (ví dụ Đắc Nhân Tâm với 30+ nguyên tắc):

### Step 1 — List chapters/topics (1 lần đầu)

POST `/api/book/extract-chapters` trả list chương:
- mode: "auto" (PDF/EPUB) hoặc "manual" (outline)
- max_chapters: cap (default 30)

```bash
curl -X POST http://127.0.0.1:8100/api/book/extract-chapters \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "manual",
    "source": {
      "outline": "...",
      "metadata": {"title": "Đắc Nhân Tâm", "author": "Dale Carnegie"}
    },
    "max_chapters": 8
  }'

# Response:
# {
#   "ok": true,
#   "chapters": [
#     {"id": 1, "title": "Đừng Chỉ Trích, Hãy Khen Ngợi Chân Thành",
#      "key_idea": "...", "summary": "..."},
#     ...
#   ]
# }
```

Lưu list này làm content calendar.

### Step 2 — Mỗi chương = 1 video (loop hoặc on-demand)

Pass `options.topic` để focus extraction:

```bash
/fk-video-book-quote "Đắc Nhân Tâm" --topic "Sức Mạnh Lắng Nghe và Nhớ Tên Người Khác"
```

Chỉ extract content liên quan đến topic, ignore phần khác. Output: 1 video focused.

Các topic khác cùng sách → các video khác trong series.

---

## Tổng quan pipeline

```
Extract quote script (1x, 7-10 insights)
    ↓
/fk-create-project (VERTICAL 9:16, 4-6 scenes)
    ↓
/fk-gen-images (4-6 scenes)
    ↓
POST /api/ken-burns/clip (quote + insights sceneized, NO text overlay)
    ↓
/fk-gen-narrator (Hong_Hanh TTS speed 0.95, all parts concat)
    ↓
POST /api/ken-burns/concat (scenes, pure visual)
    ↓
POST /api/music/generate (instrumental 2-3 min, loop if needed)
    ↓
ffmpeg mix (narrator 1.5× + music 0.15×)
    ↓
/fk-brand-logo (corner watermark)
```

**Music:** 1 Gemini Lyria Pro track (instrumental only). Loop with `-stream_loop -1` if video exceeds track duration.

---

## Bước 0: Extract quote script

Tạo 1 quote object với 7-10 insights từ sách (Phase 1 backend, `/api/book/extract-script`):

**Mode A — manual (chỉ tên sách + outline ngắn):**
```bash
curl -X POST http://127.0.0.1:8100/api/book/extract-script \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "manual",
    "format": "quote",
    "source": {
      "outline": "[Tóm tắt ý chính sách 2-5 câu]",
      "metadata": {"title": "Đắc Nhân Tâm", "author": "Dale Carnegie"}
    },
    "options": {
      "count": 1,
      "target_seconds": 150,
      "topic": "Tên chương / chủ đề cụ thể (optional)"
    }
  }'
```

**Mode B — auto (có file PDF/EPUB):**
```bash
curl -X POST http://127.0.0.1:8100/api/book/extract-script \
  -d '{
    "mode": "auto",
    "format": "quote",
    "source": {
      "file_path": "/path/to/book.pdf",
      "metadata": {"title": "...", "author": "..."}
    },
    "options": {
      "count": 1,
      "target_seconds": 150,
      "topic": "Tên chương / chủ đề cụ thể (optional)"
    }
  }'
```

**Note:** When `topic` provided, system prompt tells Gemini to focus only on that topic — ignore unrelated content.

**New v2 Response (quote + 7-10 insights + outro):**
```json
{
  "ok": true,
  "format": "quote",
  "data": {
    "script": [
      {
        "quote": "Trích dẫn cốt lõi (Vietnamese, 20-22 từ)",
        "insights": [
          {"narrator_text": "Insight 1 — 20-22 từ", "scene_prompt": "english scene description"},
          {"narrator_text": "Insight 2 — 20-22 từ", "scene_prompt": "english scene description"},
          ... (7-10 insights total)
        ],
        "outro": "Câu kết suy ngẫm (NO book/author mention, 20-22 từ)",
        "source_book": {"title": "Đắc Nhân Tâm", "author": "Dale Carnegie"}
      }
    ]
  }
}
```

Lưu `data.script[0]` và concat: quote → 7-10 insights → outro vào 1 narrator duy nhất.

---

## Bước 1: Thiết kế dự án (`/fk-create-project`)

**Cấu hình chuẩn cho Book Quote Shorts (podcast-style 2-3 min):**

| Tham số | Giá trị |
|---------|---------|
| Material | `realistic` |
| Orientation | `VERTICAL` (9:16) |
| Số scenes | **4-6 scenes** (dài hơn v1) |
| Language | Vietnamese |
| Resolution | 1080×1920 |
| FPS | 30 |

**Thiết kế 4-6 scenes theo arc (120-180s total):**

Recommended option:
- **4 scenes × {15s hook, 25s body, 25s body, 15s outro} = 78s**
- **Or 5 scenes × {12s hook, 18s body, 18s body, 18s body, 12s outro} = 75s**

| Scene | Vai trò | Duration | Narrator source |
|-------|---------|----------|-----------------|
| 0 | **HOOK** | 12-15s | `quote` (20-22 từ) |
| 1-N | **INSIGHTS** | 18-25s each | `insights[i].narrator_text` (20-22 từ each) |
| Last | **OUTRO** | 12-15s | `outro` (20-22 từ, NO book name) |

**Entities chuẩn:**
- **1-2 visual assets** — subject/objects liên quan quote theme
- **0-1 characters** — chỉ nếu cần human element
- **1 location** — setting chính của video

**Narrator text rule (CRITICAL):**
- NEVER mention book title or author name in narrator (TTS)
- Pure wisdom delivery: quote → insights → reflection
- Source metadata stays in `source_book` for captions/description ONLY
- Each sentence: 20-22 từ → TTS ~6-7s tại speed 0.95

**Tránh:**
- Mô tả những gì viewer đang thấy ("Chúng ta thấy...")
- Quá dài: >22 từ → TTS bị cắt
- Mention sách: "Sách [tên]..." → DELETE, dùng outro suy ngẫm thay

**Scene prompts (từ extract-script `insights[i].scene_prompt`):**

Mỗi insight đã có `scene_prompt` tiếng Anh. Map 7-10 insights vào 4-6 scenes:
- Scene 0 (hook) ← quote
- Scenes 1-N (body) ← group insights by visual continuity (không 1:1)
- Last scene (outro) ← outro reflection

**Image prompt formula (vertical 9:16):**
```
[Subject conveying quote theme] in [evocative setting].
Cinematic vertical composition, 9:16 portrait frame.
[Mood: powerful / contemplative / dramatic].
Soft cinematic lighting, depth of field, 4K, hyperrealistic photography.
Negative: subtitles, watermark, text, logos.
```

---

## Bước 2: Generate scene images (`/fk-gen-images`)

4-6 scenes × 1 image each. Submit 1 batch:

```bash
# Sau khi /fk-create-project trả PROJECT_ID + scene_ids
# Submit gen-images cho tất cả 4-6 scenes 1 lần
```

Poll 15s/lần đến khi `done: true`. Verify tất cả scene có image media_id UUID.

**Output**: image local path (download từ scene URL về `output/{slug}/images/scene_N.png`)

---

## Bước 5: Generate TTS (Hong_Hanh, speed 0.95)

**Concat ALL parts into ONE narrator text:**
```
{quote} {insight1} {insight2} ... {insight7-10} {outro}
```

**Voice template:** `Hong_Hanh_podcast_TTS` · Speed `0.95`

```bash
curl -X POST http://127.0.0.1:8100/api/tts/generate \
  -d '{
    "text": "[quote] [insight1] [insight2] ... [insightN] [outro]",
    "ref_audio": "output/_shared/tts_templates/Hong_Hanh_podcast_TTS.wav",
    "ref_text": "Đây là một bản ghi âm tiêu chuẩn cho mẫu giọng Hong Hanh...",
    "speed": 0.95,
    "output_path": "output/{slug}/tts/narrator_full.wav"
  }'
```

**Expected TTS duration (speed 0.95, 20-22 từ/câu × 9-11 câu):** ~60-80s total (fits 2-3 min video window)

---

## Bước 3: Apply Ken Burns motion

**API contract:** `POST /api/ken-burns/clip`
```json
{
  "image_path": "output/{slug}/images/scene_N.png",
  "duration_seconds": 12-25,
  "motion": "zoom_in" | "zoom_out" | "pan_left" | "pan_right" | "pan_up" | "pan_down" | "parallax" | "static",
  "resolution": "1080x1920",
  "output_path": "output/{slug}/clips/scene_N.mp4"
}
```

**Motion variation rule:** Không dùng cùng motion liên tiếp. Example rotation: `zoom_in` → `pan_left` → `pan_right` → `zoom_out` → `pan_left` → `pan_right`.

**Curl example (loop tất cả scenes):**
```bash
for SCENE_IDX in {0..5}; do
  curl -X POST http://127.0.0.1:8100/api/ken-burns/clip \
    -H 'Content-Type: application/json' \
    -d '{
      "image_path": "output/{slug}/images/scene_'$SCENE_IDX'.png",
      "duration_seconds": 15-25,
      "motion": "[motion_N]",
      "resolution": "1080x1920",
      "output_path": "output/{slug}/clips/scene_'$SCENE_IDX'.mp4"
    }'
done
```

---

## Bước 4: Concat clips

Dùng `/api/ken-burns/concat` hoặc ffmpeg xfade:

```bash
curl -X POST http://127.0.0.1:8100/api/ken-burns/concat \
  -H 'Content-Type: application/json' \
  -d '{
    "clips": [
      {"path": "output/{slug}/clips/scene_0.mp4", "duration": 15},
      {"path": "output/{slug}/clips/scene_1.mp4", "duration": 22},
      ... (4-6 scenes total)
    ],
    "xfade_duration": 0.5,
    "output_path": "output/{slug}/concat_scenes.mp4"
  }'
```

→ Output: `concat_scenes.mp4` (~80-100s, no audio)

---

## Bước 5a: Generate music (instrumental 2-3 min)

**1 Gemini Lyria Pro track (instrumental ONLY):**

```bash
curl -X POST http://127.0.0.1:8100/api/music/generate \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, calm contemplative ambient piano, warm strings, podcast background music, gentle pads, low energy, suitable for narration overlay, 2-3 minutes",
    "model": "gemini-lyria-pro",
    "duration_seconds": 150,
    "output_path": "output/{slug}/music/narrator_bgm.wav"
  }'
```

**Music duration:** 2-3 min (~120-180s). If video > track length, loop using `-stream_loop -1`.

---

## Bước 5b: Loop music if needed

If video duration > music track duration:

```bash
# Extract video duration first:
VIDEO_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1:nokey=1 output/{slug}/concat_scenes.mp4)

# Loop music to match video duration, with fade-out at end:
ffmpeg -stream_loop -1 -i output/{slug}/music/narrator_bgm.wav \
  -t $VIDEO_DUR \
  -ar 48000 -ac 2 \
  -af "afade=t=out:st=$(echo "$VIDEO_DUR - 2" | bc):d=2" \
  output/{slug}/music/narrator_bgm_looped.wav
```

---

## Bước 6: Mix TTS + music

**Volume mix chuẩn:**
| Track | Volume |
|-------|--------|
| Original SFX | 0 (no audio) |
| TTS narrator | 1.5 (150%) |
| Music BGM | **0.15** (15% — instrumental, don't override narrator) |

```bash
ffmpeg -y \
  -i output/{slug}/concat_scenes.mp4 \
  -i output/{slug}/tts/narrator_full.wav \
  -i output/{slug}/music/narrator_bgm_looped.wav \
  -filter_complex "[1:a]volume=1.5[tts];[2:a]volume=0.15[music];[tts][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -ar 48000 -ac 2 -b:a 192k \
  -movflags +faststart \
  output/{slug}/quote_final.mp4
```

**Lưu kết quả:** `output/{slug}/quote_final.mp4` (2-3 min Shorts)

---

## Bước 7: Generate caption (`/fk-gen-caption`)

```bash
/fk-gen-caption <video_id>
```

Tạo caption từ narrator text (Vietnamese SRT). Để lộ source_book metadata ở đây, KHÔNG ở narrator.

---

## Checklist nhanh

```
[ ] Bước 0: Extract 1 quote script (POST /api/book/extract-script, target_seconds=150)
[ ]   Verify: quote + 7-10 insights + outro, NO book name in narrator_text
[ ] Bước 1: /fk-create-project (VERTICAL, 4-6 scenes, podcast-style 2-3 min)
[ ] Bước 2: /fk-gen-images (4-6 scenes 1 wave)
[ ] Bước 3: POST /api/ken-burns/clip × 4-6 scenes (motion vary, NO text overlay)
[ ]   Verify NO consecutive motion repeat
[ ] Bước 4: /api/ken-burns/concat (xfade 0.5s, ~80-100s)
[ ] Bước 5a: POST /api/music/generate (instrumental 2-3 min, NO vocals)
[ ] Bước 5b: ffmpeg loop music if video > track (use -stream_loop -1)
[ ] Bước 5c: /fk-gen-narrator (concat quote + 7-10 insights + outro)
[ ]   TTS: Hong_Hanh_podcast_TTS, speed 0.95, ~60-80s total
[ ] Bước 6: ffmpeg mix TTS (1.5×) + music (0.15×)
[ ]   Add fade-out to looped music 2s before end
[ ] Bước 7: /fk-brand-logo (optional corner watermark)
[ ] Output: quote_final.mp4 (podcast-style 2-3 min, pure audio + visual, no CTA)
```

---

## Ví dụ đã làm

| Video | Book | Duration | Output |
|-------|------|----------|--------|
| Quote-Potential-v2 | Khoa Học Bất Bình Thường | 2:15 (podcast) | `output/book_quote_potential_v2` |
| Quote-Discipline-v2 | Khoa Học Bất Bình Thường | 2:30 (podcast) | `output/book_quote_discipline_v2` |

---

## Image prompt template (vertical)

```
A [subject conveying quote theme] in [evocative setting].
Cinematic vertical composition, 9:16 portrait frame, looking upward.
[Mood: powerful / contemplative / dramatic / inspiring].
Soft cinematic lighting, warm golden hour / cool blue mood, depth of field.
Sharp details, 4K hyperrealistic photography, smooth bokeh background.
Negative: text, subtitles, watermark, logos, people's faces, artistic filters.
```

**Examples:**
```
An ancient tree growing from stone, roots spreading, branches reaching skyward.
Cinematic vertical composition, 9:16 frame. Powerful, inspiring mood.
Soft golden-hour lighting, depth of field, 4K hyperrealistic. Negative: text, watermark.

A notebook with pen, surrounded by books and green plants on wooden desk.
Cinematic vertical, 9:16 frame. Contemplative, peaceful mood.
Soft warm lighting, shallow depth, 4K hyperrealistic. Negative: text, watermark, logos.
```

---

## Narrator text template (20-22 từ/sentence, NO book mention)

```
[Scene 0 - Hook quote (quote từ extract-script)]:
"Trong lòng mỗi người tồn tại tiềm năng vô hạn chưa được khám phá và khai phát."

[Scene 1-N - Insights (7-10 từ insights[].narrator_text)]:
"Khi chúng ta hiểu rõ bản chất tiềm năng, cuộc sống sẽ thay đổi hoàn toàn mãi mãi."
"Đó là lý do tại sao mỗi ngày nhỏ đóng góp vào sự lớn lên của bản thân."

[Last - Outro (outro từ extract-script, NO book name)]:
"Hành trình khám phá bản thân bắt đầu từ một câu hỏi đơn giản: em là ai thực sự?"
```

**CRITICAL:** Outer should NEVER mention book title, author, "subscribe", "read", or any CTA. Pure contemplation only.

---

## Series Best Practices

- Run extract-chapters lần đầu để có content calendar
- 1 topic = 1 video → tránh trùng nội dung giữa các video
- Naming convention output: `output/<book_slug>/episode_<NN>_<topic_slug>/final.mp4`
- Music reuse: 1 track Lyria có thể dùng cho 3-5 episodes (cùng vibe podcast)
- Image gen: mỗi episode tạo project Flow riêng (4 ảnh × N episodes)
- Quota: chú ý Imagen quota nếu run series 10+ episodes

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| Narrator nhắc tên sách | Schema extract-script cũ, narr text chứa CTA | Verify insights[].narrator_text chỉ có wisdom, KHÔNG sách name |
| TTS bị cắt giữa câu | >22 từ thật | Rút ngắn hoặc tách thành 2 insight |
| Music quá to che TTS | Volume 0.15 vẫn quá cao | Giảm xuống 0.10-0.12 |
| Music dừng giữa video | Lỗi -stream_loop -1 | Verify: `ffmpeg -stream_loop -1`, không dùng `-loop 1` |
| Ken Burns motion quá nhanh | Duration 12-15s quá ngắn | Tăng lên 18-25s per scene |
| Video output không có audio | Audio filter error | Kiểm tra `-ar 48000 -ac 2`, không dùng `-an` flag |
| Music có vocal/lyrics | Gemini prompt không rõ | Thêm "instrumental ONLY, no vocals, no lyrics, no singing" đầu prompt |
| Topic extraction lọc sai | Topic string không khớp outline | Verify topic tên chính xác, không typo |
| Extract-chapters API error | Mode/source schema sai | Check mode: "auto" vs "manual", source.outline format |
