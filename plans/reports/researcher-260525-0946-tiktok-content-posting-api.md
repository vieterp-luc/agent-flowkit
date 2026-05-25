# TikTok Content Posting API v2 (Direct Post) Research Report

**Date:** 2026-05-25  
**Scope:** Flow Kit `/fk-tiktok-upload` skill for Vietnamese book podcasts (1080x1920 vertical, 3-10 min)  
**Channel:** sach-thi-tham | **Stack:** Python (patterns from existing `fk-youtube-upload`)

---

## 1. Developer App Registration

### Setup Steps
1. Register app at [developers.tiktok.com/apps](https://developers.tiktok.com/apps)
2. Add **Content Posting API** product to app
3. Enable **Direct Post** in app settings
4. Request approval for `video.publish` scope

### OAuth Scopes Explained

| Scope | Use Case | Approval | Mode |
|-------|----------|----------|------|
| `video.upload` | Upload to creator's *inbox/drafts* | Auto (sandbox-ready) | Draft (editable) |
| `video.publish` | Direct publish to creator's feed | **Requires audit** | Direct Post (auto-public) |

**CRITICAL:** Only `video.publish` scope enables Direct Post auto-publish behavior. `video.upload` creates draft videos requiring manual creator review.

### Audit & Sandbox
- **Unaudited mode:** All content forced to SELF_ONLY (private) regardless of settings
- **Audited mode:** Unlocks PUBLIC_TO_EVERYONE posting after 2-4 week audit process
- **Unaudited limits:** Max 5 unique users posting per 24h via single app client
- **Testable without audit:** Sandbox mode with `video.upload` scope (drafts only)

**GOTCHA:** Unaudited Direct Post posts are **permanently private** — creator must manually change privacy + edit each post to make public after account visibility changes. User expectation management critical.

### Compliance Audit Requirements
TikTok audits for Terms of Service compliance. Submit:
- Demo video of functionality
- Privacy policy URL (for your app)
- Terms of Service URL (for your app)
- Use case description

---

## 2. OAuth 2.0 Flow (PKCE Required)

### Endpoints & TTL

| Component | Value/URL | Notes |
|-----------|-----------|-------|
| **Auth URL** | `https://www.tiktok.com/v1/oauth/authorize/` | Redirect user here for consent |
| **Token URL** | `https://open.tiktokapis.com/v2/oauth/token/` | Exchange code for tokens |
| **Access Token TTL** | 24 hours | Expires; triggers refresh |
| **Refresh Token TTL** | 365 days | Must rotate if server returns new token |

### Redirect URI Requirements
- **HTTPS required** (no localhost exceptions documented)
- **Consistent across flow** — must match exactly in auth request + token exchange
- **Pre-registered in app settings** on developers.tiktok.com

### PKCE (Proof Key Code Exchange)
- **Required for:** Desktop/CLI apps (mobile apps already require it)
- **Code verifier:** 43-128 char random string
- **Code challenge:** SHA256(verifier) base64url-encoded
- Both desktop & mobile send `code_challenge` in auth request

### Token Storage Best Practice (per TikTok docs)
```
store on backend → not in frontend/config
include in all requests as: Authorization: Bearer {access_token}
```

### Refresh Token Rotation
> "The returned refresh_token may be different than the one passed in. You must use the newly-returned token if different."

Always store/use the returned refresh token from refresh responses, not cached ones.

---

## 3. Direct Post Endpoints & Request Specs

### Initialization: `/v2/post/publish/video/init/`

**Method:** POST  
**Auth:** Bearer token + `video.publish` scope  
**Rate:** 6 requests/min per user token (1-min sliding window)

**Request Body Example (FILE_UPLOAD mode):**
```json
{
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_size": 52428800,
    "chunk_size": 5242880,
    "total_chunk_count": 10
  },
  "post_info": {
    "title": "Chap 1: Thế thớt Hồ Ba Bể #sachtitham #audiobook",
    "privacy_level": "SELF_ONLY",
    "disable_duet": false,
    "disable_stitch": false,
    "disable_comment": false,
    "video_cover_timestamp_ms": 0,
    "brand_content_toggle": false,
    "brand_organic_toggle": false
  }
}
```

**Alternative: PULL_FROM_URL (for URL sources)**
```json
{
  "source_info": {
    "source": "PULL_FROM_URL",
    "video_url": "https://example.com/video.mp4"
  },
  "post_info": { ... }
}
```

**Response:**
```json
{
  "data": {
    "publish_id": "7..."
  },
  "upload_url": "https://...",
  "upload_expire_at": 3600
}
```

### Post Info Fields

| Field | Type | Options/Limits | Notes |
|-------|------|----------------|-------|
| `title` | String | Max 2200 UTF-16 runes | Hashtags inline OK |
| `privacy_level` | Enum | PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY | Unaudited = forced SELF_ONLY |
| `disable_duet` | Bool | true/false | Prevent duet remixes |
| `disable_stitch` | Bool | true/false | Prevent stitch edits |
| `disable_comment` | Bool | true/false | Disable comments |
| `video_cover_timestamp_ms` | Int | Milliseconds | Custom thumbnail frame |
| `brand_content_toggle` | Bool | true/false | Creator fund eligible |
| `brand_organic_toggle` | Bool | true/false | Brand partnership indicator |

**AIGC Label fields:** TikTok supports `generated_data_toggle` (not shown in examples; check latest docs if using AI narration).

### Chunked Upload: `/v2/post/publish/video/upload/`

**Protocol:** HTTP PUT (sequential only, not parallel)

**Chunk Headers:**
```
PUT {upload_url}
Content-Range: bytes 0-5242879/52428800
Content-Type: video/mp4
Content-Length: 5242880

[binary chunk data]
```

**Response Codes:**
- 206 Partial Content (chunks 1 to N-1)
- 201 Created (final chunk)

**Constraints:**
- **Chunk size:** Min 5 MB, max 64 MB (final chunk can be up to 128 MB)
- **Total chunks:** 1–1000 max
- **Sequential:** Must upload in order; parallel not supported
- **Timeout:** `upload_url` valid 1 hour only

**Calculation Example (50 MB file):**
```
chunk_size = 5242880 (5 MB)
total_chunk_count = ceil(50MB / 5MB) = 10
final_chunk < 64 MB → single final chunk OK
```

### Status Check: `/v2/post/publish/status/fetch/`

**Method:** POST  
**Request:**
```json
{
  "publish_id": "7..."
}
```

**Response:**
```json
{
  "data": {
    "status": "PROCESSING|SUCCESS|FAILED",
    "error_code": "...",
    "error_message": "..."
  }
}
```

**Status Values:**
- `PROCESSING` — Upload complete, encoding in progress (poll every 2-5 sec)
- `SUCCESS` — Video published, live on creator feed
- `FAILED` — Error (check error_code; see GOTCHAS section)

---

## 4. Constraints & Limits

### File & Media
| Constraint | Value | Notes |
|-----------|-------|-------|
| Max file size | 4 GB | Chunked upload up to 1000 chunks |
| Video duration | 3–600 sec | 3 sec min, 10 min max (60 min for some creators) |
| Resolution | 1080×1920 (9:16) | Min 360×640; full-screen fill requires 1080×1920 |
| Codec | H.264, High Profile, Level 4.2 | Most compatible |
| Bitrate | 8–15 Mbps (VBR) | <5 Mbps → quality downgrade; >20 Mbps → reduced |
| Frame rate | 23–60 fps | 30 fps recommended |
| Audio codec | AAC | 44.1 kHz sample rate |
| Container | MP4 / QuickTime / WebM | MP4 + H.264 most compatible |

### API Quotas
| Limit | Value | Scope |
|-------|-------|-------|
| Init requests | 6/min | Per user token (sliding window) |
| Pending uploads | 5 | Per 24h per user |
| Daily posts (unaudited) | 5 unique users | Per 24h per app client |
| Daily posts (audited) | ~15 posts/creator | Varies; shared across all clients |

**GOTCHA:** Rate limit triggers HTTP 429 (`rate_limit_exceeded`). Implement exponential backoff. Quota reset happens daily UTC 00:00 (timezone varies; test empirically).

---

## 5. Direct Post Audit Requirement (CRITICAL GOTCHA)

### Unaudited Behavior
> "All content posted by unaudited clients will be restricted to private viewing mode."

**Even if you request `privacy_level: "PUBLIC_TO_EVERYONE"`, unaudited posts are FORCED to SELF_ONLY (creator-only).**

Workflow for unaudited app:
1. Upload + publish via API → `privacy_level: PUBLIC_TO_EVERYONE` in request
2. Post lands on creator's feed as **SELF_ONLY** (private/invisible to followers)
3. Creator manually opens post → settings → change privacy to "Everyone"
4. Post now visible (but creator must do this manually per-post)

### Audit Timeline
- **Duration:** 2–4 weeks (typically multiple review rounds)
- **Submission:** Requires privacy policy, terms URL, demo video, use case
- **Outcome:** Approval or rejection with feedback
- **Resubmit:** Address feedback, resubmit (can cycle multiple times)

### What Gets Audited
- Code compliance (terms enforcement, data handling)
- Use case legitimacy (no spam/manipulation detection)
- Brand safety (content moderation)

### Setting User Expectations
**For unaudited Flow Kit deployment:** Explicitly communicate to Vietnamese podcast creators that Direct Post will publish private videos only until app audit completes. Provide manual privacy-change instructions or consider Draft mode (`video.upload` scope) as workaround.

---

## 6. Python Libraries & SDK Options

### Official TikTok SDK

**`tiktok-business-api-sdk-official`** (PyPI)  
- [GitHub](https://github.com/tiktok/tiktok-business-api-sdk)
- Covers Business API + Ads API; does NOT cover Content Posting API (creator-focused)
- Mature, but not our use case

### Community Content Posting Implementations

**Best Options:**

1. **`tiktok-api-client`** (PyPI: `tiktok-api-client`)
   - OAuth 2.0 + PKCE built-in
   - Direct support for `video.publish` + `video.upload`
   - Actively maintained (as of 2025)
   - **Recommendation:** Check if it wraps chunked upload or requires raw HTTP calls

2. **Direct HTTP (Recommended for Flow Kit)**
   - Use `requests` library (already in stack; matches `fk-youtube-upload` pattern)
   - Handle OAuth 2.0 manually (simple; ~50 lines)
   - Chunked upload explicit via `requests.put()` with Content-Range
   - Full control, no SDK overhead

3. **PyTok** (`python-tiktok`)
   - Lightweight wrapper around official APIs
   - PKCE support
   - Needs verification if Content Posting API v2 is covered

### Why Direct HTTP Over SDK

- Flow Kit uses `google-api-python-client` pattern (low-level control)
- TikTok SDK (Business API) doesn't cover Content Posting API v2
- Chunked upload protocol is simple PUT requests
- Easier to debug + match existing `scripts/youtube_upload.py` architecture

**Recommendation:** Implement with `requests` + standard OAuth 2.0 library (e.g., `authlib` or `oauthlib`). Avoid premature SDK dependency.

---

## 7. Reference Implementations (GitHub)

### Evaluated Repos

**1. [tiktok-api-client (PyPI)](https://pypi.org/project/tiktok-api-client/)**
- **Status:** Maintained 2025
- **Code quality:** High (OAuth2/PKCE, type hints)
- **Content Posting Coverage:** Yes (POST /v2/post/publish/video/init/)
- **Chunked upload:** Unknown (needs repo verification)
- **Recommendation:** Good reference; check chunked upload implementation

**2. [tiktok-uploader (wkaisertexas)](https://github.com/wkaisertexas/tiktok-uploader)**
- **Status:** Active 2025
- **Approach:** Playwright automation (not API; bypasses auth)
- **Pros:** Works without app approval
- **Cons:** Fragile (TikTok UI changes), not production-grade
- **Recommendation:** Avoid for `/fk-tiktok-upload`; violates TikTok ToS

**3. [pytok (fweinelt)](https://github.com/fweinelt/pytok)**
- **Status:** Sparse recent activity
- **Coverage:** API wrapper; check Content Posting v2 support
- **Recommendation:** Verify before use; may be outdated

### No Official TikTok Python SDK for Content Posting API
- Business API SDK (official) does NOT cover Content Posting
- Content Posting is creator-focused; Business API is advertiser/analytics focused
- **Conclusion:** Build own thin wrapper around `requests` + OAuth 2.0

---

## Implementation Path (Recommended)

### Stack
- **Auth:** `authlib` or `requests_oauthlib` (familiar pattern)
- **HTTP:** `requests` (chunked PUT with Content-Range)
- **Storage:** JSON file (tokens) or secure env (production)
- **Pattern:** Match `scripts/youtube_upload.py` (functions: auth, upload_init, upload_chunks, status_poll)

### Minimal Code Skeleton
```python
# auth.py
import authlib
# OAuth 2.0 flow, PKCE, token refresh

# upload.py
import requests
# POST /v2/post/publish/video/init/
# PUT {upload_url} with Content-Range (sequential chunks)
# POST /v2/post/publish/status/fetch/ (poll until SUCCESS/FAILED)

# config.py
# client_key, client_secret, redirect_uri (HTTPS)
# sach-thi-tham channel metadata
```

### Testing (Before Audit)
1. Register app, request `video.publish` scope
2. Test OAuth 2.0 flow (auth.py) → manual user consent
3. Upload small test video (< 5 MB, 1 chunk)
4. Verify SELF_ONLY restriction (unaudited)
5. Check status polling (PROCESSING → SUCCESS/FAILED)

### Gotchas to Handle
- **Rate limit 429:** Retry with exponential backoff
- **Upload URL expiry (1h):** Re-init if chunk takes >1h
- **Sequential chunks:** No parallelization
- **SELF_ONLY enforcement:** Document user expectation
- **Audit blockers:** Plan audit submission early (2-4 week turnaround)

---

## Unresolved Questions

1. **Chunked upload resume/retry:** TikTok docs don't specify if resending a chunk (same Content-Range) is idempotent. Assume yes; test with manual retry.

2. **PULL_FROM_URL domain whitelist:** Docs mention "pre-verified domain URLs" for PULL_FROM_URL mode. What domains are pre-approved? GCS bucket URLs? Need to test.

3. **AIGC label fields:** Docs hint at `generated_data_toggle` for AI narration. Current documentation examples don't show field names/values. Verify with latest API reference.

4. **Max resolution encoding:** Can 1080×1920 + H.264 High Profile 4.2 at 15 Mbps / 30 fps fit in 4 GB? Roughly yes (650 min ≈ 10+ hours), but edge case near 4 GB + 10 min limit → test empirically.

5. **Refresh token rotation frequency:** Docs say "may be different"; doesn't specify how often. Assume always update; test in 365-day lifecycle.

6. **Creator info endpoint:** `/creator_info/query/` mentioned for privacy settings validation. Need full spec (request body, response fields, rate limit).

7. **Brand content eligibility audit:** Does passing Content Posting audit auto-approve `brand_content_toggle`, or separate submission?

---

## Sources

- [TikTok Content Posting API Guide](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)
- [TikTok Content Posting API Get Started](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [TikTok Content Posting API Media Transfer Guide](https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide)
- [TikTok OAuth User Access Token Management](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [TikTok Content Posting API Reference Upload Video](https://developers.tiktok.com/doc/content-posting-api-reference-upload-video)
- [TikTok API Scopes Documentation](https://developers.tiktok.com/doc/tiktok-api-scopes)
- [TikTok API v2 Rate Limits](https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit)
- [TikTok tiktok-api-client PyPI](https://pypi.org/project/tiktok-api-client/)
- [TikTok Business API SDK GitHub](https://github.com/tiktok/tiktok-business-api-sdk)
- [tiktok-uploader GitHub](https://github.com/wkaisertexas/tiktok-uploader)
