"""FastAPI router for Meta AI video generation via Playwright browser automation.

Mirrors the gemini browser path (/api/gemini/browser/*). Drives YOUR logged-in
Meta AI account in a persistent Chromium profile and captures the rendered video.
Bootstrap login once:  python scripts/meta_bootstrap.py
"""
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["meta"])

VIDEO_OUTPUT_DIR = Path("output/_shared/meta_video")


class GenerateVideoRequest(BaseModel):
    prompt: str
    image_path: Optional[str] = None  # local image for image→video (omit = text→video)
    timeout: float = 360.0
    headless: bool = True


@router.post("/meta/browser/generate-video")
async def browser_generate_video(body: GenerateVideoRequest):
    """Generate a video by driving meta.ai/create with Playwright.

    image_path → image→video; omit → text→video. Returns the saved local mp4 path.
    Requires a bootstrapped login profile (scripts/meta_bootstrap.py).
    """
    try:
        from agent.services.meta_browser import init_browser, MetaBrowserError
    except ImportError as e:
        return {"ok": False, "error": f"PLAYWRIGHT_NOT_INSTALLED: {e}"}

    try:
        browser = await init_browser(headless=body.headless)
        path = await browser.generate_video(
            body.prompt, image_path=body.image_path, timeout_s=body.timeout
        )
        return {
            "ok": True,
            "path": str(path),
            "filename": path.name,
            "size_kb": path.stat().st_size // 1024,
            "format": path.suffix.lstrip("."),
        }
    except MetaBrowserError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        logger.exception("browser_generate_video failed")
        return {"ok": False, "error": f"UNEXPECTED: {e}"}


class HarvestRequest(BaseModel):
    limit: int = 20


@router.post("/meta/browser/harvest")
async def browser_harvest(body: HarvestRequest):
    """Reclaim already-generated videos: open recent /prompt/<id> pages and return
    {url, prompt text, video src} for each. Match the text to a scene to download the
    correct existing video (no re-generation)."""
    try:
        from agent.services.meta_browser import init_browser, MetaBrowserError
    except ImportError as e:
        return {"ok": False, "error": f"PLAYWRIGHT_NOT_INSTALLED: {e}"}
    try:
        browser = await init_browser(headless=True)
        items = await browser.harvest(body.limit)
        return {"ok": True, "count": len(items), "items": items}
    except MetaBrowserError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        logger.exception("harvest failed")
        return {"ok": False, "error": f"UNEXPECTED: {e}"}


@router.post("/meta/browser/shutdown")
async def browser_shutdown():
    """Close the singleton Chromium so the persistent profile lock is released
    (lets standalone scripts like meta_vibes_inspect.py reuse the same login)."""
    try:
        from agent.services.meta_browser import shutdown_browser, is_browser_ready
        was_ready = is_browser_ready()
        await shutdown_browser()
        return {"ok": True, "was_ready": was_ready, "ready": False}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/meta/browser/status")
async def browser_status():
    try:
        from agent.services.meta_browser import is_browser_ready, PROFILE_DIR
    except ImportError:
        return {"available": False, "error": "playwright not installed"}
    return {
        "available": True,
        "ready": is_browser_ready(),
        "profile_dir": str(PROFILE_DIR),
        "profile_exists": Path(PROFILE_DIR).exists(),
        "output_dir": str(VIDEO_OUTPUT_DIR),
    }
