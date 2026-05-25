# Plan — `/fk-tiktok-upload` Skill (TikTok Content Posting API v2, Direct Post)

**Date:** 2026-05-25
**Owner:** Sang (sang@konek.vn)
**Target channel:** `sach-thi-tham` (Vietnamese book podcast)
**Source videos:** `output/podcast-book/<book>/ep_NN_slug/final_logo.mp4` (fallback `final.mp4`)
**Reference research:** `plans/reports/researcher-260525-0946-tiktok-content-posting-api.md`
**Reference impl:** `youtube/upload.py` + `skills/fk-youtube-upload.md` (mirror pattern)

## Critical Gating Constraint (READ FIRST)

TikTok **unaudited apps** force ALL Direct Post uploads to `SELF_ONLY` regardless of `privacy_level` param. To publish PUBLIC video → must pass TikTok audit (2-4 weeks). Plan code now, audit submission parallel.

→ v1 ship target: working Direct Post in SELF_ONLY mode (creator manually flips privacy in app). v2 = post-audit auto-PUBLIC.

## Architecture (mirrors `youtube/`)

```
tiktok/
├── __init__.py
├── upload.py                       # OAuth + chunked upload + status polling
└── channels/
    └── sach-thi-tham/
        ├── client_secrets.json     # TikTok Client Key + Secret (gitignored)
        ├── token.json              # OAuth token (gitignored, auto-created)
        ├── channel_rules.json      # tiktok_open_id, rules, seo
        └── upload_history.json     # appended per upload

skills/fk-tiktok-upload.md          # skill spec, mirrors fk-youtube-upload.md
.claude/commands/fk-tiktok-upload.md # command stub
```

## Phases

| # | File | Status | Brief |
|---|------|--------|-------|
| 01 | [phase-01-dev-app-and-oauth-setup.md](phase-01-dev-app-and-oauth-setup.md) | ⏳ Pending | Register TikTok dev app, scopes, redirect URI, env-only setup |
| 02 | [phase-02-python-oauth-module.md](phase-02-python-oauth-module.md) | ⏳ Pending | `tiktok/upload.py` — OAuth 2.0 + PKCE, token store/refresh |
| 03 | [phase-03-python-upload-module.md](phase-03-python-upload-module.md) | ⏳ Pending | Init → chunked PUT → status poll, upload_history.json |
| 04 | [phase-04-skill-and-cli.md](phase-04-skill-and-cli.md) | ⏳ Pending | `/fk-tiktok-upload` skill markdown + CLI flags + channel_rules |
| 05 | [phase-05-audit-submission-materials.md](phase-05-audit-submission-materials.md) | ⏳ Pending | Privacy policy, ToS, demo video, audit form submission |

## Key dependencies

- Python 3.10+ (existing)
- `requests` (existing)
- `authlib` OR manual PKCE — pick in phase-02
- HTTPS redirect URI host (likely `https://flowkit.konek.vn/oauth/tiktok/callback` or similar) — needs DNS

## Success criteria (v1)

1. `python -m tiktok.upload --auth sach-thi-tham` opens browser, completes OAuth, saves `token.json`
2. `python -m tiktok.upload --channel sach-thi-tham --video output/podcast-book/dac_nhan_tam/ep_01_.../final_logo.mp4 --title "..."` uploads + posts (as SELF_ONLY in unaudited mode)
3. `upload_history.json` records publish_id + status SUCCESS
4. `/fk-tiktok-upload sach-thi-tham <video_path>` skill command works end-to-end
5. Audit submission package prepared and submitted

## Open dependencies (block phase-01)

- TikTok developer account created? (user action — see phase-01)
- HTTPS redirect URI host decided? (user action — see phase-01)
