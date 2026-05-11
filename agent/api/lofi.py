"""FastAPI router for /fk-video-lofi pipeline."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["lofi"])


class LofiGenerateRequest(BaseModel):
    preset: str
    duration_min: int = 60
    visual_mode: str = "static"  # static | slideshow | veo (Phase 2 only ships static)
    project_id_for_image: Optional[str] = None


@router.get("/lofi/presets")
async def list_lofi_presets():
    from agent.services.lofi_pipeline import list_presets
    return {"presets": list_presets()}


@router.get("/lofi/presets/{preset_id}")
async def get_lofi_preset(preset_id: str):
    from agent.services.lofi_pipeline import load_preset, LofiPipelineError
    try:
        return load_preset(preset_id)
    except LofiPipelineError as e:
        raise HTTPException(404, str(e))


@router.post("/lofi/generate")
async def generate_lofi(body: LofiGenerateRequest):
    from agent.services.lofi_pipeline import generate_lofi_video, LofiPipelineError
    if body.duration_min < 1 or body.duration_min > 480:
        raise HTTPException(400, "duration_min must be between 1 and 480")
    try:
        return await generate_lofi_video(
            preset_id=body.preset,
            duration_min=body.duration_min,
            visual_mode=body.visual_mode,
            project_id_for_image=body.project_id_for_image,
        )
    except LofiPipelineError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        logger.exception("lofi generate failed")
        return {"ok": False, "error": f"UNEXPECTED: {e}"}
