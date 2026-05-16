# fk-video-book-summary — Classic Literature Podcast (International YouTube)

Long-form English podcast video (**10-15 minutes per chapter**) from a public-domain book — image montage with Ken Burns motion + English narrator + instrumental BGM. Designed for international YouTube channels covering classic literature chapter-by-chapter.

**4-act script structure:** Hook (1m) → Summary (5-7m) → Analysis (3-5m) → Outro (1m).

Usage:
```
/fk-video-book-summary "<book title>" --chapter "<chapter name or N>" [--source pdf:/path/to/book.pdf] [--voice Andrew_TTS] [--target-minutes 12]
```

Example:
```
/fk-video-book-summary "The Great Gatsby" --chapter "Chapter 1: Nick Arrives in West Egg"
/fk-video-book-summary "Pride and Prejudice" --chapter 3
/fk-video-book-summary "The Old Man and the Sea" --chapter "Part 1: The 84th Day"
```

---

## Copyright-Safe Book Selection (CRITICAL)

**ONLY use Public Domain works** (author deceased >70 years). Avoid modern bestsellers (Atomic Habits, The Alchemist, etc.) — they trigger YouTube copyright strikes.

| Recommended book | Author | PD status | Series potential |
|------------------|--------|-----------|------------------|
| The Little Prince | Saint-Exupéry (d.1944) | PD in most regions | 27 chapters |
| Pride and Prejudice | Jane Austen (d.1817) | Universal PD | 61 chapters |
| The Great Gatsby | F. Scott Fitzgerald (d.1940) | PD US (2021+) | 9 chapters |
| The Old Man and the Sea | Hemingway (d.1961) | Region-dependent | 1 long arc (split into 5-7 acts) |
| Wuthering Heights | Brontë (d.1848) | Universal PD | 34 chapters |
| Frankenstein | Mary Shelley (d.1851) | Universal PD | 24 chapters |
| Crime and Punishment | Dostoevsky (d.1881) | Universal PD | 6 parts × 7 chapters |
| Dracula | Bram Stoker (d.1912) | Universal PD | 27 chapters |
| Sherlock Holmes (Adventures) | Doyle (d.1930) | Universal PD | 12 stories |
| Anna Karenina | Tolstoy (d.1910) | Universal PD | 8 parts |

**Verify before scripting:** Check Gutenberg.org availability. If the full English text is on Gutenberg → safe to quote.

---

## Workflow Overview

```
Step 0: Extract chapter script (4-act)
        ↓ POST /api/book/extract-script (mode: chapter_podcast)
Step 1: Create project (HORIZONTAL, 16:9, period-appropriate aesthetic)
        ↓ /fk-create-project
Step 2: Generate scene images (12-15 scenes)
        ↓ /fk-gen-images
Step 3: Apply Ken Burns motion (vary per act)
        ↓ POST /api/ken-burns/clip
Step 4: Generate English TTS (full narration concat)
        ↓ POST /api/tts/generate (voice: Andrew_TTS, speed 0.90)
Step 5: Generate instrumental BGM (3 tracks for act transitions)
        ↓ POST /api/gemini/browser/generate-music
Step 6: Concat clips + mix narrator + music
        ↓ ffmpeg xfade + amix
Step 7: (Optional) Branding + YouTube SEO + auto-caption
        ↓ /fk-brand-logo + /fk-youtube-seo + /fk-gen-caption
```

---

## Step 0: Extract Chapter Script (4-Act Structure)

**Endpoint:** `POST /api/book/extract-script`

```bash
curl -X POST http://127.0.0.1:8100/api/book/extract-script \
  -H "Content-Type: application/json" \
  -d '{
    "book_name": "The Great Gatsby",
    "format": "chapter_podcast",
    "language": "en",
    "target_minutes": 12,
    "options": {
      "chapter": "Chapter 1: Nick Arrives in West Egg",
      "audience": "international_youtube",
      "structure": "4_act"
    }
  }'
```

### Required Response Schema (4-act)

```json
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "chapter": "Chapter 1: Nick Arrives in West Egg",
  "hook": {
    "narrator_text": "Welcome back, fellow readers. Today we open 'The Great Gatsby' — and the first chapter holds a line that defines the entire novel...",
    "scene_prompt": "1920s art deco mansion at dusk, golden light spilling from windows, jazz era opulence, painterly cinematic",
    "duration_target_sec": 55
  },
  "summary": [
    {
      "section": 1,
      "title": "Nick's Arrival",
      "narrator_text": "First, our narrator Nick Carraway moves to West Egg, a fictional Long Island suburb...",
      "scene_prompt": "young man in 1920s suit arriving at small cottage by the bay, vintage car, golden hour",
      "time_connector": "First",
      "duration_target_sec": 55
    },
    { "section": 2, "narrator_text": "Next, Nick visits his cousin Daisy across the bay...", "time_connector": "Next" },
    { "section": 3, "narrator_text": "Suddenly, the conversation shifts when a phone call interrupts...", "time_connector": "Suddenly" },
    { "section": 4, "narrator_text": "Later that evening, Nick returns home and sees his neighbor...", "time_connector": "Later" },
    { "section": 5, "narrator_text": "Finally, the chapter closes with Gatsby reaching toward the green light...", "time_connector": "In the end" }
  ],
  "analysis": [
    {
      "section": 1,
      "topic": "The Green Light Symbol",
      "narrator_text": "The green light isn't just a light — it's the symbol of the unattainable American Dream...",
      "scene_prompt": "single green lantern across dark water at night, mist, ethereal mood, symbolic",
      "duration_target_sec": 60
    },
    { "section": 2, "topic": "Nick as Unreliable Narrator", "narrator_text": "Notice how Nick claims to be 'inclined to reserve all judgments'..." },
    { "section": 3, "topic": "Class Geography (East vs West Egg)", "narrator_text": "Fitzgerald uses geography as character..." },
    { "section": 4, "topic": "Real-World Lesson", "narrator_text": "What this teaches us today: the dream of reinvention often arrives with a price tag we cannot read..." }
  ],
  "outro": {
    "narrator_text": "If this opened the book for you, hit subscribe so you don't miss Chapter 2, where we meet Tom and Myrtle. Drop a comment: what does the green light mean to you? See you next chapter.",
    "scene_prompt": "open book on wooden table beside a green lantern, warm reading lamp, inviting close",
    "duration_target_sec": 55,
    "cta_subscribe": true,
    "comment_question": "What does the green light mean to you?",
    "next_chapter_tease": "Chapter 2: Meeting Tom and Myrtle"
  }
}
```

### Word-Count Targets (English, narrator speed 0.90)

| Act | Sections | Words/section | Total words | Total minutes |
|-----|----------|---------------|-------------|---------------|
| Hook | 1 | 110-130 | 110-130 | ~1:00 |
| Summary | 5-7 | 100-130 | 550-900 | 5-7:00 |
| Analysis | 3-5 | 100-160 | 350-700 | 3-5:00 |
| Outro | 1 | 110-130 | 110-130 | ~1:00 |
| **TOTAL** | **10-14** | — | **1,100-1,860** | **10-15:00** |

**Verify after extract:**
- Hook MUST include book title, author, chapter, and a quote/question hook
- Each summary section MUST begin with a time connector (First/Next/Suddenly/Then/Later/Finally/In the end)
- Each analysis section MUST address WHY (motivation/metaphor/lesson), not just WHAT
- Outro MUST include: subscribe CTA + comment question + next-chapter tease
- All narrator_text in English, idiomatic, podcast cadence

---

## Step 1: Create Project (`/fk-create-project`)

| Param | Value |
|-------|-------|
| Orientation | `HORIZONTAL` (16:9) |
| Material | `realistic` or `painterly` (period-appropriate) |
| Resolution | 1920×1080 |
| Scenes | 12-15 (1 hook + 5-7 summary + 3-5 analysis + 1 outro) |
| Language | English |
| FPS | 30 |
| Slug | `<book_slug>_ch<NN>_<chapter_slug>` |

**Aesthetic by book (image material style):**

| Book | Aesthetic | Material profile |
|------|-----------|------------------|
| The Great Gatsby | Art Deco, jazz era, gold/black, opulent | `cinematic_1920s` |
| Pride and Prejudice | Regency England, pastel, painterly | `painterly_regency` |
| The Little Prince | Watercolor, dreamy, surreal pastel | `watercolor_dreamy` |
| The Old Man and the Sea | Cuban coast, weathered, ocean, sunset | `cinematic_realist` |
| Wuthering Heights | Yorkshire moors, gothic, brooding | `gothic_moors` |
| Frankenstein | Gothic, candlelit, anatomical, shadows | `gothic_dark` |
| Dracula | Victorian gothic, mist, crimson, candles | `gothic_victorian` |
| Crime and Punishment | 19th century St. Petersburg, dim, oppressive | `russian_realist` |
| Sherlock Holmes | Foggy London, gas lamps, Victorian | `victorian_noir` |

Set via `/fk-add-material` if needed.

### Scene Layout

| Scene idx | Act | Duration | Narrator | Image focus |
|-----------|-----|----------|----------|-------------|
| 0 | HOOK | 55-65s | hook.narrator_text | Iconic image, book theme |
| 1-N | SUMMARY | 50-60s each | summary[i].narrator_text | Plot moment per section |
| N+1..M | ANALYSIS | 55-70s each | analysis[i].narrator_text | Symbol/character close-up |
| M+1 | OUTRO | 55-65s | outro.narrator_text | Closing/inviting visual |

Patch `narrator_text` into each scene metadata for reference.

---

## Step 2: Generate Scene Images (`/fk-gen-images`)

Single wave, all 12-15 scenes via `GENERATE_IMAGE`. Poll 15s until `done: true`.

**Image prompt template (English):**

```
[Subject from scene_prompt] in [period-appropriate setting],
[Composition: wide shot / medium shot / close-up / symbolic close-up].

Mood: [contemplative / dramatic / nostalgic / brooding / hopeful].

[Aesthetic profile from book table].
Cinematic, painterly, depth of field, 16:9 horizontal frame, 4K.

Negative: subtitles, watermark, text overlay, modern objects, anachronisms,
contemporary clothing, logos, captions.
```

**Period-anachronism guard:** Always include the book's era in the prompt (e.g., "1920s", "Regency England 1810s", "Victorian London 1880s") and add anachronistic items to the negative list.

---

## Step 3: Apply Ken Burns Motion

**Motion strategy per act** (vary, no two consecutive same):

| Act | Preferred motions |
|-----|-------------------|
| Hook | `zoom_in` (intensify attention) |
| Summary | Rotate: `pan_left` → `pan_right` → `zoom_in` → `pan_left` → `zoom_out` ... |
| Analysis | `zoom_in` (focus on symbol) or `zoom_out` (reveal context) |
| Outro | `zoom_out` (release, breathe) |

**Endpoint:** `POST /api/ken-burns/clip`

```bash
curl -X POST http://127.0.0.1:8100/api/ken-burns/clip \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "output/<slug>/images/scene_<N>.png",
    "duration_seconds": <55-65>,
    "motion": "zoom_in",
    "resolution": "1920x1080",
    "output_path": "output/<slug>/ken-burns/scene_<N>_<motion>.mp4"
  }'
```

**Duration per scene = narrator_text duration at speed 0.90 + 1-2s padding.**

---

## Step 4: Generate English TTS Narrator

### Concat all narrator texts in order

```
{hook} {summary[0]} {summary[1]} ... {summary[N]} {analysis[0]} ... {analysis[M]} {outro}
```

Insert a `.` between sections to enforce sentence-final intonation. Optionally insert `<break time="500ms"/>` if your TTS backend supports SSML — otherwise rely on punctuation.

### Generate single TTS file

**Endpoint:** `POST /api/tts/generate`

```bash
curl -X POST http://127.0.0.1:8100/api/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<full concatenated English narration>",
    "ref_audio": "output/_shared/tts_templates/Andrew_TTS.wav",
    "ref_text": "Welcome back, dear listener. Today, we open a book that has lived for over a hundred years — a story of dreams reaching across dark water, of green lights and golden parties, of voices that whisper across time.",
    "speed": 0.90,
    "language": "en",
    "output_path": "output/<slug>/tts/narrator_full.wav"
  }'
```

**Voice defaults:**
- Default: `Andrew_TTS` (warm low-mid male, American accent, contemplative literary podcast narrator)
- Alternative: `narrator_male_en` (generic English male)
- Override via `--voice <template_name>` (must exist in `output/_shared/tts_templates/templates.json`)

**Verify:**
- Duration within ±5% of `target_minutes`
- TTS duration < total Ken Burns clip duration (≥1s breathing room)
- mean_volume between -25 and -10 dB

---

## Step 5: Generate Instrumental BGM (3-track for act transitions)

**CRITICAL:** All music prompts MUST include "instrumental ONLY, no vocals, no lyrics, no singing".

### Track 1: HOOK + SUMMARY intro (cinematic open)
```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, cinematic literary intro, soft piano + warm strings, period-appropriate (e.g., 1920s if Gatsby, baroque if Austen), contemplative, podcast opener, fade-friendly, 3 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 3,
    "output_path": "output/<slug>/music/01_intro.mp3"
  }'
```

### Track 2: SUMMARY body (steady ambient)
```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, calm ambient piano, low energy, podcast background music suitable for narration overlay, no melody peaks, period-appropriate, 7 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 7,
    "output_path": "output/<slug>/music/02_body.mp3"
  }'
```

### Track 3: ANALYSIS + OUTRO (reflective, uplifting close)
```bash
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "instrumental only, no vocals, no lyrics, reflective piano + gentle strings, hopeful resolution, emotional but restrained, podcast closer, fade-friendly, 4 minutes",
    "model": "gemini-lyria-pro",
    "duration_minutes": 4,
    "output_path": "output/<slug>/music/03_outro.mp3"
  }'
```

**Always save as MP3** (smaller, audio-only — Gemini Lyria returns MP4, transcode with ffmpeg `-vn -c:a libmp3lame -b:a 192k`).

---

## Step 6: Concat Clips + Mix Audio

### 6a. Concat all Ken Burns clips (xfade 1s)

```bash
ffmpeg \
  -i output/<slug>/ken-burns/scene_0_zoom_in.mp4 \
  -i output/<slug>/ken-burns/scene_1_pan_left.mp4 \
  ... \
  -i output/<slug>/ken-burns/scene_<N>_zoom_out.mp4 \
  -filter_complex "<xfade chain 1s>" \
  -map "[vout]" \
  -c:v libx264 -crf 18 -r 30 -pix_fmt yuv420p \
  -an \
  output/<slug>/concat_scenes.mp4
```

### 6b. Mix narrator + 3-track BGM

```bash
ffmpeg -y \
  -i output/<slug>/concat_scenes.mp4 \
  -i output/<slug>/tts/narrator_full.wav \
  -i output/<slug>/music/01_intro.mp3 \
  -i output/<slug>/music/02_body.mp3 \
  -i output/<slug>/music/03_outro.mp3 \
  -filter_complex "
    [1:a]volume=1.5[narrator];
    [2:a]volume=0.12[m1];
    [3:a]volume=0.12[m2];
    [4:a]volume=0.12[m3];
    [m1][m2]acrossfade=d=2:c1=tri:c2=tri[m12];
    [m12][m3]acrossfade=d=2:c1=tri:c2=tri[music_mix];
    [music_mix][narrator]amix=inputs=2:duration=first:dropout_transition=0[aout]
  " \
  -map 0:v -map "[aout]" \
  -c:v libx264 -crf 18 -r 30 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  output/<slug>/<slug>_final.mp4
```

### Volume table

| Track | Volume | Notes |
|-------|--------|-------|
| Original scene (video) | muted (`-an` upstream) | no original audio |
| Narrator | 1.5× | foreground |
| Music BGM | **0.12×** | sit clearly under English narration (English is more sensitive to muddy mids than Vietnamese — lower than 0.15 default) |
| xfade music | 2s | smooth act transitions |

### Verify

```bash
ffprobe output/<slug>/<slug>_final.mp4 2>&1 | grep Duration  # target 10:00 – 15:00
ffmpeg -i output/<slug>/<slug>_final.mp4 -af "volumedetect" -f null - 2>&1 | grep mean_volume  # -20 to -10 dB
```

---

## Step 7 (Optional): Branding, SEO, Captions

### 7a. Brand logo
```bash
/fk-brand-logo <video_id>  # bottom-right watermark, channel-aware
```

### 7b. YouTube SEO metadata
```bash
/fk-youtube-seo <video_id> --language en --format chapter_podcast
# Generates: title, description, tags, chapters timestamps, thumbnail brief
```

**Recommended YouTube title pattern:**
```
<Book> Explained — Chapter <N>: <Chapter Name> | Classic Literature Podcast
```
Example: `The Great Gatsby Explained — Chapter 1: Nick Arrives in West Egg | Classic Literature Podcast`

**Description template:**
```
In this episode we open <Book> by <Author>, Chapter <N>: <Chapter Name>.

Chapters:
00:00 Hook
01:00 Summary
07:30 Analysis & Lessons
11:30 Outro

📚 Source text: Project Gutenberg (public domain)
🎙️ Narrated by AI for educational discussion
💬 Comment below: <comment_question>
🔔 Subscribe for one chapter per week

#ClassicLiterature #BookPodcast #<BookTag>
```

### 7c. Auto-caption (.vtt)
```bash
/fk-gen-caption <video_id> --language en
```

Required for international SEO and accessibility.

---

## Output Folder Structure

```
output/<book_slug>/
├── ch01_<chapter_slug>/
│   ├── images/                  scene_0.png ... scene_N.png
│   ├── ken-burns/               scene_0_zoom_in.mp4 ...
│   ├── tts/                     narrator_full.wav + per-section if needed
│   ├── music/                   01_intro.mp3, 02_body.mp3, 03_outro.mp3
│   ├── concat_scenes.mp4        video-only montage
│   ├── <slug>_final.mp4         final mixed video
│   ├── <slug>_final_branded.mp4 with logo (optional)
│   ├── captions.vtt             auto-generated
│   ├── youtube_seo.json         title/description/tags/chapters
│   └── script.json              the 4-act extract response (archive)
├── ch02_<chapter_slug>/...
└── series_calendar.json         chapter list + upload schedule
```

---

## Series Workflow (One Book → Multiple Episodes)

### Step A: Extract chapter list (once per book)

```bash
curl -X POST http://127.0.0.1:8100/api/book/extract-chapters \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "auto",
    "source": {"pdf_path": "/path/to/great_gatsby.pdf"},
    "max_chapters": 9
  }'
```

Save response to `output/<book_slug>/series_calendar.json`.

### Step B: One chapter = one episode

Loop or run on-demand:
```bash
/fk-video-book-summary "The Great Gatsby" --chapter "Chapter 1: Nick Arrives"
/fk-video-book-summary "The Great Gatsby" --chapter "Chapter 2: Tom and Myrtle"
...
```

### Step C: Upload schedule
- Use `/fk-youtube-upload` per episode
- Recommended cadence: 1 chapter/week (gives audience time to read along)
- Use `/fk-podcast-book` pattern for calendar+retry orchestration if running many episodes

---

## Quick Reference — Standard Config

| Param | Value |
|-------|-------|
| Resolution | 1920×1080 (16:9) |
| FPS | 30 |
| Video codec | h264, yuv420p, crf 18 |
| Audio codec | aac, 192k, 48kHz, stereo |
| Narrator voice | `Andrew_TTS` (default) |
| Narrator speed | 0.90 |
| Narrator volume | 1.5× |
| Music volume | **0.12×** (English narration sensitive) |
| Music type | Instrumental ONLY, period-appropriate |
| xfade (video) | 1s |
| xfade (music) | 2s |
| Target duration | 10:00 – 15:00 |
| Scenes | 12-15 (1 + 5-7 + 3-5 + 1) |
| Words total | 1,100 – 1,860 |
| NO text overlay | (per project memory) |

---

## Checklist

```
[ ] Verify book is PUBLIC DOMAIN (Gutenberg.org check)
[ ] Extract 4-act script: POST /api/book/extract-script (chapter_podcast format)
[ ]   Hook: book/author/chapter named + hook quote/question
[ ]   Summary: 5-7 sections, each starts with time connector
[ ]   Analysis: 3-5 sections, WHY/motivation/metaphor/lesson
[ ]   Outro: subscribe CTA + comment question + next-chapter tease
[ ]   Word count: 1,100 – 1,860 total
[ ] /fk-create-project — HORIZONTAL, period-appropriate aesthetic, 12-15 scenes
[ ]   Patch narrator_text per scene
[ ] /fk-gen-images — 1 wave, period-accurate, no anachronisms
[ ] Ken Burns clips: vary motions, duration = TTS section + 1-2s padding
[ ] TTS: voice=Andrew_TTS, speed=0.90, language=en
[ ] Music: 3 tracks (intro/body/outro), instrumental ONLY, MP3, period-appropriate
[ ] Concat + mix: xfade 1s video, 2s music, narrator 1.5×, music 0.12×
[ ] Verify final:
[ ]   Duration 10:00–15:00
[ ]   1920×1080 30fps
[ ]   mean_volume -20 to -10 dB
[ ]   No vocals/lyrics in music
[ ]   No text overlay
[ ] /fk-brand-logo (optional)
[ ] /fk-youtube-seo --language en --format chapter_podcast
[ ] /fk-gen-caption --language en
[ ] /fk-youtube-upload (when ready)
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Narrator mispronounces character names | TTS phonetic gap | Add IPA hint or rewrite name phonetically in script |
| Outro missing subscribe CTA | extract-script returned reflection-only | Re-run with `audience: international_youtube` flag |
| Anachronism in image (modern objects) | Era not in prompt | Add explicit decade/century + reinforce in negative list |
| Music has vocals | Prompt vague | Add "instrumental ONLY, no vocals, no lyrics, no singing" at prompt start |
| Final >15min | Word count exceeded | Trim 1-2 analysis sections OR raise speed to 0.95 |
| Final <10min | Too few sections | Add summary section or expand analysis to 5 sections |
| English narration muddy under music | Music too loud | Drop music volume to 0.10× |
| Copyright strike risk | Modern book used | SWITCH to public domain title before regen |
| TTS cuts mid-sentence | Section >130 words | Split at natural sentence break |
| Ken Burns motion repeats | Motion not rotated | Use `motion_table[idx % 4]` rotation |

---

## When to Call `/fk-doctor`

```
[ ] /api/book/extract-script HTTP 5xx or schema mismatch
[ ] TTS rate limit / quota
[ ] /api/ken-burns/clip stall
[ ] Music generation quota exceeded (Gemini Lyria)
[ ] Flow extension disconnected during image batch
[ ] YouTube upload HttpError after /fk-youtube-upload
```

---

## Credits & Conventions

- Source texts: Project Gutenberg (public domain)
- Voice template: `Andrew_TTS.wav` (default — warm contemplative male, American accent, literary podcast tone)
- Music model: Gemini Lyria Pro (instrumental, period-appropriate)
- Format: 4-act podcast (Hook / Summary / Analysis / Outro) — script structure spec per channel brief
- Audience: International YouTube, English-speaking
- Image style: Period-appropriate cinematic/painterly, no anachronisms
- Word count cadence: ~135 wpm @ TTS speed 0.90
- NO text overlay (per project memory `feedback-no-text-overlay-podcast`)
