"""Pydantic models for Ken Burns FFmpeg endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, Literal


MotionPreset = Literal[
    "zoom_in", "zoom_out",
    "pan_left", "pan_right",
    "pan_up", "pan_down",
    "parallax", "static",
]

ResolutionPreset = Literal["1920x1080", "1080x1920", "1080x1080"]

TextStyle = Literal["bold_caption", "quote_centered", "subtitle"]

TextPosition = Literal["center", "bottom", "top"]


class TextOverlayRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    style: TextStyle = "bold_caption"
    position: TextPosition = "bottom"


class ClipRequest(BaseModel):
    image_path: str = Field(..., max_length=1000)
    duration_seconds: float = Field(5.0, ge=1.0, le=60.0)
    motion: MotionPreset = "zoom_in"
    resolution: ResolutionPreset = "1920x1080"
    output_path: str = Field(..., max_length=1000)
    text_overlay: Optional[TextOverlayRequest] = None


class ClipResponse(BaseModel):
    ok: bool
    output_path: str
    duration: Optional[float] = None
    resolution: str


class ConcatClipItem(BaseModel):
    path: str = Field(..., max_length=1000)
    duration: float = Field(..., ge=0.1)


class AudioTrack(BaseModel):
    path: str = Field(..., max_length=1000)
    volume: float = Field(0.25, ge=0.0, le=2.0)


class ConcatRequest(BaseModel):
    clips: list[ConcatClipItem] = Field(..., min_length=1)
    xfade_duration: float = Field(0.5, ge=0.0, le=2.0)
    output_path: str = Field(..., max_length=1000)
    audio_track: Optional[AudioTrack] = None


class ConcatResponse(BaseModel):
    ok: bool
    output_path: str
    total_duration: Optional[float] = None
