# Phase 01 — TikTok Developer App + OAuth Setup

**Status:** ⏳ Pending (BLOCKS all downstream phases)
**Priority:** P0 (blocking)
**Owner:** Sang (user action) + Claude (documentation)

## Context

- Research: `plans/reports/researcher-260525-0946-tiktok-content-posting-api.md` §1, §2
- Reference: how `youtube/channels/sach-thi-tham/client_secrets.json` was set up

## Objective

Register TikTok app, obtain `client_key` + `client_secret`, request `video.publish` scope, set up HTTPS redirect URI. End state: ready to plug credentials into `tiktok/channels/sach-thi-tham/client_secrets.json`.

## Steps

### 1.1 Register developer account
- URL: https://developers.tiktok.com
- Sign in with TikTok account that owns/will-own `sach-thi-tham` brand presence (NOT personal account)
- Complete developer profile (real name, email = sang@konek.vn, country VN)

### 1.2 Create new app
- App name: `Flow Kit Podcast Publisher` (or chosen)
- App type: `Web` (CLI counts as web — uses redirect URI)
- Category: `Content Posting / Creator Tools`
- Description: "Automation tool for Vietnamese audiobook podcast channel — auto-uploads pre-rendered episodes to creator's TikTok feed"

### 1.3 Add product: Content Posting API
- In app dashboard → Add products → Content Posting API
- Enable **Direct Post** mode (NOT Inbox/Draft mode)
- Required scopes:
  - `user.info.basic` — get creator open_id
  - `video.publish` — Direct Post (REQUIRES AUDIT for public)
  - `video.upload` — fallback / draft mode (auto-granted)

### 1.4 Configure redirect URI

**Critical:** TikTok requires HTTPS. No `http://localhost` exceptions.

Options (pick one — record decision in this file):

| Option | Setup | Tradeoff |
|--------|-------|----------|
| A. Existing Konek domain | `https://flowkit.konek.vn/oauth/tiktok/callback` — needs Cloudflare/DNS + tiny static page that captures `?code=` | Reuses infra |
| B. Cloudflare Pages free | Deploy single-page redirect handler to e.g. `https://fk-tiktok-oauth.pages.dev/callback` | Free, fast setup |
| C. ngrok/localtunnel for setup-only | `https://<random>.ngrok.io/callback` during initial auth only | Free, ephemeral |

**Decision:** _____ (fill before phase-02)

The callback page just needs to display the `code` query param so user copies it back to CLI. No backend needed.

### 1.5 Save credentials locally

After app created, copy from app dashboard:
- Client Key (alias: `client_id`)
- Client Secret

Create file `tiktok/channels/sach-thi-tham/client_secrets.json`:
```json
{
  "client_key": "awxxxxxxxxxxxxx",
  "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "redirect_uri": "https://<chosen>/callback",
  "scopes": ["user.info.basic", "video.publish", "video.upload"]
}
```

Add `tiktok/channels/*/client_secrets.json` + `tiktok/channels/*/token.json` to `.gitignore`.

### 1.6 (Parallel) Start audit prep checklist

Audit takes 2-4 weeks → kick off in phase-05 now. Required artifacts:
- Privacy policy URL (publicly accessible)
- Terms of Service URL
- Demo video (screen recording of upload flow)
- Use case description

## Files to create

- `tiktok/channels/sach-thi-tham/client_secrets.json` (gitignored)
- `tiktok/channels/sach-thi-tham/.gitkeep`
- Update `.gitignore`: add `tiktok/channels/*/client_secrets.json`, `tiktok/channels/*/token.json`

## Todo

- [ ] 1.1 Register at developers.tiktok.com
- [ ] 1.2 Create app `Flow Kit Podcast Publisher`
- [ ] 1.3 Add Content Posting API, enable Direct Post, request `video.publish` scope
- [ ] 1.4 Pick redirect URI option (A/B/C) and deploy callback page
- [ ] 1.5 Save `client_secrets.json` + update `.gitignore`
- [ ] 1.6 Note audit prep — handled in phase-05

## Success criteria

- App visible in TikTok dev dashboard with Content Posting API product enabled
- Redirect URI reachable over HTTPS, returns the `code` value
- `client_secrets.json` exists, gitignored, contains valid keys
- Scopes show `video.publish` in pending/approved state

## Risks

| Risk | Mitigation |
|------|------------|
| App rejection at registration (account not eligible) | Use established account; provide clear use case |
| Redirect URI cannot be HTTPS (no domain available) | Use Cloudflare Pages (option B) — 5 min setup |
| `video.publish` scope auto-rejected | Submit audit materials immediately (phase-05) |

## Next

→ phase-02 once `client_secrets.json` populated
