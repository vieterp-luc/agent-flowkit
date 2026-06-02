# fk-gen-meta-video — Generate Video via Meta AI (Browser Automation)

Generate a video by driving the **Meta AI web app** (`meta.ai/create`) with Playwright —
same "drive-the-real-UI + capture the rendered file" approach as Gemini Lyria in
`/fk-gen-music`. No public API exists for Meta AI video, so this controls YOUR own
logged-in account in a persistent Chromium profile. Supports **image→video** (attach an
image + describe) and **text→video** (describe only).

> ⚠️ **Read before using.** Meta AI has **no official video API** and its Terms of
> Service restrict automated access. There is **no commercial usage license** for
> Meta AI-generated video and output carries Meta/SynthID watermarks. Do **not** use
> this for monetized YouTube/Shorts content — for that, stay on Google Veo via
> `/fk-gen-videos`. This skill is for personal experiments / manual-equivalent use of
> your own account. Use at your own risk of rate-limits or account action.

## Prerequisites

- GLA server running: `curl -s http://127.0.0.1:8100/health`
- Playwright installed (shared with the Gemini path):
  `venv/bin/pip install playwright && venv/bin/python -m playwright install chromium`
- **Bootstrap login once** (headed window — log into Meta AI via FB/IG/Meta account, then close it):
  ```bash
  venv/bin/python scripts/meta_bootstrap.py
  ```
  Session is saved to `output/_shared/meta_profile/` (gitignored, separate from Gemini).

## How it works

Drives `meta.ai/create`: (optionally upload an image via the hidden file input) → type the
prompt into the `composer-input` editor → click the **send arrow** → wait. Meta renders
**4 variations and is slow (often 3–9 min)**.

**Key gotcha — Meta's SPA does NOT live-update the grid.** When a generation finishes, the
page stays on "Imagining" while the video is actually ready. So the service **reloads the
page every ~45s** while waiting; after a reload the finished result appears at the top of
the grid with its `fbcdn` `<video>` src, and the topmost new src (vs a pre-submit baseline)
is downloaded. **Always allow a generous `timeout` (≥600s).**

## Generate

```bash
# image → video  (image_path = local file: jpg/png/webp/mp4/mov)
curl -X POST http://127.0.0.1:8100/api/meta/browser/generate-video \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "gentle ripples on the water, slow cinematic push-in, soft dawn light",
    "image_path": "output/<project>/img/scene_00.jpg",
    "timeout": 600,
    "headless": true
  }'

# text → video  (omit image_path)
curl -X POST http://127.0.0.1:8100/api/meta/browser/generate-video \
  -d '{"prompt":"a calm koi pond at dawn, cinematic","timeout":600}'

# Response:
# {"ok": true, "path": "output/_shared/meta_video/<name>.mp4",
#  "filename": "<name>.mp4", "size_kb": 1234, "format": "mp4"}
```

| Field | Default | Notes |
|-------|---------|-------|
| `prompt` | (required) | Scene description, typed verbatim. Keep visual + motion; no need for Veo-style Audio/SFX/Negative lines. |
| `image_path` | `null` | Local image → **image→video**. Omit for **text→video**. |
| `timeout` | `360` | **Set ≥600** — real gen often takes 3–9 min; this is the ceiling (returns as soon as the result appears). |
| `headless` | `true` | `false` opens a visible Chromium window (debug). The singleton keeps the mode of its first init — call `/shutdown` to switch. |

Output mp4 is saved under `output/_shared/meta_video/`. Aspect ratio follows the input image
(vertical image → 9:16 clip). Move/rename it into your project as needed.

## Batch (multi-scene) — PROVEN pattern

Meta is fine for back-to-back generations **as long as each waits for its result with a
≥600s ceiling + periodic reload** (it is NOT throttled — the earlier "throttle" theory was
a misdiagnosis of the SPA-staleness bug). Drive sequentially (the browser lock serializes
anyway), with a small gap between scenes:

- One generation at a time (`image_path` per scene).
- `timeout: 600`, ~30s gap between scenes.
- Move each returned `path` → `output/<project>/clips/scene_NN.mp4`.
- Re-run to retry only missing scenes (skip ones whose clip already exists).

Write a small driver that loops the scenes → calls the endpoint per scene → moves each
returned `path` into `output/<project>/clips/scene_NN.mp4`, logging progress. Run it
detached (`nohup python3 <driver> &`) and poll the log — gens take minutes each.

## Release the browser (for inspect scripts / RAM)

The server holds a singleton Chromium on the persistent profile. To run a standalone script
(e.g. `meta_vibes_inspect.py`) that needs the same login, or to free RAM, release it first:

```bash
curl -X POST http://127.0.0.1:8100/api/meta/browser/shutdown
```

## Status & selector drift

```bash
curl -s http://127.0.0.1:8100/api/meta/browser/status
# → {"available": true, "ready": bool, "profile_dir": "...", "profile_exists": bool}
```

Meta's DOM is undocumented and shifts. Selectors live centrally in
`agent/services/meta_selectors.py`. If generation breaks (`COMPOSER_NOT_FOUND`, no capture),
re-discover them:

```bash
# dumps composer / file-input / button / video candidates on /create to a log
venv/bin/python scripts/meta_vibes_inspect.py --wait 240   # do the flow manually in the window
venv/bin/python scripts/meta_inspect_dom.py "a cat surfing" --wait 120
```

Then patch `meta_selectors.py`. Verified anchors: composer `textarea[data-testid="composer-input"]`,
upload `input[type=file]` (hidden, set directly), submit = send button (`aria-label*="Send"`,
NOT Enter — composer re-renders once an image is attached), results = `fbcdn` `<video>` srcs.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `LOGIN_EXPIRED` | Meta session expired/missing | Re-run `scripts/meta_bootstrap.py` |
| `IMAGE_NOT_FOUND` / `IMAGE_UPLOAD_FAILED` | Bad `image_path` or rejected format | Check path + format (jpg/png/webp/mp4/mov) |
| `COMPOSER_NOT_FOUND` | UI/selector drift | Run `meta_vibes_inspect.py`, patch `COMPOSER` in `meta_selectors.py` |
| `VIDEO_TIMEOUT after Ns` | Timeout too short, or gen still running | Use `timeout: 600`+; the reload-capture needs the gen to finish |
| `BLOCKED` | Quota / safety refusal | Wait for reset or rephrase prompt |
| `PLAYWRIGHT_NOT_INSTALLED` | Missing dep | `venv/bin/pip install playwright && venv/bin/python -m playwright install chromium` |

## Notes

- One generation at a time (browser lock serializes calls).
- Profile is **separate** from the Gemini music profile and from the Flow Chrome extension —
  no conflict with `/fk-gen-videos` or `/fk-gen-music`.
- Code: `agent/services/meta_browser.py` + `meta_selectors.py` + `agent/api/meta.py`. Mirrors
  the Gemini browser path; if Meta ships a real API, swap `meta_browser.py` internals only.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/meta/browser/generate-video` | POST | Generate video (image→video or text→video); returns saved mp4 path |
| `/api/meta/browser/status` | GET | Browser singleton readiness + profile path |
| `/api/meta/browser/shutdown` | POST | Close singleton browser → release profile lock |
