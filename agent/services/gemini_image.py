"""Image generation via the Gemini API (Nano Banana / gemini-2.5-flash-image) with
key-pool rotation.

Uses a DEDICATED key pool (separate from the text pool) because image and text have
independent free-tier per-day caps on the Gemini API — marking a key "daily-exhausted"
for image must not block text/music features that share the same keys.

Imagen (imagen-*:predict) is paid-only; this uses the free-tier-capable
`gemini-2.5-flash-image` via :generateContent with responseModalities IMAGE.
"""
import base64
import logging
import uuid
from pathlib import Path
from typing import Optional

from agent.config import GEMINI_API_KEYS
from agent.services.gemini_key_pool import GeminiKeyPool, call_gemini_async

logger = logging.getLogger(__name__)

IMAGE_MODEL = "gemini-2.5-flash-image"
OUTPUT_DIR = Path("output/_shared/gemini_images")

_VERTICAL = {"9:16", "3:4", "2:3"}
_HORIZONTAL = {"16:9", "4:3", "3:2"}


class GeminiImageError(RuntimeError):
    """Raised when the API returns no image (safety block, bad response, or all keys exhausted)."""


# Dedicated image pool — independent daily/cooldown tracking from the text pool.
_img_pool: Optional[GeminiKeyPool] = None


def get_image_pool() -> GeminiKeyPool:
    global _img_pool
    if _img_pool is None:
        _img_pool = GeminiKeyPool(GEMINI_API_KEYS)
    return _img_pool


def _aspect_hint(aspect_ratio: Optional[str]) -> str:
    if not aspect_ratio:
        return ""
    orient = "vertical" if aspect_ratio in _VERTICAL else "horizontal" if aspect_ratio in _HORIZONTAL else "square"
    return (f"\n\nCompose strictly as a {aspect_ratio} {orient} full-frame image — "
            "fill the whole frame, no letterboxing, no black bars, upright (not rotated).")


async def generate_image(
    prompt: str,
    output_path: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    model: str = IMAGE_MODEL,
    timeout: int = 120,
) -> Path:
    """Generate one image from `prompt`, save it, return the path.

    Nano Banana has no explicit aspect-ratio param, so the ratio is steered via the
    prompt. Key rotation + 429/daily handling come from the dedicated image pool.
    """
    full_prompt = prompt + _aspect_hint(aspect_ratio)
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    res = await call_gemini_async(payload, model=model, timeout=timeout, pool=get_image_pool())

    cands = res.get("candidates", [])
    if not cands:
        fb = res.get("promptFeedback", {})
        raise GeminiImageError(f"No candidates (blocked? {fb})")
    parts = cands[0].get("content", {}).get("parts", [])
    b64 = next(
        (p["inlineData"]["data"] for p in parts
         if p.get("inlineData") and p["inlineData"].get("data")),
        None,
    )
    if not b64:
        raise GeminiImageError(
            f"No image in response (finishReason={cands[0].get('finishReason')})"
        )
    data = base64.b64decode(b64)

    if output_path:
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        dest = OUTPUT_DIR / f"{uuid.uuid4().hex}.png"
    dest.write_bytes(data)
    logger.info("Gemini image saved: %s (%d KB)", dest, dest.stat().st_size // 1024)
    return dest
