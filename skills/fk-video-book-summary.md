# fk-video-book-summary — Tóm tắt sách (YouTube long-form)

Long-form podcast video (5-8 phút) từ tên sách hoặc PDF, chuỗi hình ảnh kèm Ken Burns motion + narrator tiếng Việt (NO book/author mention) + nhạc nền instrumental (pure audio + rotating images, NO text overlay). Hỗ trợ series mode focus theo chương để tạo episode-based content.

Usage: `/fk-video-book-summary "<tên sách hoặc outline>" [--topic "<chương/chủ đề cụ thể>"] [--source pdf:/path/to/book.pdf] [--target-minutes 7]`

---

## Workflow Series (nhiều video từ 1 sách)

Để làm series podcast từ 1 sách (ví dụ Atomic Habits với 4 phần chính):

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
      "metadata": {"title": "Atomic Habits", "author": "James Clear"}
    },
    "max_chapters": 8
  }'

# Response:
# {
#   "ok": true,
#   "chapters": [
#     {"id": 1, "title": "The Fundamentals: Why Tiny Changes Make Big Difference",
#      "key_idea": "...", "summary": "..."},
#     ...
#   ]
# }
```

Lưu list này làm content calendar.

### Step 2 — Mỗi chương = 1 video (loop hoặc on-demand)

Pass `options.topic` để focus extraction trên chương cụ thể:

```bash
/fk-video-book-summary "Atomic Habits" --topic "How to Build Better Habits in 4 Steps"
```

Chỉ extract content liên quan đến topic, ignore phần khác. Output: 1 video focused dài 5-8 phút.

Các topic khác cùng sách → các video khác trong series.

---

## Tổng quan pipeline

```
Extract script           Create project (HORIZONTAL)    Gen images (1 wave)
        ↓                           ↓                            ↓
POST /api/book/extract-script   /fk-create-project        /fk-gen-images
        ↓
Apply Ken Burns     Generate TTS narrator        Generate 3 music tracks
        ↓                    ↓                              ↓
POST /api/ken-burns/clip   POST /api/tts/generate    POST /api/gemini/browser/generate-music
        ↓
Concat + mix audio   Optional: Brand + Caption
        ↓
POST /api/ken-burns/concat  /fk-brand-logo + /fk-gen-caption
```

---

## Bước 0: Extract script từ sách

**Endpoint:** `POST /api/book/extract-script`

```bash
curl -X POST http://127.0.0.1:8100/api/book/extract-script \
  -H "Content-Type: application/json" \
  -d '{
    "book_name": "Atomic Habits",
    "format": "summary",
    "language": "vi",
    "sections": 7,
    "target_minutes": 7,
    "options": {
      "topic": "Tên chương / chủ đề cụ thể (optional)"
    }
  }'
```

**Note:** When `topic` provided, system prompt tells Gemini to focus only on that topic — ignore unrelated content.

**v2 Response schema:**
```json
{
  "title": "Atomic Habits",
  "author": "James Clear",
  "hook": {
    "narrator_text": "Những thay đổi nhỏ mỗi ngày tạo ra những kết quả lớn theo thời gian...",
    "scene_prompt": "english scene description"
  },
  "sections": [
    {
      "section": 1,
      "title": "1% Daily Improvement",
      "narrator_text": "Một sự cải thiện một phần trăm mỗi ngày có vẻ nhỏ...",
      "scene_prompt": "english scene description",
      "key_themes": ["habit", "improvement", "consistency"]
    },
    ... (5-7 sections tương tự)
  ],
  "outro": {
    "narrator_text": "Hành trình thay đổi bắt đầu từ những quyết định nhỏ hàng ngày...",
    "scene_prompt": "english scene description"
  },
  "source_book": {"title": "Atomic Habits", "author": "James Clear"}
}
```

**Verify:**
- CRITICAL: `hook.narrator_text` + all `sections[].narrator_text` + `outro.narrator_text` NEVER mention book title/author
- `hook.narrator_text` ≥ 15 từ, ≤ 30 từ
- Mỗi `sections[i].narrator_text` ≈ 20-22 từ (đếm theo split)
- `outro.narrator_text` ≥ 15 từ (reflection, NO "read the book" CTA)

---

## Bước 1: Thiết kế dự án (`/fk-create-project`)

### Cấu hình chuẩn

| Tham số | Giá trị |
|---------|---------|
| Orientation | `HORIZONTAL` (16:9) |
| Material | `realistic` |
| Resolution | 1920×1080 |
| Số scenes | 7-10 (1 hook + 5-7 sections + 1 outro) |
| Language | Vietnamese |
| FPS | 30 |

### Scene structure

| Scene | Loại | Duration | Narrator text | Image subject |
|-------|------|----------|---------------|---------------|
| 0 | HOOK | 20-30s | Opening statement từ extract-script | Book theme visual |
| 1-7 | SECTION | 60-90s | Section narrator text | Key concept từng section |
| 8 | OUTRO | 30-45s | Closing statement + CTA | Resolution/summary visual |

**Entities:** 1-3 locations hoặc visual assets (không cần character — focus vào concept visuals)

### Narrator text per scene (Vietnamese, 20-22 từ, contemplative podcast tone, NO book mention)

**Hook template:**
```
[Powerful opening idea/question — NO book name] [Why it matters] [What you'll learn].
```
Example: "Những thay đổi nhỏ nhất có thể tạo ra kết quả lớn nhất — nhưng tại sao chúng ta lại bỏ qua chúng?"

**Section template (repeat 5-7 lần):**
```
[Key concept from section] [Example or explanation] [Real-world application — NO book reference].
```

**Outro template:**
```
[Powerful closing reflection] [Call to action on wisdom, NOT book] [End with contemplative question].
```
Example: "Hôm nay bạn sẽ bắt đầu một thay đổi nhỏ nào — biết rằng nó sẽ dẫn đến điều tuyệt vời?"

**CRITICAL RULE:**
- NEVER: "Cuốn sách này dạy...", "Tác giả James Clear...", "Đọc sách để..."
- ALWAYS: Pure wisdom delivery + contemplative outro
- `outro.narrator_text` MUST NOT contain CTA like "subscribe/follow/read"

**Đếm từ (Python):**
```python
text.split()  # tính cả dấu như "—" là 1 token
# Mục tiêu: 20-22 tokens thật → TTS duration ~6-7s tại speed 0.85
```

### Patch narrator_text vào từng scene

Sau khi create project, PATCH `narrator_text` vào từng scene (lưu reference).

---

## Bước 2: Generate scene images (`/fk-gen-images`)

### Single wave (no chain)

| Wave | Scenes | Request type |
|------|--------|-------------|
| 1 | Tất cả 7-10 scenes | `GENERATE_IMAGE` |

**Poll 15s/lần cho đến khi `done: true`.**

---

## Bước 3: Apply Ken Burns motion

**Endpoint:** `POST /api/ken-burns/clip`

**Ken Burns motion strategy (vary để tránh lặp):**

| Scene | Motion | Duration | Effect |
|-------|--------|----------|--------|
| 0 (HOOK) | `zoom_in` | 5-6s | Intensify attention |
| 1 | `pan_left` | 5-6s | Explore composition |
| 2 | `pan_right` | 5-6s | Counter-movement |
| 3 | `zoom_out` | 5-6s | Reveal context |
| 4 | `zoom_in` | 5-6s | Focus detail |
| 5 | `pan_left` | 5-6s | Symmetric pacing |
| 6 | `pan_right` | 5-6s | Maintain rhythm |
| 7 | `zoom_out` | 5-6s | Release/outro |

**Rule:** Không có 2 scenes liên tiếp dùng cùng motion.

**Curl example:**

```bash
curl -X POST http://127.0.0.1:8100/api/ken-burns/clip \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "output/<slug>/images/scene_N.png",
    "duration_seconds": 5-6,
    "motion": "zoom_in",
    "resolution": "1920x1080",
    "output_path": "output/<slug>/ken-burns/scene_0_zoom_in.mp4"
  }'
```

**Process:**
1. Loop mỗi scene từ script extract
2. GET media URL từ scene sau /fk-gen-images
3. PATCH motion strategy vào scene (lưu reference)
4. POST /api/ken-burns/clip per scene → download clip

**Tổng duration:** ~7-10 phút × 60s = 420-600s video content

---

## Bước 4: Generate TTS narrator

### Concat all narrator texts

Ghép tất cả `narrator_text` từ hook + 5-7 sections + outro thành 1 dài đoạn:

```
{hook} {section1} {section2} ... {sectionN} {outro}
```

### Generate single TTS file

**Endpoint:** `POST /api/tts/generate`

```bash
# Voice template: Phap_Van_podcast_TTS (slow, contemplative podcast style)
# Speed: 0.85 (long-form pacing, not rushed)

curl -X POST http://127.0.0.1:8100/api/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<full concatenated narrator text>",
    "ref_audio": "output/_shared/tts_templates/Phap_Van_podcast_TTS.wav",
    "ref_text": "Năm hai nghìn không trăm hai mươi tư, thế giới đổi thay mãi mãi...",
    "speed": 0.85,
    "output_path": "output/<slug>/tts/narrator_full.wav"
  }'

# Response:
{
  "audio_url": "https://storage.googleapis.com/...",
  "duration_s": 420.5,
  "format": "wav"
}
```

**Verify:**
- TTS duration < total Ken Burns clips duration (breathing room 1-2s)
- Format: WAV, mono or stereo, 48kHz

---

## Bước 5: Generate music (instrumental ONLY)

**Endpoint:** `POST /api/gemini/browser/generate-music`

**Single track OR 3 tracks (both work — 3 tracks preferred for intro/body/outro transitions):**

### Option A: Single continuous track (simpler)

```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, no singing, calm contemplative ambient piano, warm strings, podcast background music, gentle pads, low energy, suitable for narration overlay, 7-8 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 7,
    "output_path": "output/<slug>/music/narrator_bgm_continuous.wav"
  }'
```

### Option B: 3 tracks (INTRO + BODY + OUTRO)

**Track 1: INTRO**
```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, cinematic intro music, building anticipation, deep strings + soft piano, contemplative, podcast opener, no melody peaks, fade-friendly ending, 2-3 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 3,
    "output_path": "output/<slug>/music/intro_cinematic.wav"
  }'
```

**Track 2: BODY**
```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, calm ambient piano, low energy, podcast background, contemplative, no melody peaks, gentle pads, suitable for narration overlay, 5-7 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 7,
    "output_path": "output/<slug>/music/body_ambient.wav"
  }'
```

**Track 3: OUTRO**
```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, warm uplifting piano, hopeful resolution, gentle strings, emotional but restrained, podcast closer, fade-friendly ending, 2-3 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 3,
    "output_path": "output/<slug>/music/outro_warm.wav"
  }'
```

**Music duration targets:**
- Single track: 7-8 min (matches typical video length)
- INTRO: 2:30-3:00
- BODY: 5:00-7:00
- OUTRO: 2:30-3:00

**CRITICAL:** All prompts must emphasize "instrumental ONLY, no vocals, no lyrics, no singing" to avoid lyrical contamination.

---

## Bước 6: Concat + Mix audio

### 6a. Download Ken Burns clips + concat

```bash
# Download từng Ken Burns clip (đã có video, không audio)
for i in {0..8}; do
  ffmpeg -ss 0 -i "<Ken Burns clip URL $i>" \
    -c:v libx264 -crf 18 \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
    -r 30 -pix_fmt yuv420p -an \
    output/<slug>/raw/scene_$i.mp4
done

# xfade concat 7-10 clips (0.5s crossfade)
ffmpeg \
  -i output/<slug>/raw/scene_0.mp4 \
  -i output/<slug>/raw/scene_1.mp4 \
  ... \
  -i output/<slug>/raw/scene_N.mp4 \
  -filter_complex "[xfade chains]" \
  -map [vout] \
  -c:v libx264 -crf 18 -r 30 -pix_fmt yuv420p \
  output/<slug>/concat_scenes.mp4
```

### 6b. Mix narrator + music into concat video

**For Option A (single track):**
```bash
ffmpeg -y \
  -i output/<slug>/concat_scenes.mp4 \
  -i output/<slug>/tts/narrator_full.wav \
  -i output/<slug>/music/narrator_bgm_continuous.wav \
  -filter_complex "[1:a]volume=1.5[narrator];[2:a]volume=0.15[music];[narrator][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v libx264 -crf 18 -r 30 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  output/<slug>/<slug>_final.mp4
```

**For Option B (3 tracks with transitions):**
```bash
ffmpeg -y \
  -i output/<slug>/concat_scenes.mp4 \
  -i output/<slug>/tts/narrator_full.wav \
  -i output/<slug>/music/intro_cinematic.wav \
  -i output/<slug>/music/body_ambient.wav \
  -i output/<slug>/music/outro_warm.wav \
  -filter_complex "
    [1:a]volume=1.5[narrator];
    [2:a]volume=0.15,atrim=0:3[intro_mix];
    [3:a]volume=0.15[body_mix];
    [4:a]volume=0.15,atrim=0:3[outro_mix];
    [intro_mix][body_mix]acrossfade=d=1:c1=tri:c2=tri[intro_body];
    [intro_body][outro_mix]acrossfade=d=1:c1=tri:c2=tri[music_mix];
    [music_mix][narrator]amix=inputs=2:duration=first[aout]
  " \
  -map 0:v -map "[aout]" \
  -c:v libx264 -crf 18 -r 30 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  output/<slug>/<slug>_final.mp4
```

**v2 Volume table (UPDATED):**
| Track | Volume |
|-------|--------|
| Original SFX | 0 (no audio) |
| TTS narrator | 1.5 (150%, foreground) |
| Music BGM | **0.15** (15%, was 0.20-0.25) |

**Parameters:**
- Narrator volume: `1.5` (150%, foreground)
- Music volume: `0.15` (15% — instrumental, don't override narrator)
- Xfade: `1s` intro↔body, body↔outro (smoother than 0.5s)
- `duration=first` — audio fits video length
- NO `-an` flag — must include audio

### Output

```
output/<slug>/concat_scenes.mp4     # video, no audio
output/<slug>/<slug>_final.mp4      # final: video + narrator + music
output/<slug>/tts/narrator_full.wav # narrator WAV
```

**Verify with ffprobe:**
```bash
ffprobe output/<slug>/<slug>_final.mp4 | grep Duration
# Mục tiêu: 5:00 - 8:00 (300-480 giây)

ffmpeg -i output/<slug>/<slug>_final.mp4 -af "volumedetect" -f null - 2>&1 | grep mean_volume
# Mục tiêu: -30 đến -10 dB (không -inf, âm thanh rõ)
```

---

## Bước 7: Optional — Branding + Caption

### 7a. Add brand logo

```bash
/fk-brand-logo <video_id>
# Watermark top-right corner
```

### 7b. Generate captions

```bash
/fk-gen-caption <video_id>
# Auto-caption từ narrator_full.wav → .vtt file
```

---

## Configuration chuẩn (quick ref)

| Tham số | Giá trị |
|---------|---------|
| Resolution | 1920×1080 (16:9) |
| FPS | 30 |
| Codec video | h264, yuv420p |
| Codec audio | aac, 192k, 48kHz, stereo |
| Narrator voice | `Phap_Van_podcast_TTS` |
| Narrator speed | 0.85 |
| Narrator volume | 1.5× (150%) |
| Music volume | **0.15× (15%, was 0.20-0.25)** |
| Xfade duration | 1s (intro↔body, body↔outro) |
| Ken Burns motions | zoom_in/out, pan_left/right (no consecutive repeat) |
| Target duration | 5:00 - 8:00 |
| Scenes | 7-10 (1 hook + 5-7 sections + 1 outro) |
| Music type | **Instrumental ONLY, no vocals/lyrics** |
| Section duration | 30-90s each |

---

## Image prompt template (English)

```
[Subject related to book theme] in [setting],
[Composition: wide shot / medium shot / close-up].

[Mood: contemplative / inspiring / dramatic / introspective].

Cinematic photography, soft golden lighting, depth of field, 16:9 horizontal frame, 4K.

Negative: subtitles, watermark, text overlay, logos, people (unless core to concept).
```

**Example (Atomic Habits):**
```
A person forming a new habit, tiny stone becoming a mountain,
in a serene morning environment.

Composition: wide shot showing before and after.
Mood: inspiring, hopeful, gradual transformation.

Cinematic photography, soft morning light, depth of field, 16:9 horizontal frame, 4K.

Negative: subtitles, watermark, text, logos.
```

---

## Narrator script template (Vietnamese, NO book mention)

**Hook (15-30s, ~20-22 từ):**
```
[Opening powerful idea — NO book name] [Why it matters] [Teaser for content].
Example: "Những thay đổi nhỏ nhất có thể dẫn đến kết quả lớn nhất — hôm nay ta sẽ khám phá cách đó."
```

**Section (60-90s, ~20-22 từ/câu × 3-4 câu):**
```
[Key concept] [Explanation or example] [Real-world application — NO book reference].
```

**Outro (30-45s, ~20-22 từ, CRITICAL NO CTA):**
```
[Closing reflection] [Call to wisdom/action — NOT to book] [Final contemplative question].
Example: "Hôm nay bạn sẽ thực hiện một thay đổi nhỏ nào để bắt đầu hành trình?"
AVOID: "Đọc sách để...", "Subscribe để...", "Follow để..."
```

---

## Checklist nhanh

```
[ ] Extract script: POST /api/book/extract-script → hook + 5-7 sections + outro
[ ]   VERIFY: NO book name/author in narrator_text (metadata in source_book only)
[ ]   VERIFY: outro is reflection, NOT CTA
[ ] /fk-create-project — HORIZONTAL, realistic, 7-10 scenes
[ ]   Patch narrator_text per scene (20-22 từ, NO book mention)
[ ] /fk-gen-images — 1 wave, all scenes GENERATE_IMAGE
[ ] Apply Ken Burns: POST /api/ken-burns/clip per scene (NO text overlay)
[ ]   Vary motions (zoom_in/out, pan_left/right), no consecutive repeat
[ ] Gen TTS: Concat all narrator_text → 1 file, Phap_Van_podcast_TTS speed 0.85
[ ] Gen music: Gemini Lyria Pro
[ ]   Option A: Single 7-8min track (simpler)
[ ]   Option B: 3 tracks INTRO + BODY + OUTRO (better transitions)
[ ]   CRITICAL: "instrumental ONLY, no vocals, no lyrics" in prompt
[ ] Concat + mix: xfade scenes (1s for 3-track option), blend narrator (1.5×) + music (0.15×)
[ ] Verify final video:
[ ]   Duration: 5:00 - 8:00
[ ]   Resolution: 1920×1080, 30fps
[ ]   mean_volume: -30 to -10 dB
[ ]   NO vocal/lyrics in music background
[ ] /fk-brand-logo (optional)
[ ] /fk-gen-caption (optional, show source_book metadata)
```

---

## Series Best Practices

- Run extract-chapters lần đầu để có content calendar (tối đa 30 chapters)
- 1 topic = 1 video → tránh trùng nội dung giữa các video trong series
- Naming convention output: `output/<book_slug>/episode_<NN>_<topic_slug>/<slug>_final.mp4`
- Music reuse: 1 track Lyria có thể dùng cho 3-5 episodes (cùng vibe long-form podcast)
- Image gen: mỗi episode tạo project Flow riêng (7-10 ảnh × N episodes = quota management)
- Quota: chú ý Imagen quota nếu run series 10+ episodes (300+ scene images)
- Voice consistency: dùng Phap_Van_podcast_TTS để tất cả episodes có cùng narrator voice

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| Narrator nhắc tên sách | extract-script cũ, narrator text chứa book name | Verify hook/sections/outro NO "Sách...", "Tác giả..." |
| Outro có CTA ("subscribe/read") | Prompt extract-script sai | Rerun extract-script, verify outro is reflection ONLY |
| Music có vocal/lyrics | Gemini prompt không rõ ràng | Thêm "instrumental ONLY, no vocals, no lyrics, no singing" đầu prompt |
| TTS dài hơn video | Narrator text quá dài ở speed 0.85 | Rút ngắn mỗi câu xuống 19-20 từ, hoặc tăng speed lên 0.90 |
| Ken Burns motion lặp liên tiếp | Chiến lược motion không random | Dùng rotation: idx % 4 → motion type |
| Narrator bị cắt giữa câu | >22 từ thực tế → TTS bị cap | Đếm lại bằng Python split(), giới hạn 22 |
| Music quá to che TTS | Volume music > 0.15 | Giảm xuống 0.10-0.12 |
| Narrator quá yếu | Volume narrator < 1.5 | Tăng lên 1.5-2.0, kiểm tra amix duration=first |
| mean_volume = -inf | Audio track bị mất | Kiểm tra NO `-an` flag, dùng `-ar 48000 -ac 2` |
| Intro/outro bị cắt (3-track) | atrim window quá nhỏ | Mở rộng atrim=0:4 hoặc 0:5 |
| xfade stall | Filter quá phức tạp | Giảm xfade duration 1s → 0.5s hoặc tách video/audio |
| Image generation quota | Too many scenes | Batch request sau, hoặc dùng 5 scenes instead of 10 |
| Topic extraction lọc sai | Topic string không khớp chapter outline | Verify topic tên chính xác, không typo |
| Extract-chapters API error | Mode/source schema sai | Check mode: "auto" vs "manual", source.outline format |

---

## Ví dụ đã làm

| Sách | OUTDIR | Đặc điểm | Duration | Music |
|------|--------|----------|----------|-------|
| Atomic Habits (v2) | `output/atomic_habits_vi_v2` | 7 scenes, NO book mention, instrumental BGM | 6:45 | Single continuous 7min |
| The Alchemist (v2) | `output/alchemist_vi_v2` | 8 scenes, 3-track music (intro/body/outro) | 7:30 | 3-track with xfade |

---

## Khi nào cần /fk-doctor

```
[ ] TTS generation timeout / rate limit
[ ] Ken Burns API returns HTTP 5xx
[ ] /fk-gen-images fails multiple scenes
[ ] Music generation quota exceeded
[ ] Extension not connected to Flow
```

---

## Credits & Tham khảo

- Voice template: Phap_Van_podcast_TTS (slow podcast narrator)
- Music model: Gemini Lyria Pro (music generation)
- Narrator word count: 20-22 từ per sentence (project memory)
- Image prompts: English only (Flow convention)
