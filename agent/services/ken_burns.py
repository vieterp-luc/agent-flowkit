"""Ken Burns FFmpeg helper: zoom/pan/parallax motion + text overlays on still images."""
import logging
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default font for text overlays — Arial Bold on macOS
_DEFAULT_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
_FALLBACK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FPS = 30


def _font_path() -> str:
    if Path(_DEFAULT_FONT).exists():
        return _DEFAULT_FONT
    if Path(_FALLBACK_FONT).exists():
        return _FALLBACK_FONT
    return ""  # Let ffmpeg use fontconfig


def _parse_resolution(resolution: str) -> tuple[int, int]:
    w, h = resolution.split("x")
    return int(w), int(h)


def _run_ffmpeg(cmd: list[str], timeout: int = 300) -> None:
    """Run ffmpeg command, raise RuntimeError on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr[-500:]}")


def _probe_duration(path: str) -> Optional[float]:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def _zoompan_filter(motion: str, width: int, height: int, frames: int) -> str:
    """Return zoompan vf filter string for the given motion preset."""
    W, H, N = width, height, frames

    if motion == "zoom_in":
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z='min(zoom+0.0015,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    elif motion == "zoom_out":
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z='if(lte(on,1),1.2,max(zoom-0.0015,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_left":
        # Pan left-to-right (x increases)
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z=1.2:x='iw*0.05+(iw*0.6)*on/{N}':y='ih*0.2'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_right":
        # Pan right-to-left (x decreases)
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z=1.2:x='iw*0.65-(iw*0.6)*on/{N}':y='ih*0.2'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_up":
        # Tilt up: y decreases (bottom to top)
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z=1.2:x='iw*0.2':y='ih*0.5-(ih*0.3)*on/{N}'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_down":
        # Tilt down: y increases (top to bottom)
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z=1.2:x='iw*0.2':y='ih*0.2+(ih*0.3)*on/{N}'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    elif motion == "parallax":
        # Parallax fallback: combined diagonal zoom+pan for layered feel
        return (
            f"scale={W*2}:{H*2},"
            f"zoompan=z='min(zoom+0.001,1.15)':x='iw*0.05+(iw*0.3)*on/{N}':y='ih*0.5-(ih*0.2)*on/{N}'"
            f":d={N}:s={W}x{H}:fps={FPS}"
        )
    else:  # static
        return f"scale={W}:{H},fps={FPS}"


def _text_overlay_filter(text: str, style: str, position: str,
                         width: int, height: int, duration: float) -> str:
    """Return drawtext filter string for the given text overlay style."""
    font = _font_path()
    font_clause = f"fontfile='{font}':" if font else ""

    # Sanitize text: escape single quotes and backslashes for ffmpeg filter
    safe_text = text.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")

    if style == "bold_caption":
        fs = min(height // 18, 72)
        y_expr = f"h*0.82" if position == "bottom" else (f"h*0.05" if position == "top" else "(h-text_h)/2")
        return (
            f"drawtext={font_clause}text='{safe_text}':fontsize={fs}:fontcolor=white"
            f":borderw=4:bordercolor=black:x=(w-text_w)/2:y={y_expr}"
            f":line_spacing=8"
        )
    elif style == "quote_centered":
        fs = min(height // 14, 88)
        fade_d = min(0.8, duration * 0.2)
        fade_frames = int(fade_d * FPS)
        total_frames = int(duration * FPS)
        alpha_expr = (
            f"if(lt(n,{fade_frames}),n/{fade_frames},"
            f"if(gt(n,{total_frames - fade_frames}),({total_frames}-n)/{fade_frames},1))"
        )
        return (
            f"drawtext={font_clause}text='{safe_text}':fontsize={fs}:fontcolor=white"
            f":borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2"
            f":alpha='{alpha_expr}'"
        )
    else:  # subtitle
        fs = min(height // 24, 48)
        y_expr = f"h*0.88" if position == "bottom" else (f"h*0.05" if position == "top" else "(h-text_h)/2")
        return (
            f"drawtext={font_clause}text='{safe_text}':fontsize={fs}:fontcolor=white"
            f":borderw=2:bordercolor=black:x=(w-text_w)/2:y={y_expr}"
        )


def build_clip(
    image_path: str,
    duration_seconds: float,
    motion: str,
    resolution: str,
    output_path: str,
    text_overlay: Optional[dict] = None,
) -> str:
    """Render a Ken Burns clip from a still image. Returns output_path."""
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    width, height = _parse_resolution(resolution)
    frames = int(duration_seconds * FPS)

    vf_parts = [_zoompan_filter(motion, width, height, frames)]

    if text_overlay:
        overlay_filter = _text_overlay_filter(
            text=text_overlay["text"],
            style=text_overlay.get("style", "bold_caption"),
            position=text_overlay.get("position", "bottom"),
            width=width,
            height=height,
            duration=duration_seconds,
        )
        vf_parts.append(overlay_filter)

    vf = ",".join(vf_parts)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-t", str(duration_seconds),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-movflags", "+faststart",
        "-an",
        output_path,
    ]
    logger.info("Building clip: motion=%s res=%s dur=%.1fs", motion, resolution, duration_seconds)
    _run_ffmpeg(cmd, timeout=300)
    return output_path


def concat_clips(
    clips: list[dict],
    output_path: str,
    xfade_duration: float = 0.5,
    audio_track: Optional[dict] = None,
) -> str:
    """Concat clip list with xfade transitions. Returns output_path."""
    if not clips:
        raise ValueError("clips list is empty")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Validate all clip files exist
    for c in clips:
        if not Path(c["path"]).exists():
            raise FileNotFoundError(f"Clip not found: {c['path']}")

    n = len(clips)

    if n == 1:
        # Single clip: just copy or mux audio
        if audio_track:
            _mux_audio(clips[0]["path"], audio_track, output_path)
        else:
            import shutil
            shutil.copy2(clips[0]["path"], output_path)
        return output_path

    # Build xfade filter_complex for n clips
    # Input labels: [0:v], [1:v], ...
    # Chain: [0:v][1:v]xfade=...[v01]; [v01][2:v]xfade=...[v012]; ...
    filter_parts = []
    prev_label = "[0:v]"
    total_dur = 0.0

    for i in range(n - 1):
        clip_dur = clips[i]["duration"]
        offset = total_dur + clip_dur - xfade_duration
        total_dur = offset
        out_label = f"[v{i}{i+1}]"
        filter_parts.append(
            f"{prev_label}[{i+1}:v]xfade=transition=fade:duration={xfade_duration}"
            f":offset={offset:.3f}{out_label}"
        )
        prev_label = out_label

    # Final total duration
    final_dur = total_dur + clips[-1]["duration"]

    filter_complex = ";".join(filter_parts)
    final_video_label = prev_label  # last output label

    inputs = []
    for c in clips:
        inputs += ["-i", c["path"]]

    if audio_track and Path(audio_track["path"]).exists():
        vol = audio_track.get("volume", 0.25)
        audio_inputs = ["-i", audio_track["path"]]
        audio_idx = n
        audio_filter = (
            f";[{audio_idx}:a]volume={vol},afade=t=in:st=0:d=1.0,"
            f"afade=t=out:st={max(0, final_dur - 2.0):.3f}:d=2.0[aout]"
        )
        filter_complex += audio_filter
        cmd = [
            "ffmpeg", "-y",
            *inputs, *audio_inputs,
            "-filter_complex", filter_complex,
            "-map", final_video_label, "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-r", str(FPS),
            "-movflags", "+faststart",
            output_path,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", final_video_label,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-r", str(FPS),
            "-movflags", "+faststart",
            "-an",
            output_path,
        ]

    logger.info("Concatenating %d clips with xfade=%.2fs", n, xfade_duration)
    _run_ffmpeg(cmd, timeout=600)
    return output_path


def _mux_audio(video_path: str, audio_track: dict, output_path: str) -> None:
    """Mux single video with audio track."""
    vol = audio_track.get("volume", 0.25)
    dur_probe = _probe_duration(video_path) or 5.0
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path, "-i", audio_track["path"],
        "-filter_complex",
        f"[1:a]volume={vol},afade=t=in:st=0:d=1.0,"
        f"afade=t=out:st={max(0, dur_probe - 2.0):.3f}:d=2.0[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        output_path,
    ]
    _run_ffmpeg(cmd, timeout=120)
