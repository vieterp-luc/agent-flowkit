# Phase 04 — `/fk-tiktok-upload` Skill + CLI + Channel Rules

**Status:** ⏳ Pending (depends on phase-03)
**Priority:** P0
**Owner:** Claude (`fullstack-developer` agent)

## Context

- Mirror skill: `skills/fk-youtube-upload.md`
- Mirror command stub: `.claude/commands/fk-youtube-upload.md`
- Mirror rules file: `youtube/channels/<name>/channel_rules.json`

## Objective

Wire the Python module behind a `/fk-tiktok-upload` slash command. Add channel rules (posting cadence, defaults, SEO). Provide batch + single modes.

## Skill spec — `/fk-tiktok-upload`

Signature:
```
/fk-tiktok-upload <channel> <video_path_or_dir> [--privacy SELF_ONLY|PUBLIC|FRIENDS] [--title "..."] [--batch] [--dry-run]
```

Behavior:
- `<channel>` — e.g. `sach-thi-tham`
- `<video_path_or_dir>` — either single file or `ep_NN_slug/` dir (auto-pick `final_logo.mp4` → `final.mp4`)
- `--privacy` — defaults to `SELF_ONLY`. Warn if PUBLIC requested + app not audited.
- `--title` — if omitted, auto-generate from channel `seo` template + ep metadata (see below)
- `--batch` — scan parent dir for `ep_*/final_logo.mp4`, upload all respecting `max_per_day` from rules
- `--dry-run` — show what would happen, no API calls

## `channel_rules.json` schema

```json
{
  "display_name": "Sách Thì Thầm",
  "tiktok_open_id": "<filled after first --auth>",
  "rules": {
    "max_per_day": 3,
    "min_gap_hours": 4,
    "optimal_times_local": ["07:00", "12:00", "20:00"],
    "avoid_hours_local": [0, 1, 2, 3, 4, 5],
    "timezone": "Asia/Saigon"
  },
  "defaults": {
    "privacy_level": "SELF_ONLY",
    "disable_duet": false,
    "disable_stitch": false,
    "disable_comment": false,
    "brand_content": false,
    "cover_timestamp_ms": 0
  },
  "seo": {
    "title_template": "{book} — {ep_title} | #{book_slug} #sach #audiobook #sachhay",
    "title_max_chars": 150,
    "always_include_hashtags": ["#sachthitham", "#sach", "#audiobook", "#sachhay", "#review_sach"],
    "default_caption_suffix": "\n\nFollow @sach.thi.tham để nghe trọn bộ."
  }
}
```

Note on cadence: TikTok unlike YouTube doesn't punish multi-post days as harshly. 3/day matches the YouTube Shorts rule. Adjust based on actual analytics later.

## CLI mapping (`python -m tiktok.upload`)

| CLI flag | Python arg | Notes |
|----------|-----------|-------|
| `--auth <channel>` | (auth-only mode) | Run OAuth flow only |
| `--channel <name>` | `channel_name` | required |
| `--video <path>` | `video_path` | required (file or dir) |
| `--title <text>` | `title` | optional, auto-generated if missing |
| `--privacy <enum>` | `privacy_level` | default from rules.defaults |
| `--disable-duet` | flag | default from rules |
| `--disable-stitch` | flag | default from rules |
| `--disable-comment` | flag | default from rules |
| `--cover-ms <int>` | `cover_timestamp_ms` | default 0 |
| `--dry-run` | flag | print payload, no API |

## Title auto-generation

Source: `output/podcast-book/<book>/ep_NN_slug/` — look for `caption.txt` (existing pattern per memory `feedback-podcast-folder-structure`). If exists, use first line as title. Else format from path:
- book = parent dir name (`dac_nhan_tam` → `Đắc Nhân Tâm` via simple title-case + diacritics dict — start hardcoded for known books)
- ep_title = derive from `ep_NN_slug` (strip `ep_NN_`, kebab → space-case)

Apply `seo.title_template` substitution. Truncate to `title_max_chars`. Append hashtags.

## Skill markdown — outline

File: `skills/fk-tiktok-upload.md`

Sections (mirror `fk-youtube-upload.md` structure):
1. Step 1: Parse input + detect single vs batch
2. Step 2: Load channel rules + apply defaults
3. Step 3: Validate against rules (`max_per_day`, `min_gap_hours`)
4. Step 4: Resolve video (`final_logo.mp4` → `final.mp4` fallback)
5. Step 5: Auto-title / accept --title override
6. Step 6: Pre-upload checks (file constraints from phase-03)
7. Step 7: Dry-run path
8. Step 8: Execute upload via `tiktok.upload.upload_video()`
9. Step 9: Append to history, print share URL/publish_id

Add prominent **GOTCHA** callout near top:
> ⚠️ App is unaudited until phase-05 completes. ALL uploads will be SELF_ONLY (private). Open TikTok app → drafts/profile → toggle privacy manually per post. Do not pass `--privacy PUBLIC` until audit approval — request will be downgraded silently.

## Files to create

- `tiktok/channels/sach-thi-tham/channel_rules.json` — finalized
- `skills/fk-tiktok-upload.md` — full skill spec
- `.claude/commands/fk-tiktok-upload.md` — command stub pointing to skill

## Files to modify

- `tiktok/upload.py` — add CLI flags (`--privacy`, `--disable-*`, `--dry-run`, `--cover-ms`)
- `CLAUDE.md` — add `/fk-tiktok-upload` row to skill table

## Todo

- [ ] Write `channel_rules.json` for sach-thi-tham
- [ ] Update CLI arg parser in `tiktok/upload.py`
- [ ] Implement `_load_rules()` + `_apply_defaults()` helpers
- [ ] Implement `_validate_cadence()` (cmp with `upload_history.json`)
- [ ] Implement `_auto_title()` from caption.txt + path
- [ ] Implement `--dry-run` path (print resolved video + payload, exit)
- [ ] Implement `--batch` (scan dir, schedule respecting rules)
- [ ] Write `skills/fk-tiktok-upload.md`
- [ ] Write `.claude/commands/fk-tiktok-upload.md`
- [ ] Update `CLAUDE.md` skill table
- [ ] Manual test: `--dry-run` → expected payload
- [ ] Manual test: single upload via skill invocation
- [ ] Manual test: batch upload 3 episodes

## Success criteria

- User can run `/fk-tiktok-upload sach-thi-tham output/podcast-book/dac_nhan_tam/ep_01_xxx/` end-to-end
- Auto-title sensible, includes default hashtags
- Cadence rules block 4th upload in same day
- Dry-run accurate, no API call
- Batch correctly spaces uploads (or warns if rule violation)

## Risks

| Risk | Mitigation |
|------|------------|
| Auto-title misses Vietnamese diacritics | Maintain `BOOK_TITLES` dict in module; fallback = path raw |
| Batch hits 6/min init rate limit | Sleep 12s between init calls (5/min safe) |
| User sets `--privacy PUBLIC` before audit | Warn loudly + log expected downgrade |

## Next

→ phase-05 (audit submission) — can run in parallel
