"""FastAPI router for Gemini Bridge — music generation and capture via Chrome extension."""
import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, UploadFile, File, Form
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["gemini"])

# Pending requests waiting for Gemini extension response
_pending: dict[str, asyncio.Future] = {}

# Music entries captured from Gemini by the extension
_captured_music: list[dict] = []

# Gemini WS connection (set by main.py ws handler)
_gemini_ws = None

MUSIC_OUTPUT_DIR = Path("output/_shared/gemini_music")


def set_gemini_ws(ws) -> None:
    global _gemini_ws
    _gemini_ws = ws


def get_gemini_ws():
    return _gemini_ws


def resolve_pending(req_id: str, data: dict) -> bool:
    future = _pending.pop(req_id, None)
    if future and not future.done():
        future.set_result(data)
        return True
    return False


def handle_music_captured(entry: dict) -> None:
    _captured_music.insert(0, entry)
    if len(_captured_music) > 100:
        _captured_music.pop()
    logger.info("Gemini music captured: %s", entry.get("filename"))


def _unique_dest(filename: str) -> Path:
    MUSIC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = MUSIC_OUTPUT_DIR / filename
    counter = 1
    while dest.exists():
        dest = MUSIC_OUTPUT_DIR / f"{Path(filename).stem}_{counter}.mp4"
        counter += 1
    return dest


async def _send_to_extension(method: str, params: dict, timeout: float = 200.0) -> dict:
    """Send a request to the Gemini extension and await its response."""
    ws = _gemini_ws
    if ws is None:
        raise RuntimeError("Gemini extension not connected")
    req_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    _pending[req_id] = future
    import json
    await ws.send(json.dumps({"id": req_id, "method": method, "params": params}))
    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        if result.get("error"):
            raise RuntimeError(result["error"])
        return result.get("result", result.get("data", {}))
    except asyncio.TimeoutError:
        _pending.pop(req_id, None)
        raise RuntimeError(f"Extension timeout after {timeout}s")


# ─── Endpoints ──────────────────────────────────────────────

class GenerateMusicRequest(BaseModel):
    prompt: str
    lang: str = "vi"
    timeout: float = 200.0


@router.post("/gemini/generate-music")
async def generate_music(body: GenerateMusicRequest):
    """Generate music via Gemini (sends StreamGenerate request through extension with browser cookies)."""
    prev_count = len(_captured_music)
    try:
        result = await _send_to_extension(
            "generate_music",
            {"prompt": body.prompt, "lang": body.lang},
            timeout=body.timeout,
        )
        # Wait a moment for upload to complete if music was just captured
        if result.get("ok") and len(_captured_music) > prev_count:
            await asyncio.sleep(3)
        return {"ok": True, "entry": _captured_music[0] if _captured_music else result.get("entry")}
    except RuntimeError as e:
        return {"ok": False, "error": str(e)}


@router.get("/gemini/session-status")
async def session_status():
    """Check if extension has valid session params for music generation."""
    if _gemini_ws is None:
        return {"connected": False, "session_ready": False}
    try:
        result = await _send_to_extension("get_session_status", {}, timeout=5.0)
        return {"connected": True, **result}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.post("/gemini/music-upload")
async def music_upload(
    file: UploadFile = File(...),
    filename: str = Form(...),
    id: str = Form(default=""),
):
    """Receive music binary uploaded by extension (fetched with browser cookies)."""
    dest = _unique_dest(filename)
    dest.write_bytes(await file.read())
    size_kb = dest.stat().st_size // 1024
    logger.info("Gemini music saved: %s (%d KB)", dest, size_kb)
    for entry in _captured_music:
        if entry.get("id") == id or entry.get("filename") == filename:
            entry["local_path"] = str(dest)
            break
    return {"ok": True, "path": str(dest), "size_kb": size_kb}


@router.post("/gemini/callback")
async def gemini_callback(request: Request):
    """HTTP callback from extension — resolves pending futures."""
    data = await request.json()
    req_id = data.get("id")
    if req_id and resolve_pending(req_id, data):
        return {"ok": True}
    return {"ok": False, "reason": "no matching pending request"}


@router.get("/gemini/status")
async def gemini_status():
    return {
        "connected": _gemini_ws is not None,
        "captured_music_count": len(_captured_music),
        "pending_requests": len(_pending),
        "music_output_dir": str(MUSIC_OUTPUT_DIR),
    }


@router.get("/gemini/music")
async def list_captured_music(limit: int = 20):
    return _captured_music[:limit]


@router.delete("/gemini/music")
async def clear_captured_music():
    _captured_music.clear()
    return {"ok": True}


# ─── Playwright Browser Path (Phase 2) ──────────────────────


class BrowserGenerateMusicRequest(BaseModel):
    prompt: str
    model: str = "Pro"  # Pro = 2-3min tracks; Nhanh = 30s
    timeout: float = 300.0
    headless: bool = True
    audio_format: str = "mp3"  # "mp3" (default, smaller) or "mp4" (raw container from Gemini)


def _transcode_to_mp3(mp4_path: Path, delete_source: bool = True) -> Path:
    """Convert audio-only MP4 (from Gemini) to MP3 192k. Returns mp3 path."""
    import subprocess
    mp3_path = mp4_path.with_suffix(".mp3")
    cmd = [
        "ffmpeg", "-y", "-i", str(mp4_path),
        "-vn", "-acodec", "libmp3lame", "-b:a", "192k",
        str(mp3_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg mp3 transcode failed: {result.stderr[:300]}")
    if delete_source:
        try:
            mp4_path.unlink()
        except OSError:
            pass
    return mp3_path


@router.post("/gemini/browser/generate-music")
async def browser_generate_music(body: BrowserGenerateMusicRequest):
    """Generate music by driving the Gemini UI with Playwright (no extension required).

    Default audio_format="mp3" — transcodes the captured MP4 container into MP3 192k
    (smaller, faster) and deletes the original MP4. Set audio_format="mp4" to keep raw.
    """
    try:
        from agent.services.gemini_browser import (
            init_browser,
            GeminiBrowserError,
        )
    except ImportError as e:
        return {"ok": False, "error": f"PLAYWRIGHT_NOT_INSTALLED: {e}"}

    try:
        browser = await init_browser(headless=body.headless)
        path = await browser.generate_music(
            body.prompt, timeout_s=body.timeout, model=body.model
        )
        if body.audio_format == "mp3":
            try:
                path = _transcode_to_mp3(path, delete_source=True)
            except RuntimeError as e:
                logger.warning("MP3 transcode failed, returning MP4: %s", e)
        size_kb = path.stat().st_size // 1024
        return {
            "ok": True,
            "path": str(path),
            "filename": path.name,
            "size_kb": size_kb,
            "model": body.model,
            "format": path.suffix.lstrip("."),
        }
    except GeminiBrowserError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        logger.exception("browser_generate_music failed")
        return {"ok": False, "error": f"UNEXPECTED: {e}"}


@router.get("/gemini/browser/status")
async def browser_status():
    try:
        from agent.services.gemini_browser import is_browser_ready, PROFILE_DIR
        from pathlib import Path as _P
    except ImportError:
        return {"available": False, "error": "playwright not installed"}
    return {
        "available": True,
        "ready": is_browser_ready(),
        "profile_dir": str(PROFILE_DIR),
        "profile_exists": _P(PROFILE_DIR).exists(),
    }
