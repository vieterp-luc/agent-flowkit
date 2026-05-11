# Register in main.py: from agent.api.ken_burns import router as ken_burns_router; app.include_router(ken_burns_router, prefix="/api")
"""FastAPI router for Ken Burns FFmpeg clip generation endpoints."""
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from agent.models.ken_burns import (
    ClipRequest, ClipResponse,
    ConcatRequest, ConcatResponse,
)
from agent.services.ken_burns import build_clip, concat_clips, _probe_duration

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ken-burns"])

_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def _validate_image(path: str) -> None:
    p = Path(path)
    if not p.exists():
        raise HTTPException(400, f"Image not found: {path}")
    if p.suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported image format: {p.suffix}")


def _validate_output(path: str) -> None:
    if not path.endswith(".mp4"):
        raise HTTPException(400, "output_path must end with .mp4")


@router.post("/ken-burns/clip", response_model=ClipResponse)
async def create_ken_burns_clip(body: ClipRequest):
    """Render a Ken Burns motion clip from a still image."""
    _validate_image(body.image_path)
    _validate_output(body.output_path)

    overlay = None
    if body.text_overlay:
        overlay = {
            "text": body.text_overlay.text,
            "style": body.text_overlay.style,
            "position": body.text_overlay.position,
        }

    try:
        out = build_clip(
            image_path=body.image_path,
            duration_seconds=body.duration_seconds,
            motion=body.motion,
            resolution=body.resolution,
            output_path=body.output_path,
            text_overlay=overlay,
        )
    except FileNotFoundError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        logger.exception("Ken Burns clip failed")
        raise HTTPException(500, str(e))

    duration = _probe_duration(out)
    return ClipResponse(ok=True, output_path=out, duration=duration, resolution=body.resolution)


@router.post("/ken-burns/concat", response_model=ConcatResponse)
async def concat_ken_burns_clips(body: ConcatRequest):
    """Concatenate Ken Burns clips with xfade transitions and optional audio."""
    _validate_output(body.output_path)

    for item in body.clips:
        if not Path(item.path).exists():
            raise HTTPException(400, f"Clip not found: {item.path}")

    audio = None
    if body.audio_track:
        if not Path(body.audio_track.path).exists():
            raise HTTPException(400, f"Audio track not found: {body.audio_track.path}")
        audio = {"path": body.audio_track.path, "volume": body.audio_track.volume}

    clips = [{"path": c.path, "duration": c.duration} for c in body.clips]

    try:
        out = concat_clips(
            clips=clips,
            output_path=body.output_path,
            xfade_duration=body.xfade_duration,
            audio_track=audio,
        )
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        logger.exception("Ken Burns concat failed")
        raise HTTPException(500, str(e))

    total_duration = _probe_duration(out)
    return ConcatResponse(ok=True, output_path=out, total_duration=total_duration)
