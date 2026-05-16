# fk-video-lamplit-library — Lamplit Library Channel Operator

Status dashboard + next-action recommender for the **Lamplit Library** YouTube channel (classic literature podcast).

Default invocation = 1-screen summary: which book is active, how many episodes published / scheduled / pending, what to do next.

Usage:
```
/fk-video-lamplit-library                      # status dashboard (default)
/fk-video-lamplit-library --detail             # per-episode breakdown table
/fk-video-lamplit-library --batch 8-14         # produce + upload ep range (active book)
/fk-video-lamplit-library --book <slug>        # show status for another book
/fk-video-lamplit-library --next               # ONLY show next 3 actions

# Bootstrap a NEW book (smart positional):
/fk-video-lamplit-library "Wuthering Heights"            # auto-detect: if in roadmap → status; else → bootstrap flow
/fk-video-lamplit-library "Dracula" --author "Bram Stoker"  # explicit author hint
/fk-video-lamplit-library "Jane Eyre" --bootstrap        # force bootstrap even if slug-collides
```

---

## Data Sources (read on every invocation)

| File | Purpose |
|------|---------|
| `youtube/channels/lamplit-library/series_roadmap.json` | All books + chapter maps + entity waves |
| `youtube/channels/lamplit-library/channel_rules.json` | Schedule, SEO, branding defaults |
| `youtube/channels/lamplit-library/upload_history.json` | What's been uploaded (video_id, title, publish_at) |
| `youtube/channels/lamplit-library/playlists.json` | Playlist IDs per book |
| `output/<book_local_dir>/ep*/` | What's been built locally (ep dirs + final mp4) |
| YouTube API `videos.list(mine=true)` | Live status (private / scheduled / public) — optional, only if `--detail` |

---

## Default Workflow (status dashboard)

### Step 1: Load roadmap + channel state
```bash
ROADMAP=/Users/vieterp/code/Research/agent-flowkit/youtube/channels/lamplit-library/series_roadmap.json
HISTORY=/Users/vieterp/code/Research/agent-flowkit/youtube/channels/lamplit-library/upload_history.json
```
Read both. If `--book <slug>` was passed, override `active_book` for this invocation only (don't write back unless user explicitly says "switch active book").

### Step 2: Compute state per active book

For the active book:
- `total_ep` = `roadmap.books[active].total_episodes`
- `chapter_map` = `roadmap.books[active].chapter_map`
- `local_built` = count of `output/<local_dir>/ep*_*/<*_final_branded.mp4>` files that exist
- `uploaded` = count of entries in `upload_history.json` whose title contains the book name
- `scheduled` = uploaded count where publish_at is in the future
- `published` = uploaded count where publish_at is in the past (or absent)
- `next_ep_to_produce` = smallest `ep` number in `chapter_map` whose slug has NO local final mp4
- `next_ep_to_upload` = smallest `ep` already built locally but NOT in upload_history

### Step 3: Compute entity wave needs

From `entity_waves`:
- For each wave with `status: "pending"`, if `needed_by_ep <= next_ep_to_produce`, flag as **blocking** for next batch.
- If next_ep_to_produce already needs Wave 3 entities and Wave 3 status is pending → top action = "Gen Wave 3 first".

### Step 4: Output 1-screen summary (DEFAULT)

Template:
```
🕯️  LAMPLIT LIBRARY  —  Status @ <today's date ICT>

📚 Active: <Book> (<Author>) — <uploaded>/<total> episodes uploaded
   ├─ Published:  <count>  (latest: ep<N> on <date>)
   ├─ Scheduled:  <count>  (next: ep<N+1> on <date> at 08:00 ICT)
   ├─ Local-ready: <count>  (built but not uploaded)
   └─ Entity waves: <list of wave statuses>

📺 Channel: @lamplitlibrary  |  Schedule: daily 08:00 ICT (publish_at 01:00 UTC)
   Verified: ✅  |  Custom thumbnails: ✅  |  Playlists: <count>

📅 Next 7 days schedule:
   <Day Date>  →  ep<N>  (<chapter name>)
   <Day Date>  →  ep<N+1> (<chapter name>)
   ...

🎯 NEXT ACTIONS:
   1. <#1 action with concrete command>
   2. <#2 action>
   3. <#3 action>

📖 Books in roadmap:
   ✅ <book> (in_progress, <done>/<total>)
   ⏳ <book> (planned, <launch_target>)
   ...
```

### Step 5: Pick the 3 next actions (decision tree)

Pick in priority order. Stop at 3:

1. **Wave entities blocking?** → "Gen Wave <N> first (needed by ep<X>)" with the prompt to run.
2. **Backlog < 3 days of scheduled content?** → "Produce next batch ep<A>-<B> — invoke `/fk-video-lamplit-library --batch <A>-<B>`"
3. **Built locally but not uploaded?** → "Upload ep<N> to YouTube — invoke `upload_video()` from `youtube/upload.py`"
4. **Thumbnail missing on any uploaded ep?** → "Gen + upload thumbnail for ep<N>"
5. **Active book < 80% done?** → suggest continuing
6. **Active book 100% done?** → "Switch to next planned book — invoke `--book <next_book_slug>` and bootstrap project + Wave 1 entities"
7. **Channel verification still pending?** → "Verify channel at youtube.com/verify"
8. **ep01 published today/yesterday but no analytics check?** → "Check YouTube Studio analytics for first-day baseline"

---

## --detail Workflow (full per-ep table)

Output per-episode table:

```
ep  | status      | scheduled            | video_id      | playlist_pos | thumb
----|-------------|----------------------|---------------|--------------|------
01  | scheduled   | 2026-05-15 08:00 ICT | Deg46rjRXoc   | 0            | ✅
02  | scheduled   | 2026-05-16 08:00 ICT | Vq72r9xOTgI   | 1            | ✅
...
08  | not built   | -                    | -             | -            | -
```

Optional: hit YouTube API `videos.list(id=...)` to get LIVE status (privacyStatus field) per uploaded video. Skip if user just wants quick check.

---

## --batch Workflow (produce + upload range)

If `--batch A-B` flag present:

1. Validate range: A and B both in chapter_map, A < B, both currently NOT built locally.
2. Check entity wave needs (run Step 3 above). If wave entities needed, REFUSE batch and instruct user to gen waves first.
3. Copy `output/<local_dir>/batch-produce-ep2-7.py` as template → make `batch-produce-ep<A>-<B>.py`:
   - Update `EPS` list with chapter map entries for range A-B
   - Update `SCENE_ENTITIES` mapping per ep (TODO: auto-generate from script)
   - Update publish_at base date = day after most recently scheduled ep
4. Run in background via `nohup ./venv/bin/python -u <script> > /tmp/batch-ep<A>-<B>.log 2>&1 &`
5. Report PID + log path, monitor via `tail`.
6. When done, `--status` should show new episodes added.

---

## Bootstrap New Book Workflow (positional book name OR `--bootstrap`)

Mirrors what was done for Frankenstein. Runs end-to-end, pausing only at major creative decisions.

### Step 0 — Copyright validation (HARD GATE)
1. Check author + edition. Reject if author died < 70 years ago (e.g., Hemingway 1961 → US PD 2032+).
2. Verify full English text is on Project Gutenberg (`https://www.gutenberg.org/ebooks/search/?query=<title>`). If not — STOP and surface to user.
3. For translated works (e.g., Dostoevsky, Tolstoy): use ONLY US-PD translations (Constance Garnett for Russian classics is safe; modern Pevear/Volokhonsky translations are NOT).
4. Output: ✅ PD-clear OR ❌ with reason.

### Step 1 — Resolve metadata + aesthetic profile
Ask user (or auto-decide) for:
- **Book title + author + edition year** — confirm
- **Total episodes target** (usually = chapter count; long books may merge)
- **Aesthetic profile** — pick from preset OR custom:
  | Book class | Aesthetic preset |
  |------------|------------------|
  | Gothic horror (Frankenstein, Dracula) | `gothic_dark` — oil painting, candlelit, Fuseli + Goya |
  | Brontë moors (Wuthering Heights, Jane Eyre) | `gothic_moors` — windswept Yorkshire, brooding sky |
  | Regency (Austen) | `painterly_regency` — Vigée Le Brun pastel, drawing rooms |
  | Russian realism (Dostoevsky, Tolstoy) | `russian_realist` — 19th c St. Petersburg, dim, oppressive |
  | Victorian noir (Sherlock Holmes) | `victorian_noir` — foggy London, gas lamps |
  | 1920s Jazz Age (Gatsby) | `cinematic_1920s` — art deco, gold/black |
  | Watercolor dreamy (Little Prince) | `watercolor_dreamy` — pastel surrealism |

### Step 2 — Create Flow project
Call `POST /api/projects` with:
- `name`: `<Book> Classics Podcast`
- `description`: one-line summary
- `story`: 2-3 sentence book + setting + aesthetic
- `material`: `oil_painting` (or matching preset)
- `language`: `en`
- `orientation`: `HORIZONTAL`
- `characters`: Wave 1 roster (see Step 3)

### Step 3 — Define Wave 1 entity roster
Researcher first identifies main characters + critical locations from the source text or known summary. Typical Wave 1 = 6-10 entities:
- 3-5 main characters (English aliases like "The Scientist", "The Lover", "The Captain" — avoid real names per Imagen content policy)
- 3-5 key recurring locations
- Each with detailed visual description matching the chosen aesthetic profile

Pause for user to review/edit roster before commit. Show ASCII table:
```
WAVE 1 ROSTER for <Book>:
  [character] The X    — <one-line look>
  [character] The Y    — <one-line look>
  [location]  Z House  — <one-line look>
  ...
OK to commit? (yes / edit)
```

### Step 4 — Submit Wave 1 batch + poll
After commit, POST `/api/requests/batch` with `GENERATE_CHARACTER_IMAGE` for all Wave 1 entities. Poll `/api/requests/batch-status` until done. Download refs to `output/<book_slug>_classics_en/refs/`.

### Step 5 — Spot-check critical entity
For brand-defining entities (e.g., the Creature for Frankenstein, Heathcliff for Wuthering Heights), Read the ref image and verify match. Flag for regen if drift.

### Step 6 — Extract chapter map
Two options:
- **Auto** — `POST /api/book/extract-chapters` with `mode: "auto"` if user provides PDF/EPUB path. Returns chapter list.
- **Manual** — user provides chapter outline OR skill uses a known chapter map for famous books (preload common books).

Save chapter_map array of `{ep, slug, chapter}` entries to `series_roadmap.json`.

### Step 7 — Create YouTube playlist
Programmatic via `youtube.playlists().insert()`:
- Title: `<Book> — A Chapter Walkthrough`
- Description: book intro + cadence + AI disclosure + subscribe
- Privacy: public

Save playlist_id to `playlists.json` + `series_roadmap.json`.

### Step 8 — Register in roadmap + activate
Update `series_roadmap.json`:
```json
{
  "active_book": "<new_slug>",
  "books": {
    "<new_slug>": {
      "title": "...", "author": "...", "edition": "...",
      "status": "in_progress",
      "flow_project_id": "<new_pid>",
      "playlist_id": "<new_plid>",
      "local_dir": "output/<new_slug>_classics_en",
      "total_episodes": <N>,
      "entity_waves": {
        "wave_1": {"status": "done", "entities": [...]}
      },
      "chapter_map": [...]
    }
  }
}
```

### Step 9 — Suggest first batch
Output:
```
🎉 <Book> bootstrapped.
   Project: <pid>
   Playlist: <plid>
   Wave 1: ✅ <N> entities
   Chapter map: <N> episodes

🎯 NEXT:
   1. Produce launch batch: /fk-video-lamplit-library --batch 1-7
   2. Review thumbnail style for ep1 before batch (optional)
   3. Update channel banner if launching new series prominently
```

### Pause/confirmation points (HARD STOPS)
The bootstrap MUST pause for user input at:
1. Copyright validation result (proceed only if PD-clear)
2. Aesthetic profile selection (if not auto-obvious)
3. Wave 1 entity roster review (creative direction)
4. Critical entity spot-check (e.g., the Creature)

Other steps run autonomously.

---

## --book Workflow (switch active book)

If `--book <slug>` flag present:
1. Verify slug exists in `roadmap.books`.
2. If just `--status --book <slug>` → show stats for that book (don't switch persistently).
3. If `--book <slug> --activate` → write back to `series_roadmap.json` with `active_book: <slug>`.
4. If switching to a "planned" book → suggest bootstrap:
   - Run `/fk-create-project` for the book
   - Update `roadmap.books[slug]` with `flow_project_id`, `playlist_id`, `local_dir`, `status: "in_progress"`
   - Define Wave 1 entities (main characters + key locations)
   - Gen Wave 1
   - Then `--batch 1-7` for first sprint

---

## Quick Reference — Channel Standard

| Item | Value |
|------|-------|
| Channel | Lamplit Library (`@lamplitlibrary`) |
| Channel ID | `UCXtufbOp2KVds3MjNax8_LA` |
| Schedule | Daily 08:00 ICT (01:00 UTC) |
| Voice | `Andrew_TTS` @ speed 0.9 |
| Image style | Oil painting (Caspar David Friedrich + Goya + Fuseli) |
| Brand overlay | `avatar_1024_circle_preview.png`, 130×130, top-left 30px, opacity 0.7 |
| TTS narrator volume | 1.5× |
| BGM music volume | 0.12× |
| Brand watermark | locked in `build-final-video.sh` Step 5 |
| Title pattern | `{book} Explained — Episode {ep}: {chapter} \| Lamplit Library` (max 80 chars) |
| Default category | 27 (Education) |
| Default privacy | private (auto-scheduled via `publish_at`) |
| First upload should be | Verified channel (one-time prereq for custom thumbnail upload) |

---

## Common Outputs

### Healthy state (≥3 days scheduled backlog)
```
🎯 NEXT ACTIONS:
   1. Produce ep<N>-<M> — `/fk-video-lamplit-library --batch <N>-<M>`
   2. Check YouTube Studio analytics for ep<latest published>
   3. Schedule community post / pinned comment for ep<latest>
```

### Wave blocking
```
🎯 NEXT ACTIONS:
   1. ⚠️  Wave 3 entities pending (Justine, Mont Blanc, De Lacey) — required by ep08
      Run: gen Wave 3 via /fk-add-entity then /fk-gen-refs
   2. Produce ep08-14 (after Wave 3 done)
   3. Update series_roadmap.json wave_3.status → "done"
```

### Book complete
```
🎯 NEXT ACTIONS:
   1. 🎉 Frankenstein 24/24 done. Pin "Series Complete" community post.
   2. Bootstrap Wuthering Heights — `/fk-video-lamplit-library --book wuthering_heights --activate`
   3. Plan launch banner update + reorder featured sections
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `series_roadmap.json` missing | Create from template (this skill file's "Quick Reference" defaults), warn user |
| `active_book` slug not in `books` | Error + list valid book slugs |
| Local dir for active book missing | Warn "Run `/fk-create-project` first for this book" |
| `upload_history.json` missing | Show local-only state, warn "no uploads tracked" |
| Schedule conflict (2 eps same publish_at) | Flag in output + suggest reschedule |

---

## Files Created / Edited by This Skill

- READ: roadmap, channel rules, upload history, playlists, local ep dirs
- WRITE (only on explicit user action): `series_roadmap.json` (when `--activate` or wave completion update)
- INVOKES: existing skills `/fk-create-project`, `/fk-add-entity`, `/fk-gen-refs`, `/fk-youtube-upload`, and the local `batch-produce-ep*-*.py` orchestrators

---

## Output Length Discipline

**DEFAULT invocation = 1 screen.** No long explanations. Show the dashboard + 3 numbered actions. User can ask follow-up or run `--detail` for more.

**Don't** include build logs, command history, or raw API responses in the default output.
**Don't** repeat the chapter map (user can see it in `series_roadmap.json`).
**Don't** invoke YouTube API on default — only on `--detail`.
