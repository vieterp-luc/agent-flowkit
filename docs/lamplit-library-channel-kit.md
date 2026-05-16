# Lamplit Library — Channel Setup Kit

Reference document for YouTube + podcast platform setup.

---

## 1. Channel Basics

| Field | Value |
|-------|-------|
| **Channel name** | Lamplit Library |
| **Subtitle** | Audiobooks & Summaries |
| **Mission line** | Classics, one chapter at a time. |
| **Handle** (suggested) | `@lamplitlibrary` |
| **Channel URL** (target) | `youtube.com/@lamplitlibrary` |
| **Country** | (set per uploader profile) |
| **Default language** | English |
| **Audience** | International, English-speaking, literary readers |
| **Content niche** | Public-domain classic literature, chapter-by-chapter podcast/audio-essay |

---

## 2. About Description

**Short version (for YouTube About — under 1,000 chars):**

> Welcome to **Lamplit Library** — where the great classics of public-domain literature come alive, one chapter at a time.
>
> Each episode is a 10–15 minute English-narrated walkthrough of a single chapter: a hook, the plot summary, character and symbolic analysis, and a real-world insight you can carry forward. From Mary Shelley's *Frankenstein* to Jane Austen, the Brontës, Dostoevsky, and Stoker — we read these books slowly, so you don't have to.
>
> An audiobook companion, a literary insight column, and cinematic painterly visuals — all by candlelight.
>
> 🕯️ A new chapter every week. Subscribe so you don't miss the next page.
>
> 📚 All source texts are public domain (Project Gutenberg). Narration by AI for educational discussion.

**Ultra-short version (Apple Podcasts / Spotify, ~150 chars):**

> Classic literature read slowly, one chapter at a time. 10–15 min episodes of plot summary, character analysis, and timeless insights — by candlelight.

---

## 3. Brand Identity

### Visual
- **Aesthetic:** Gothic Romantic painterly (Caspar David Friedrich + Goya + Fuseli + Vigée Le Brun)
- **Logo mark:** Ornate Trajan serif **L** with brass hanging lantern + ribbon flourish
- **Color palette:**
  - Parchment cream `#F5EBD7`
  - Deep umber `#3C2816`
  - Light umber `#6E5537`
  - Brass / gold accent (lantern flame)
- **Typography:** Baskerville (Bold for headers, Regular for body)
- **Mood:** Candlelit, contemplative, premium-library, never harsh-modern

### Voice
- **Narrator template:** `Andrew_TTS` (warm low-mid pitch, American accent, contemplative literary podcast narrator)
- **TTS speed:** 0.90 (slightly slower than natural — podcast pacing)
- **Pace target:** ~135 wpm

### Asset Files
Path: `output/frankenstein_classics_en/logos/`

| File | Size | Use |
|------|------|-----|
| `avatar_1024.png` | 1024×1024 | YouTube profile / Apple / Spotify square |
| `avatar_1024_circle_preview.png` | 1024×1024 | Preview under YouTube's circle crop |
| `banner_2560.png` | 2560×1440 | YouTube channel banner |
| `watermark_400.png` | 400×120 transparent | Video corner sticker |
| `logo_mark_transparent.png` | 1117×2000 | Source L monogram (transparent BG) |

---

## 4. Content Format (per episode)

### 4-act script structure (10–15 min)
1. **Hook (1 min, 110-130 words)** — book title, author, chapter name + a quote or question that defines the chapter
2. **Summary (5–7 min, 5-7 sections × 100-130 words)** — plot retold; each section begins with a time connector (First / Next / Suddenly / Then / Later / Finally)
3. **Analysis (3–5 min, 3-5 sections × 100-160 words)** — character motivations, metaphors, themes, real-world insight
4. **Outro (1 min, 110-130 words)** — subscribe CTA + engagement question + tease next chapter

### Video build pipeline
- 12-15 scenes per episode (1 hook + 5-7 summary + 3-5 analysis + 1 outro)
- Resolution: 1920×1080 @ 30 fps
- Painterly oil-painting scene images (consistent project entities across all episodes for character continuity)
- Ken Burns motion (zoom_in / zoom_out / pan_left / pan_right, no consecutive repeat)
- 3-track instrumental BGM (intro / body / outro) at 0.12× volume under narrator at 1.5× volume
- xfade scene transitions 1s, music crossfades 3s
- Final mix verified: -20 to -10 dB mean_volume

---

## 5. SEO / Discovery

### Title pattern
```
<Book Title> Explained — Episode <N>: <Chapter Name> | Lamplit Library
```
Examples:
- `Frankenstein Explained — Episode 1: Walton's Letters | Lamplit Library`
- `Pride and Prejudice Explained — Chapter 3: The Netherfield Ball | Lamplit Library`

### Description template (per video)
```
In this episode we open <Book Title> by <Author>, <Chapter Name>.

Chapters:
00:00 Hook
01:00 Summary
07:30 Analysis & Lessons
11:30 Outro

📚 Source text: Project Gutenberg (public domain)
🎙️ Narrated by AI for educational discussion
💬 Comment below: <comment_question_from_outro>
🔔 Subscribe for one chapter per week

Visit our library — <book series playlist link>

#ClassicLiterature #BookPodcast #<BookTag> #LamplitLibrary
```

### Channel tags (YouTube About page, ~500 char total)
```
classic literature, book summary, audiobook, chapter analysis, gothic literature,
literary podcast, frankenstein, mary shelley, wuthering heights, jane austen,
english literature, book club, public domain books, great books podcast, reading
podcast, classics summary, book analysis, literature explained
```

---

## 6. Series Roadmap

### Launch — Q1 2026
- **Frankenstein** (Mary Shelley) — 24 chapters, ride Netflix del Toro adaptation Nov 2025 momentum

### Q2 2026
- **Wuthering Heights** (Brontë) — 34 chapters, ride WB film Feb 2026
- **Dracula** (Stoker) — 27 epistolary entries, ride Luc Besson film Feb 2026

### Q3 2026
- **Crime and Punishment** (Dostoevsky) — 6 parts × ~7 chapters, BookTok crossover

### Tentative
- Pride and Prejudice
- Jane Eyre
- The Picture of Dorian Gray
- The Metamorphosis (Kafka, single novella)
- Sherlock Holmes (Doyle, short stories)
- Anna Karenina

**Cadence:** 1 chapter / week recommended (give audience reading time + steady algorithm signal). Sunday US evening upload slot.

---

## 7. Production Stack (reference)

| Stage | Tool / Skill |
|-------|--------------|
| Project + entities | `/fk-create-project`, Flow image gen with multi-panel character sheets |
| Script extraction | `POST /api/book/extract-script` with `format: "chapter_podcast"` |
| Scene image gen | `/fk-gen-images` |
| Ken Burns motion | `POST /api/ken-burns/clip` |
| English narration | `POST /api/tts/generate` with `template: "Andrew_TTS"`, `speed: 0.9` |
| Instrumental music | `POST /api/gemini/browser/generate-music` (Lyria Pro) |
| Concat + mix | ffmpeg xfade + amix `duration=longest` + dynaudnorm |
| Brand watermark | ffmpeg overlay `watermark_400.png` |
| YouTube upload | `/fk-youtube-upload` |
| SEO metadata | `/fk-youtube-seo` (with `chapter_podcast` format) |
| Auto-captions | `/fk-gen-caption --language en` |

---

## 8. Channel Policy / Legal

- **Source texts:** All books are public domain in the US (author deceased >70 years). Verified via Project Gutenberg.
- **AI disclosure:** Description always states "Narrated by AI for educational discussion."
- **Copyright avoidance:** No modern bestsellers, no translation copyright (use US-PD translations only for non-English originals, e.g., Constance Garnett's Dostoevsky).
- **Fair use:** Plot summary + criticism + commentary is transformative use under US fair use doctrine.

---

## 9. First Upload — Ready Now

| Asset | Path | Status |
|-------|------|--------|
| Channel avatar | `output/frankenstein_classics_en/logos/avatar_1024.png` | ✅ |
| Channel banner | `output/frankenstein_classics_en/logos/banner_2560.png` | ✅ |
| Watermark | `output/frankenstein_classics_en/logos/watermark_400.png` | ✅ |
| Episode 1 video | `output/frankenstein_classics_en/ep01_waltons_letters/ep01_final.mp4` | ✅ 10:05 final mix |
| Episode 1 narrator script | `output/frankenstein_classics_en/ep01_waltons_letters/script.json` | ✅ |
| Caption (.vtt) | not yet generated | ⏰ Run `/fk-gen-caption` before upload |
| YouTube SEO metadata | not yet generated | ⏰ Run `/fk-youtube-seo` |
| Brand-watermarked final | not yet generated | ⏰ Optional `ffmpeg overlay watermark` |

---

## 10. Open Questions

- Final handle availability — verify `@lamplitlibrary` is free on YouTube + Apple Podcasts + Spotify
- Domain (optional): `lamplitlibrary.com` for site / show notes
- Email contact (e.g., `hello@lamplitlibrary.com`) for sponsorship later
- Patreon / Ko-fi link in description (defer until ~1k subs)
- Should we cross-post audio-only version to Spotify Podcasts? (likely yes — same script, no video processing)
