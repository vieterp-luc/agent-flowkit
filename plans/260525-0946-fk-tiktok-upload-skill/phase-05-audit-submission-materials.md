# Phase 05 — Audit Submission Materials (unlock public Direct Post)

**Status:** ⏳ Pending (can run parallel to phase-02..04)
**Priority:** P1 (blocks public launch, not code dev)
**Owner:** Sang + Claude (docs draft)

## Context

- Research: `plans/reports/researcher-260525-0946-tiktok-content-posting-api.md` §1, §5
- Without audit: ALL Direct Posts forced to SELF_ONLY → not viable for production channel growth.

## Audit checklist (TikTok requires)

| Artifact | Status | Where |
|----------|--------|-------|
| Privacy Policy URL (HTTPS) | ⏳ | Need hosted page |
| Terms of Service URL (HTTPS) | ⏳ | Need hosted page |
| Demo video (functionality screencast) | ⏳ | Record after phase-04 done |
| Use case description (text) | ⏳ | Draft below |
| Data handling explanation | ⏳ | Draft below |
| Active app with successful test uploads | ⏳ | Output of phase-03 |

## Draft: Use case description

> Flow Kit is a personal automation tool used by a single creator (sach-thi-tham channel) to upload pre-produced Vietnamese audiobook episodes to TikTok. Videos are 1080×1920 vertical format, 3-10 minutes, with original narration and licensed background imagery. The tool authenticates with one creator account, uploads via Content Posting API, and does not target multiple users or operate as a service for third parties. Upload cadence is 1-3 episodes per day, scheduled manually.

## Draft: Data handling

> The application stores only the TikTok OAuth access + refresh tokens locally on the creator's machine (gitignored JSON file). No user data beyond the authenticated creator's open_id is collected, stored, or transmitted to any third party. The tool does not request `user.info.profile`, `user.info.stats`, or any social graph scopes. No analytics, logging, or telemetry leaves the local machine.

## Privacy policy + ToS (need hosted pages)

Minimal acceptable form — single static HTML each. Options for hosting:

| Option | URL pattern | Effort |
|--------|-------------|--------|
| Cloudflare Pages (recommended) | `https://flowkit-legal.pages.dev/privacy` | 5 min |
| GitHub Pages on existing repo | `https://<user>.github.io/flowkit/privacy` | 10 min |
| Konek subdomain | `https://flowkit.konek.vn/privacy` | needs DNS |

Content templates: stash drafts under `docs/legal/privacy-policy.md` + `docs/legal/terms-of-service.md` for review, then deploy.

## Demo video script (60-90 sec screencast)

1. Show `/fk-tiktok-upload sach-thi-tham output/podcast-book/...` command in terminal
2. Show OAuth flow in browser (first-time only, redacted)
3. Show progress prints (chunk upload + status poll)
4. Switch to TikTok app → show resulting post in profile
5. Voice-over: "This is Flow Kit publishing to the sach-thi-tham creator account. Single creator, manual schedule, content fully owned."

Recording: ScreenStudio or OBS. Output mp4 ≤ 100MB. Upload to YouTube unlisted or attach directly to submission.

## Submission process

1. Open TikTok dev dashboard → app → Direct Post audit submission
2. Fill form with above artifacts
3. Submit, wait 2-4 weeks
4. If rejected: read feedback, iterate
5. Once approved: update `channel_rules.json:defaults.privacy_level` from `SELF_ONLY` → `PUBLIC_TO_EVERYONE`, remove gotcha warning from skill markdown

## Files to create

- `docs/legal/privacy-policy.md` — draft
- `docs/legal/terms-of-service.md` — draft
- `docs/tiktok-audit-submission-260525.md` — log of submission + tracking (replace date in filename when submitting)

## Todo

- [ ] Decide hosting (Cloudflare Pages / GH Pages / Konek)
- [ ] Draft `privacy-policy.md` (use template — single creator, local-only data)
- [ ] Draft `terms-of-service.md`
- [ ] Deploy both to HTTPS
- [ ] Record demo video after phase-04 working end-to-end
- [ ] Fill audit submission form on dev dashboard
- [ ] Track submission ID + date in `tiktok-audit-submission-260525.md`
- [ ] Set calendar reminder +14d to check status
- [ ] Update skill markdown after approval

## Success criteria

- Audit submitted with all artifacts referenced
- Approval received within 2-6 weeks (allow 1 resubmit)
- Test upload with `privacy_level: PUBLIC_TO_EVERYONE` → actually public
- Skill gotcha removed, defaults flipped

## Risks

| Risk | Mitigation |
|------|------------|
| Audit rejected — vague use case | Specific, single-channel framing in description |
| Privacy policy too generic | Lift template, fill in actual data flow specifics |
| Demo shows nothing if audit not done first | Demo SELF_ONLY upload — that's fine, just narrate the limitation |
| Long audit lag | Channel runs YT-only meanwhile; TikTok = additive |

## Next

→ once approved, flip `privacy_level` default + announce in CLAUDE.md
