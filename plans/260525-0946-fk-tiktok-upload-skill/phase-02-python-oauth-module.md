# Phase 02 — Python OAuth 2.0 + PKCE Module

**Status:** ⏳ Pending (depends on phase-01)
**Priority:** P0
**Owner:** Claude (`fullstack-developer` agent)

## Context

- Research: `plans/reports/researcher-260525-0946-tiktok-content-posting-api.md` §2
- Mirror pattern: `youtube/upload.py:42-96` (authorize/load_token/save_token)

## Objective

Implement OAuth 2.0 flow with PKCE in `tiktok/upload.py`. Functions: `authorize(channel_name) -> dict (token info)`, `refresh(token) -> token`, persistent storage `token.json`.

## Endpoints (from research)

| Action | URL |
|--------|-----|
| Authorize | `https://www.tiktok.com/v2/auth/authorize/` |
| Token exchange | `https://open.tiktokapis.com/v2/oauth/token/` |
| Refresh | same as token URL with `grant_type=refresh_token` |

Note: docs show `v1/oauth/authorize` historically but v2 endpoint is current — verify at registration time.

## Token shape (saved to `token.json`)

```json
{
  "access_token": "act.xxx",
  "expires_in": 86400,
  "expires_at": "2026-05-26T09:46:00+00:00",
  "refresh_token": "rft.xxx",
  "refresh_expires_in": 31536000,
  "open_id": "...",
  "scope": "user.info.basic,video.publish,video.upload",
  "token_type": "Bearer"
}
```

## Implementation outline

File: `tiktok/upload.py` (single file, mirrors `youtube/upload.py`)

```python
"""TikTok uploader for FlowKit channels.

Each channel lives under tiktok/channels/<name>/:
- client_secrets.json   {client_key, client_secret, redirect_uri, scopes}
- token.json            Auto-created after first auth (refresh-able)
- channel_rules.json    display_name, tiktok_open_id, rules, seo, defaults
- upload_history.json   Auto-appended after each upload

Usage:
    # First-time auth
    python -m tiktok.upload --auth sach-thi-tham

    # Upload one video
    python -m tiktok.upload --channel sach-thi-tham \\
        --video output/podcast-book/dac_nhan_tam/ep_01_.../final_logo.mp4 \\
        --title "Đắc Nhân Tâm — Chương 1 #sach #audiobook" \\
        --privacy SELF_ONLY
"""

# OAuth helpers
def _pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge). SHA256 + base64url, no padding."""

def _build_auth_url(client_key, redirect_uri, scopes, state, code_challenge) -> str:
    """Build /v2/auth/authorize/ URL."""

def _exchange_code(client_key, client_secret, code, code_verifier, redirect_uri) -> dict:
    """POST /v2/oauth/token/ grant_type=authorization_code."""

def _refresh(client_key, client_secret, refresh_token) -> dict:
    """POST /v2/oauth/token/ grant_type=refresh_token. CRITICAL: respect rotation."""

def authorize(channel_name: str) -> dict:
    """Return valid token; refresh if near-expiry; run full flow if missing/expired-refresh."""
```

### Token flow (in `authorize`)

1. Load `token.json`. If missing → full flow (step 5+).
2. If `expires_at - now > 60s` → return token.
3. Else if refresh_token exists and not expired → POST refresh, **overwrite both access AND refresh** (rotation), save, return.
4. Else → fall through to full flow.
5. Full flow:
   - Generate PKCE pair
   - Print auth URL + instructions ("open in browser, after consent paste the `?code=` value")
   - Read code from stdin
   - Exchange code → token
   - Save `token.json`

### CLI auth wiring

`python -m tiktok.upload --auth <channel>` runs `authorize(channel)` and prints success + open_id verification.

### Open_id verification (matches youtube `get_service` pattern)

After token obtained, call `GET https://open.tiktokapis.com/v2/user/info/?fields=open_id,union_id,display_name` and check returned `open_id` matches `channel_rules.json:tiktok_open_id`. If mismatch → raise with same friendly message as `youtube/upload.py:117-123`.

## Dependencies

- `requests` (existing)
- stdlib: `hashlib`, `base64`, `secrets`, `urllib.parse`, `json`, `pathlib`, `datetime`

**Decision:** No `authlib` — manual PKCE is ~30 LOC, easier to audit, no extra dep.

## Files to create/modify

- Create: `tiktok/__init__.py` (empty)
- Create: `tiktok/upload.py` (OAuth portion ~120 LOC; upload portion in phase-03)
- Create: `tiktok/channels/sach-thi-tham/channel_rules.json` (stub, finalized in phase-04)

## Todo

- [ ] Create `tiktok/__init__.py`
- [ ] Create `tiktok/upload.py` with OAuth functions + `authorize()`
- [ ] PKCE helpers (verifier/challenge)
- [ ] `_build_auth_url`, `_exchange_code`, `_refresh`
- [ ] Token load/save with `expires_at` ISO timestamp
- [ ] `authorize()` orchestration (load → check expiry → refresh OR full flow)
- [ ] Open_id verification call after auth
- [ ] CLI `--auth <channel>` entrypoint
- [ ] Manual test: run `--auth sach-thi-tham`, paste code, verify `token.json` written
- [ ] Manual test: re-run `--auth`, verify cached token returned (no browser prompt)
- [ ] Manual test: force-expire token, verify refresh path

## Success criteria

- `python -m tiktok.upload --auth sach-thi-tham` succeeds, prints `OK — token can act on: <display_name> (<open_id>)`
- `token.json` valid, parseable, contains all fields including `expires_at`
- Re-running uses cached token without browser
- Refresh path triggers when `expires_at < now + 60s`

## Risks

| Risk | Mitigation |
|------|------------|
| HTTPS redirect lacks code-display page | User pastes code manually from URL bar — document clearly |
| TikTok rotates refresh token but we don't save it | Always save full response over old token |
| `state` parameter mismatch (CSRF) | Generate random `state`, verify on callback |
| Network/transient errors | Single retry with 2s backoff |

## Next

→ phase-03 once OAuth works end-to-end
