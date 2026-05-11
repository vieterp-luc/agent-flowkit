from pydantic import BaseModel, Field
from typing import Optional, Literal


class ReupJobRequest(BaseModel):
    video_path: str = Field(..., max_length=1000)
    tts_template: str = Field(..., max_length=64)
    speed: float = Field(1.0, ge=0.5, le=2.0)
    language: str = Field("vi", max_length=10)
    min_scene_duration: float = Field(5.0, ge=2.0, le=30.0)
    sfx_volume: float = Field(0.10, ge=0.0, le=1.0)


class ReupJobStatus(BaseModel):
    job_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    step: Optional[str] = None
    progress: int = 0
    scenes_total: int = 0
    scenes_done: int = 0
    output_path: Optional[str] = None
    error: Optional[str] = None
