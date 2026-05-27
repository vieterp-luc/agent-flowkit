# fk-video-bible-explainer — Lamplit Word Channel Operator + Episode Producer

Long-form English Bible Explainer videos (**~25 minutes**) for the **Lamplit Word** YouTube channel. Combines three creative skills — `script-bible-explainer`, `image-bible-explainer`, `thumbnail-bible-explainer` — into the full FlowKit render pipeline: watercolor image montage + Ken Burns motion + English narrator + reverent instrumental BGM.

This skill is both the **per-episode producer** and the **channel operator** (status dashboard + next-action recommender + batch + topic backlog), modeled on `fk-video-lamplit-library`.

**One topic = one video.** Unlike Lamplit Library (one book → many chapter-episodes), each Bible Explainer topic is a **standalone 25-minute video** — never split into chapters, parts, or a multi-episode series. The script's 6 internal parts (Opening / Act 1 / CTA / Act 2 / Climax / Outro) all concat into a single MP4. The channel is a flat library of independent one-off videos; each roadmap entry is one topic and produces exactly one `_final.mp4`.

Usage:
```
/fk-video-bible-explainer                                  # status dashboard (DEFAULT)
/fk-video-bible-explainer --detail                         # per-episode breakdown table
/fk-video-bible-explainer --next                           # ONLY the next 3 actions
/fk-video-bible-explainer --topics                         # generate 5 viral topic ideas → backlog
/fk-video-bible-explainer "Every Word Jesus Spoke From the Cross"   # produce ONE episode
/fk-video-bible-explainer --ep 2                           # produce ep already in roadmap
/fk-video-bible-explainer --ep 1 --script <path>           # produce using an existing script file
/fk-video-bible-explainer --batch 2-5                      # produce a roadmap range
/fk-video-bible-explainer --no-music                       # skip BGM for this run
```

---

## What This Skill Combines

| Creative skill | Role in the pipeline | Output it returns |
|----------------|----------------------|-------------------|
| `script-bible-explainer` | Episode script (6-phase workflow) | ~3,700-word voiceover-ready clean prose, zero brackets |
| `image-bible-explainer` | Scene image prompts | N watercolor Imagen prompts distributed across the script's 6 parts |
| `thumbnail-bible-explainer` | Thumbnail prompts | 3 watercolor thumbnail variations (text + no-text versions) |

These three are **Skill-tool skills** in `.claude/skills/`. This skill invokes them, then renders their text/prompts into a finished MP4 via FlowKit.

---

## Channel: Lamplit Word

| Item | Value |
|------|-------|
| Display name | Lamplit Word |
| Handle | `@lamplitword` |
| Slug | `lamplit-word` |
| Channel dir | `youtube/channels/lamplit-word/` |
| Local output | `output/lamplit_word/` |
| Content focus | Long-form Bible "Every X Explained" videos (~25 min) |
| Audience | English-speaking Christian (US / UK / AU / CA) |
| Narrator voice | `Andrew_TTS` @ speed 0.88 (warm, reverent, contemplative male) |
| Image style | Watercolor Bible storybook — white/cream ground, ink outlines, burnt orange + navy + cream |
| Render | Ken Burns image montage (16:9, 1920×1080, 30fps) — no Flow video-gen, quota-safe |
| BGM | Reverent instrumental ONLY, 0.06× volume (optional) |
| Text overlay | NONE on the body video (per `feedback-no-text-overlay-podcast`) |
| Cadence | 2 episodes / week (long-form is production-heavy) |

---

## Pre-flight

```bash
curl -s http://127.0.0.1:8100/health   # must return {"extension_connected": true}
```
If it fails → run `/fk-doctor` before anything else.

Read channel state on every invocation:

| File | Purpose |
|------|---------|
| `youtube/channels/lamplit-word/roadmap.json` | One entry per topic/video + topic backlog + status |
| `youtube/channels/lamplit-word/channel_rules.json` | Schedule, SEO, branding, voice defaults |
| `youtube/channels/lamplit-word/upload_history.json` | Uploaded episodes (video_id, publish_at) |
| `youtube/channels/lamplit-word/playlists.json` | Playlist IDs |
| `output/lamplit_word/ep*/` | What is built locally |

If any channel file is missing → create it from the templates in "Quick Reference" and warn the user.

---

## MODE A — Status Dashboard (DEFAULT, no args)

### Step 1 — Load roadmap + history

Read `roadmap.json` + `upload_history.json`.

### Step 2 — Compute per-episode state

For each entry in `roadmap.episodes`:
- `script_ready` = `output/lamplit_word/<slug>/script.txt` exists
- `built` = `output/lamplit_word/<slug>/<slug>_final.mp4` exists
- `branded` = `..._final_branded.mp4` exists
- `uploaded` = slug present in `upload_history.json`
- `scheduled` = uploaded with `publish_at` in the future
- `next_ep_to_produce` = lowest `ep` with `status` ∈ {planned, scripted} and not built
- `next_ep_to_upload` = lowest `ep` built locally but not in `upload_history`

### Step 3 — Output 1-screen summary

```
📖  LAMPLIT WORD  —  Status @ <today ICT>

🎬 Episodes: <uploaded>/<total in roadmap> uploaded
   ├─ Published:   <count>   (latest: ep<N> — <title>)
   ├─ Scheduled:   <count>   (next: ep<N+1> on <date>)
   ├─ Local-ready: <count>   (built, not uploaded)
   └─ Scripted:    <count>   (script done, not rendered)

📺 Channel: @lamplitword | Cadence: 2/week | Voice: Andrew_TTS

📋 Topic backlog: <count> ý tưởng đang chờ
   1. <topic — English, dùng cho production>
      🇻🇳 <vi — tên tiếng Việt>
      <desc — 1-2 dòng mô tả tiếng Việt, giúp user hiểu chủ đề>
   2. <topic 2>
      🇻🇳 <vi 2>
      <desc 2>
   ... (max 5 hiển thị)

🎯 NEXT ACTIONS:
   1. <#1 with concrete command>
   2. <#2>
   3. <#3>
```

**Backlog display rule:** every `topic_backlog` entry is rendered bilingually — the English `topic` line (this is the exact string passed to `script-bible-explainer`), then a 🇻🇳 Vietnamese title, then a 1-2 line Vietnamese description so the user understands the topic at a glance. The episode rows above also show the `vi` title in parentheses when present.

### Step 4 — Pick the 3 next actions (decision tree, stop at 3)

1. **Topic backlog empty?** → "Generate topics — `/fk-video-bible-explainer --topics`"
2. **An episode is `scripted` but not built?** → "Render ep<N> — `/fk-video-bible-explainer --ep <N>`"
3. **Scheduled backlog < 3 episodes?** → "Produce next episode — `/fk-video-bible-explainer \"<next backlog topic>\"`"
4. **Built locally but not uploaded?** → "Upload ep<N> — `/fk-youtube-upload <video_id>`"
5. **Thumbnail missing on an uploaded ep?** → "Gen + attach thumbnail for ep<N>"
6. **Channel not verified?** → "Verify channel at youtube.com/verify (one-time, needed for custom thumbnails)"

`--next` = print only the 3 actions. `--detail` = add a per-episode table (ep | status | slug | video_id | scheduled | thumb).

---

## MODE B — Produce One Episode

Triggered by a positional topic string OR `--ep N`. Runs end-to-end, autonomously. The only creative pause is inside `script-bible-explainer`'s own phases (it manages those).

### Step 0 — Episode script

- If `--script <path>` given → use that file as the script. Skip to Step 1.
- Else invoke the **`script-bible-explainer`** skill with: `TOPIC = <positional topic>`, `LENGTH = 25`, `TONE = reverent-conversational` (default for the channel; pass `dramatic` only if the topic is a Passion/judgment theme).
- Take its **Phase 6 final clean prose** (not the phase scaffolding).
- Resolve the episode slug: `ep<NN>_<kebab-topic>` (e.g. `ep02_every_word_from_the_cross`).
- Save to `output/lamplit_word/<slug>/script.txt`.
- **Verify before continuing:** `grep -c '\[' script.txt` returns 0 (no brackets); word count 3,400–4,000.

### Step 1 — Scene image prompts

Invoke the **`image-bible-explainer`** skill with this config (do not ask the user — these are channel defaults):
- Total images: **40** (Bible-contemplative density for ~25 min ≈ 1 image / 37.5s — Ken Burns motion already adds visual variety, reverent pacing favors longer dwell time)
- Distribution: **AUTO** (its 12/25/5/24/26/8 formula across the 6 script parts → 5 / 10 / 2 / 10 / 10 / 3)
- Priority scene type: **balanced**
- Text labels: **NO** (body video carries no text)

Pass the `script.txt` as the source. Save the returned prompts to `output/lamplit_word/<slug>/image_prompts.json` as an array of `{idx, part, prompt}` — `part` ∈ 1..6 so the renderer can time each image to its part.

**Defensive prompt hygiene** (per `feedback-flow-image-orientation-text`): every prompt must force `16:9 HORIZONTAL landscape frame` and `STRICTLY NO TEXT, no letters, no captions, no watermark`. Append these if `image-bible-explainer` did not.

### Step 2 — Create the Flow project

`POST /api/projects`:
- `name`: `Lamplit Word — <episode title>`
- `story`: 2–3 sentences on the topic + watercolor Bible-storybook aesthetic
- `material`: `watercolor` (or set via `/fk-add-material` to a watercolor-storybook profile)
- `language`: `en`
- `orientation`: `HORIZONTAL`

Save `flow_project_id` into the roadmap entry.

### Step 3 — Render scene images (6 waves — one per script part)

**Never mass-batch all 40** (per `feedback-flow-image-gen-per-chapter`: bulk gen triggers reCAPTCHA + burns quota regardless of total count).

For each script part 1→6:
1. **Probe**: gen the first image of the part alone. If it fails with QUOTA / CAPTCHA / no-operations → **HALT**, run `/fk-doctor`, surface to user.
2. If the probe is clean → `POST /api/requests/batch` with `GENERATE_IMAGE` for the rest of that part's images.
3. Poll `/api/requests/batch-status` (15s) until done. Download to `output/lamplit_word/<slug>/images/scene_<idx>.png`.

Pre-flight Flow credits before Part 1 (per `feedback-flow-quota-safety`).

### Step 4 — TTS narration (6-part chunked)

The script is one continuous 3,700-word prose. Split it at the natural part boundaries (`script-bible-explainer` parts: Opening / Act 1 / CTA / Act 2 / Climax / Outro) into 6 chunks.

**Load full `ref_text`** before any call (per `feedback-tts-full-ref-text` — truncated ref_text silently makes TTS ~2× slower, 10-17s vs 5-7s):
```bash
REF_TEXT=$(python3 -c "import json; print(json.load(open('output/_shared/tts_templates/templates.json'))['Andrew_TTS']['text'])")
```
Never inline a shortened sample; always pass the full transcript from `templates.json.Andrew_TTS.text`.

For each chunk → `POST /api/tts/generate`:
```json
{
  "text": "<chunk prose>",
  "ref_audio": "output/_shared/tts_templates/Andrew_TTS.wav",
  "ref_text": "<full REF_TEXT loaded above — NOT truncated>",
  "speed": 0.88,
  "language": "en",
  "output_path": "output/lamplit_word/<slug>/tts/part_<K>.wav"
}
```
Concat the 6 parts → `tts/narrator_full.wav`. Record each part's duration `D_k` — used for Ken Burns timing.

**Verify:** total duration 23–27 min; mean_volume −25…−10 dB; no chunk cut mid-sentence; per-chunk render time ≤ 1.5× chunk audio length (if higher → ref_text was truncated, re-run).

### Step 5 — Ken Burns motion

Each image belongs to a part `K`. For part `K` with duration `D_k` and `n_k` images:

**Clip length must compensate for the 1s xfade overlap in Step 7a**, otherwise the concatenated video ends up ~`(N_total − 1) × 1s` shorter than the narrator and the last image stretches under silence. Formula:

```
clip_seconds = (D_k / n_k) + xfade_seconds        # xfade_seconds = 1.0
```

The first clip of the whole montage uses `D_k / n_k` only (no leading xfade); every subsequent clip absorbs one 1s overlap. Equivalently: total video = Σ(clip_i) − (N_total − 1) × 1s ≈ narrator duration. Round each `clip_seconds` to 2 decimals.

`POST /api/ken-burns/clip` per image:
```json
{
  "image_path": "output/lamplit_word/<slug>/images/scene_<idx>.png",
  "duration_seconds": <D_k / n_k>,
  "motion": "<rotated>",
  "resolution": "1920x1080",
  "output_path": "output/lamplit_word/<slug>/ken-burns/scene_<idx>_<motion>.mp4"
}
```
Motion rotation: `pan_left → zoom_in → pan_right → zoom_out → static …`, never two consecutive the same. For close-up / single-figure images use `static` or `pan` only — avoid `zoom_in` (it crops faces). Hook (Part 1) leans `zoom_in`; Outro (Part 6) leans `zoom_out`.

### Step 6 — Reverent instrumental BGM

Skip entirely if `--no-music`.

Generate **4 instrumental tracks** (`POST /api/gemini/browser/generate-music`), each ~7–8 min — a 4-track minimum guarantees ≥ 28 min raw, leaving headroom over a 25-min target after the 2s crossfades (~6s lost total). If any track returns < 6 min, re-gen that single track. All prompts start with `instrumental only, no vocals, no lyrics, no singing`:
- Track 1 — opening: `soft piano + warm strings, sacred, reverent, contemplative, cinematic Bible-documentary opener, fade-friendly`
- Track 2/3 — body: `calm ambient piano + low strings, prayerful, very low energy, no melody peaks, suitable under spoken narration`
- Track 4 — close: `gentle uplifting strings + piano, hopeful resolution, restrained, reverent closer`

**Coverage check (mandatory before concat):** `sum(track_i) − 3 × xfade_2s ≥ narrator_duration + 5s`. If not satisfied → generate one extra body-style track and re-check; never proceed with a music bed shorter than the narrator.

Crossfade-concat (xfade 2s) in order [1, 2, 3, 4], trim to narrator duration. **Always save MP3** (transcode Gemini Lyria MP4 → `-vn -c:a libmp3lame -b:a 192k`, per `feedback-music-as-mp3`).

### Step 7 — Concat + mix

7a. Concat all Ken Burns clips in `idx` order, xfade 1s, `-an` →`concat_scenes.mp4`.

7b. Mix narrator + BGM:
```
[1:a]volume=1.6[narrator];
[2:a]volume=0.06[bgm];
[bgm][narrator]amix=inputs=2:duration=first:dropout_transition=0[aout]
```
`-c:v libx264 -crf 18 -r 30 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart` → `<slug>_final.mp4`.

**Verify:** duration 23–27 min; 1920×1080 30fps; mean_volume −20…−10 dB; no vocals in BGM; **no burned text overlay**.

### Step 8 — Thumbnail

Invoke the **`thumbnail-bible-explainer`** skill with `Title = <episode title>` + the `script.txt`. It returns 3 variations. Default: render **Variation 1** via Flow `GENERATE_IMAGE` (16:9). Save text + no-text versions to `output/lamplit_word/<slug>/thumbnail/`.

### Step 9 — Branding + SEO + caption

- `/fk-brand-logo <video_id>` — Lamplit Word watermark (see channel_rules `branding`) → `<slug>_final_branded.mp4`
- `/fk-youtube-seo <video_id> --language en` — title/description/tags/chapter timestamps → `youtube_seo.json`
- `/fk-gen-caption <video_id> --language en` — `.vtt` captions

### Step 10 — Register + upload

Update the roadmap entry: `status: "built"`, `flow_project_id`, `local_dir`. Then:
- `/fk-youtube-upload <branded mp4>` when the user is ready (default privacy `private` → auto-publish via `publish_at`).
- On upload, append to `upload_history.json` and set `status: "uploaded"`.

---

## MODE C — `--batch A-B`

1. Validate A..B are roadmap episodes with `status` ∈ {planned, scripted}, none already built.
2. Pre-flight Flow credits once. If low → refuse, tell the user to wait for quota reset.
3. Produce each episode **fully and sequentially** (Mode B, ep A → ep B). Do **not** parallelize image gen across episodes — sequential per-episode is what keeps Flow quota / reCAPTCHA safe.
4. After each episode, update the roadmap before starting the next, so an interruption is resumable.
5. Report a summary table at the end.

---

## MODE D — `--topics`

Generate **5** viral-potential "Every X Explained" topics (compatible with `script-bible-explainer`'s formula): `Every Time God Said X`, `Every Wife/Father/Disciple/Miracle/Prophecy`, etc. Show them bilingually (English + 🇻🇳 + mô tả), let the user pick which to keep. New episodes draw from this backlog in order.

Each appended `topic_backlog` entry is an **object**, not a bare string:
```json
{
  "topic": "<English topic — exact string passed to script-bible-explainer>",
  "vi": "<Vietnamese title>",
  "desc": "<1-2 line Vietnamese description of what the episode covers>"
}
```
The skill writes all three fields. Only `topic` is used downstream for production; `vi` and `desc` exist purely so the user understands the backlog.

---

## Output Folder Structure

```
output/lamplit_word/
└── ep01_every_fear_not/
    ├── script.txt                 script-bible-explainer Phase 6 prose
    ├── image_prompts.json         [{idx, part, prompt}]
    ├── images/                    scene_0.png … scene_39.png
    ├── ken-burns/                 scene_0_zoom_in.mp4 …
    ├── tts/                       part_1.wav … part_6.wav + narrator_full.wav
    ├── music/                     01_open.mp3 … 04_close.mp3
    ├── thumbnail/                 var1_text.png, var1_notext.png
    ├── concat_scenes.mp4          video-only montage
    ├── ep01_every_fear_not_final.mp4
    ├── ep01_every_fear_not_final_branded.mp4
    ├── captions.vtt
    └── youtube_seo.json
```

---

## Quick Reference — Channel Standard

| Param | Value |
|-------|-------|
| Resolution / FPS | 1920×1080 (16:9) / 30 |
| Video codec | h264, yuv420p, crf 18 |
| Audio codec | aac, 192k, 48kHz, stereo |
| Script length | ~3,700 words / ~25 min (`script-bible-explainer`) |
| Scenes / images | ~40 (AUTO distribution: 5 / 10 / 2 / 10 / 10 / 3 across 6 parts, ≈ 1 image / 37.5s) |
| Narrator voice / speed | `Andrew_TTS` / 0.88 |
| Narrator volume | 1.6× |
| BGM | instrumental ONLY, reverent, 0.06× (optional) |
| xfade video / music | 1s / 2s |
| Image style | watercolor Bible storybook, no text, 16:9 |
| Text overlay | NONE on body video |
| Target duration | 23:00 – 27:00 |
| Default privacy | `private` (auto-scheduled via `publish_at`) |
| YouTube title pattern | `{title} — Bible Explained \| Lamplit Word` (≤ 80 chars) |
| YouTube category | 27 (Education) |

---

## Per-Episode Checklist

```
[ ] Pre-flight: /health ok, Flow credits ok
[ ] Step 0 Script — script-bible-explainer, 25min, 0 brackets, 3.4k–4k words → script.txt
[ ] Step 1 Image prompts — image-bible-explainer, 40 / AUTO / no-text → image_prompts.json
[ ] Step 2 Flow project — HORIZONTAL, watercolor material
[ ] Step 3 Images — 6 waves (per part), probe-first each wave, no mass-batch
[ ] Step 4 TTS — Andrew_TTS 0.88, full ref_text from templates.json, 6 chunks → narrator_full.wav, 23–27 min
[ ] Step 5 Ken Burns — clip = D_k / n_k + 1s xfade compensation, motion rotated, static for close-ups
[ ] Step 6 BGM — instrumental only, 4 tracks, coverage ≥ narrator + 5s, MP3, xfade-2s concat (skip if --no-music)
[ ] Step 7 Concat + mix — narrator 1.6×, BGM 0.06×, no text overlay
[ ] Verify final — 23–27 min, 1080p30, mean_volume −20…−10 dB
[ ] Step 8 Thumbnail — thumbnail-bible-explainer var1 rendered
[ ] Step 9 Branding + SEO + caption
[ ] Step 10 Roadmap updated → upload when ready
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Brackets in script | `script-bible-explainer` Phase 6 skipped | Re-run its Phase 6 clean pass before rendering |
| reCAPTCHA during image gen | Mass-batched all 60 | Gen per-part waves (6), probe-first — never one batch |
| QUOTA / no-operations error | Flow credits exhausted | HALT, `/fk-doctor`, resume after reset |
| Text baked into watercolor image | Prompt missing the NO-TEXT guard | Add `STRICTLY NO TEXT` + negative list, regen |
| Image is vertical | Orientation not forced | Add `16:9 HORIZONTAL landscape frame` to prompt |
| TTS cuts mid-sentence | Chunk split mid-sentence | Split only at part boundaries / sentence ends |
| TTS render ~2× slower than expected | `ref_text` truncated or missing | Load full `templates.json.Andrew_TTS.text`, pass as `ref_text` (see Step 4) |
| Final video shorter than narrator (last image lingers under silence) | Step 5 ignored xfade overlap | Use `clip = D_k / n_k + 1` (xfade comp); see Step 5 formula |
| Music bed runs out before narrator ends | Only 3 tracks generated or one < 6 min | Generate 4 tracks min; run coverage check before concat (Step 6) |
| Final > 27 min | Script over length | Trim Act 2 in `script-bible-explainer`, regen TTS |
| BGM has vocals | Music prompt vague | Prefix every prompt with `instrumental only, no vocals, no lyrics` |
| Narration muddy under music | BGM too loud | Drop BGM volume to 0.04× |

---

## When to Call `/fk-doctor`

```
[ ] /health → extension_connected: false
[ ] /api/projects or /api/requests/batch HTTP 4xx/5xx
[ ] Image batch returns QUOTA / CAPTCHA / NO_FLOW_KEY / UNSAFE_GENERATION
[ ] /api/tts/generate rate limit or stall
[ ] /api/ken-burns/clip stall
[ ] Gemini Lyria music quota exceeded
[ ] /fk-youtube-upload HttpError
```

---

## Files Created / Edited

- READ: `youtube/channels/lamplit-word/*.json`, `output/lamplit_word/ep*/`
- WRITE (autonomous): episode artifacts under `output/lamplit_word/<slug>/`; roadmap status updates
- WRITE (on explicit upload): `upload_history.json`
- INVOKES: skills `script-bible-explainer`, `image-bible-explainer`, `thumbnail-bible-explainer`; commands `/fk-create-project`, `/fk-add-material`, `/fk-brand-logo`, `/fk-youtube-seo`, `/fk-gen-caption`, `/fk-youtube-upload`, `/fk-doctor`

## Output Length Discipline

Default invocation = **1 screen**: dashboard + 3 numbered actions. No build logs, no raw API dumps, no roadmap reprint. Use `--detail` for the per-episode table.
