"""FastAPI router for Reup Video feature."""
import json, uuid, logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pathlib import Path

from agent.models.reup import ReupJobRequest, ReupJobStatus
from agent.services.reup import JOBS, run_reup_job
from agent.config import BASE_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["reup"])

TEMPLATES_META = Path(BASE_DIR) / "output" / "_shared" / "tts_templates" / "templates.json"


def _load_templates():
    if TEMPLATES_META.exists():
        return json.loads(TEMPLATES_META.read_text(encoding="utf-8"))
    return {}


@router.post("/reup/jobs", response_model=ReupJobStatus)
async def start_reup_job(body: ReupJobRequest, background_tasks: BackgroundTasks):
    if not Path(body.video_path).exists():
        raise HTTPException(400, f"Video not found: {body.video_path}")

    meta = _load_templates()
    if body.tts_template not in meta:
        raise HTTPException(404, f"TTS template '{body.tts_template}' not found")
    tmpl = meta[body.tts_template]
    ref_audio = tmpl["audio_path"]
    ref_text = tmpl.get("text", "")

    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {
        "job_id": job_id, "status": "pending", "step": None,
        "progress": 0, "scenes_total": 0, "scenes_done": 0,
        "output_path": None, "error": None,
    }

    background_tasks.add_task(
        run_reup_job, job_id, body.video_path, body.tts_template,
        body.speed, body.language, body.min_scene_duration, ref_audio, ref_text,
        body.sfx_volume
    )

    return ReupJobStatus(**JOBS[job_id])


@router.get("/reup/jobs/{job_id}", response_model=ReupJobStatus)
async def get_reup_job(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, "Job not found")
    return ReupJobStatus(**JOBS[job_id])
