# Phase 03 — Python Upload Module (Init + Chunked PUT + Status Poll)

**Status:** ⏳ Pending (depends on phase-02)
**Priority:** P0
**Owner:** Claude (`fullstack-developer` agent)

## Context

- Research: `plans/reports/researcher-260525-0946-tiktok-content-posting-api.md` §3, §4
- Mirror pattern: `youtube/upload.py:133-190` (`upload_video`)

## Objective

Implement Direct Post upload flow: probe file → init upload → PUT chunks → poll status → append history.

## Endpoints

| Step | Endpoint | Method |
|------|----------|--------|
| Init | `https://open.tiktokapis.com/v2/post/publish/video/init/` | POST |
| Upload chunk | `{upload_url}` (from init response) | PUT |
| Status | `https://open.tiktokapis.com/v2/post/publish/status/fetch/` | POST |

## Constraints (enforce in code)

- File size: ≤ 4 GB
- Duration: 3-600 sec (max 10 min)
- Chunk size: 5 MB ≤ size ≤ 64 MB (final chunk up to 128 MB)
- Total chunks: 1-1000
- Sequential PUT only — no parallelism
- `upload_url` expires in 1 hour
- Resolution recommend 1080×1920 9:16, H.264 + AAC
- Rate limit: 6 init calls/min/user

## Implementation outline

```python
import math
import time
from pathlib import Path

CHUNK_SIZE = 10 * 1024 * 1024   # 10 MB — within [5MB, 64MB]
INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"


def _probe(video_path: Path) -> dict:
    """ffprobe → duration_s, size_bytes. Validate against TikTok limits."""

def _init_upload(token: str, video_size: int, post_info: dict) -> dict:
    """POST /v2/post/publish/video/init/ → {publish_id, upload_url, ...}."""

def _put_chunks(upload_url: str, video_path: Path, chunk_size: int, total_chunks: int):
    """Sequentially PUT bytes with Content-Range headers. Progress prints."""

def _poll_status(token: str, publish_id: str, timeout_s: int = 600) -> dict:
    """Poll every 3s until SUCCESS / FAILED / timeout."""

def upload_video(
    channel_name: str,
    video_path,
    title: str,
    privacy_level: str = "SELF_ONLY",  # safe default until audited
    disable_duet: bool = False,
    disable_stitch: bool = False,
    disable_comment: bool = False,
    cover_timestamp_ms: int = 0,
    brand_content: bool = False,
    brand_organic: bool = False,
) -> dict:
    """Full Direct Post upload. Returns {publish_id, status, share_url_or_none}."""
```

### Upload flow detail

1. Resolve video path: if user passed dir or partial path, fallback `final_logo.mp4` → `final.mp4`
2. Probe (size, duration). Validate against constraints — raise `ValueError` with clear message if violated.
3. `authorize(channel_name)` → fresh token
4. Compute `chunk_size`, `total_chunk_count` (round up; final chunk allowed up to 128 MB)
5. POST init with `source_info` + `post_info`. Catch 429 → exponential backoff 2s/4s/8s, max 3 retries.
6. For each chunk index 0..N-1:
   - Read bytes via file seek + read
   - PUT to `upload_url` with `Content-Range: bytes START-END/TOTAL`, `Content-Type: video/mp4`, `Content-Length: <chunk>`
   - Expect 206 for intermediate, 201 for final
   - On non-2xx → retry once with same range
   - Print progress `[chunk N/M | XX%]`
7. Poll status every 3s, max 10 min. Status `SUCCESS` → done; `FAILED` → raise with `error_code` + `error_message`; timeout → log warning, append history as PENDING.
8. Append to `upload_history.json` (channel-dir):
   ```json
   {
     "publish_id": "7...",
     "video_path": "...",
     "title": "...",
     "privacy_level": "SELF_ONLY",
     "uploaded_at": "<ISO>",
     "final_status": "SUCCESS",
     "share_url": null
   }
   ```

### Video source resolution helper

```python
def _resolve_video(arg: str) -> Path:
    """If arg is dir, prefer final_logo.mp4 then final.mp4. If file, use directly."""
    p = Path(arg)
    if p.is_dir():
        for cand in ("final_logo.mp4", "final.mp4"):
            if (p / cand).exists():
                return p / cand
        raise FileNotFoundError(f"No final*.mp4 in {p}")
    if not p.exists():
        raise FileNotFoundError(p)
    return p
```

## Error handling matrix

| TikTok error | Action |
|--------------|--------|
| 429 rate_limit_exceeded | Exponential backoff 2s/4s/8s, retry 3× |
| 400 invalid_param | Log details, raise — fix on caller side |
| 401 token_expired | Re-authorize once, retry |
| 5xx | Retry 3× with backoff |
| status=FAILED `video_pull_failed` | Likely codec/duration issue — print probe info, raise |
| Upload URL expired (50x mid-upload) | Re-init from scratch, restart chunks |

## Files to modify

- Append to `tiktok/upload.py` (functions above; total file target < 250 LOC matching `youtube/upload.py`)

## Todo

- [ ] `_probe()` using ffprobe (subprocess) — return `{size, duration, codec, resolution}`
- [ ] Constraint validator with clear error messages
- [ ] `_init_upload()` with retry on 429
- [ ] `_put_chunks()` sequential, Content-Range header math
- [ ] `_poll_status()` with timeout
- [ ] `_resolve_video()` for dir/file input
- [ ] `upload_video()` orchestrator
- [ ] Append to `upload_history.json`
- [ ] Manual test: upload 30s test clip → verify SELF_ONLY on phone
- [ ] Manual test: upload real ep_NN/final_logo.mp4 (3-8 min)
- [ ] Manual test: force 429 (rapid retry) → verify backoff

## Success criteria

- Test clip uploads, `publish_id` returned, status SUCCESS within 60s
- Real episode (5-8 min, ~80MB) uploads in <90s on home connection
- `upload_history.json` accurate, contains publish_id + final_status
- All TikTok constraints enforced pre-flight (no failed init due to client-side preventable errors)

## Risks

| Risk | Mitigation |
|------|------------|
| Chunks fail mid-upload, partial state | Restart from init (URL re-fetch) — no resume support in API |
| Encoding fails post-upload (status FAILED) | Pre-validate via ffprobe (codec, fps, bitrate) before init |
| Quota burn during dev (5 unaudited users/day) | Use SELF_ONLY exclusively during dev; delete test posts from app |
| Slow status (audio sync re-encode) | 10 min timeout — log PENDING and let user manual-check next run |

## Next

→ phase-04 (skill markdown + channel_rules.json)
