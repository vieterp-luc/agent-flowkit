"""Reup video service: scene detection → narrator text → TTS → mix → concat."""
import asyncio, json, os, subprocess, tempfile, uuid, base64, shutil
from pathlib import Path
from typing import Optional

from agent.config import BASE_DIR
from agent.services.tts import generate_speech

JOBS: dict[str, dict] = {}  # in-memory job store


def _update_job(job_id, **kwargs):
    JOBS[job_id].update(kwargs)


def _ffprobe_duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0


def _detect_scenes(video_path: str, min_dur: float, total_dur: float) -> list[tuple[int, float, float]]:
    """Detect scene boundaries using ffmpeg, merge short scenes."""
    r = subprocess.run(
        ["ffmpeg", "-i", video_path, "-filter:v", "select='gt(scene,0.4)',showinfo",
         "-f", "null", "-"],
        capture_output=True, text=True, timeout=120
    )
    cuts = []
    for line in r.stderr.splitlines():
        if "showinfo" in line and "pts_time:" in line:
            for part in line.split():
                if part.startswith("pts_time:"):
                    try:
                        cuts.append(float(part.split(":")[1]))
                    except ValueError:
                        pass

    boundaries = [0.0] + cuts + [total_dur]
    merged = [boundaries[0]]
    for t in boundaries[1:]:
        if t - merged[-1] >= min_dur:
            merged.append(t)
    if merged[-1] < total_dur:
        merged.append(total_dur)

    scenes = []
    for i in range(len(merged) - 1):
        s, e = merged[i], merged[i + 1]
        if e - s >= 1.0:
            scenes.append((len(scenes), round(s, 2), round(e, 2)))
    return scenes


def _extract_frame(video_path: str, timestamp: float) -> Optional[str]:
    """Extract frame as base64 JPEG."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        tmp = f.name
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
             "-frames:v", "1", "-q:v", "3", tmp],
            capture_output=True, timeout=30
        )
        with open(tmp, "rb") as f:
            return base64.standard_b64encode(f.read()).decode()
    except Exception:
        return None
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def _generate_narrator_texts(scenes: list[tuple], video_path: str, language: str) -> list[str]:
    """Call Claude CLI to generate narrator text for each scene using frame screenshots."""
    lang_map = {"vi": "Vietnamese", "en": "English", "zh": "Chinese", "ja": "Japanese", "ko": "Korean"}
    lang_name = lang_map.get(language, "Vietnamese")
    max_words = {"vi": 20, "en": 20, "zh": 26, "ja": 30, "ko": 20}.get(language, 20)

    content = []
    for idx, start, end in scenes:
        mid = round(start + (end - start) / 2, 2)
        b64 = _extract_frame(video_path, mid)
        if b64:
            content.append({
                "type": "text",
                "text": f"Scene {idx:02d} (start={start:.1f}s, end={end:.1f}s, duration={end - start:.1f}s):"
            })
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}
            })

    content.append({
        "type": "text",
        "text": f"""Generate narrator voiceover text in {lang_name} for each scene shown above.

Rules:
- MAX {max_words} words per scene (HARD limit — TTS must fit within scene duration)
- Documentary narrator style: informative, engaging, adds context viewer can't see
- Do NOT describe what's obviously visible — add facts, context, emotion
- Short punchy sentences
- Output ONLY a JSON array of strings, one per scene, in order
- Example: ["Scene 00 text here.", "Scene 01 text here.", ...]
- No markdown, no explanation, just the JSON array"""
    })

    stream_msg = json.dumps({
        "type": "user",
        "message": {"role": "user", "content": content}
    })

    claude_bin = shutil.which("claude") or "claude"
    r = subprocess.run(
        [claude_bin, "-p", "--input-format", "stream-json", "--output-format", "stream-json",
         "--verbose", "--model", "claude-haiku-4-5-20251001"],
        input=stream_msg, capture_output=True, text=True, timeout=120
    )
    raw = ""
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get("type") == "assistant":
                for block in obj.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        raw += block["text"]
        except (json.JSONDecodeError, KeyError):
            pass

    start_idx = raw.find("[")
    end_idx = raw.rfind("]") + 1
    if start_idx >= 0 and end_idx > start_idx:
        try:
            return json.loads(raw[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
    return [f"Scene {i}." for i in range(len(scenes))]


def _mix_scene(video_path: str, tts_path: str, start: float, end: float,
               out_path: str, w: int, h: int, sfx_volume: float = 0.10) -> bool:
    """Trim scene + mix TTS audio."""
    tts_dur = _ffprobe_duration(tts_path)
    scene_dur = end - start
    cut_dur = round(min(tts_dur + 0.5, scene_dur), 2)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-i", video_path,
        "-i", tts_path,
        "-t", str(cut_dur),
        "-filter_complex", f"[0:a]volume={sfx_volume}[bg];[1:a]volume=1.5[fg];[bg][fg]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
        "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", out_path
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    return r.returncode == 0


async def run_reup_job(job_id: str, video_path: str, tts_template: str,
                       speed: float, language: str, min_scene_duration: float,
                       ref_audio: str, ref_text: str, sfx_volume: float = 0.10):
    """Full reup pipeline — runs in background."""
    import logging
    logger = logging.getLogger(__name__)

    try:
        _update_job(job_id, status="processing", step="detecting_scenes", progress=5)

        if not Path(video_path).exists():
            _update_job(job_id, status="failed", error=f"Video not found: {video_path}")
            return

        total_dur = _ffprobe_duration(video_path)
        if total_dur <= 0:
            _update_job(job_id, status="failed", error="Cannot read video duration")
            return

        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path],
            capture_output=True, text=True
        )
        dims = r.stdout.strip().split(",")
        W, H = (int(dims[0]), int(dims[1])) if len(dims) == 2 else (720, 1280)

        scenes = _detect_scenes(video_path, min_scene_duration, total_dur)
        _update_job(job_id, scenes_total=len(scenes), step="generating_narrator", progress=15)

        narrator_texts = _generate_narrator_texts(scenes, video_path, language)
        _update_job(job_id, step="generating_tts", progress=35)

        out_dir = Path(BASE_DIR) / "output" / "_reup" / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        clips_dir = out_dir / "clips"
        clips_dir.mkdir(exist_ok=True)
        tts_dir = out_dir / "tts"
        tts_dir.mkdir(exist_ok=True)

        clip_paths = []
        for i, (idx, start, end) in enumerate(scenes):
            text = narrator_texts[idx] if idx < len(narrator_texts) else ""
            tts_path = str(tts_dir / f"scene_{idx:02d}.wav")

            if text:
                await generate_speech(
                    text=text, output_path=tts_path,
                    ref_audio=ref_audio, ref_text=ref_text, speed=speed
                )

            clip_path = str(clips_dir / f"scene_{idx:02d}.mp4")
            if text and Path(tts_path).exists():
                _mix_scene(video_path, tts_path, start, end, clip_path, W, H, sfx_volume)
            else:
                subprocess.run([
                    "ffmpeg", "-y", "-ss", str(start), "-i", video_path,
                    "-t", str(end - start),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-movflags", "+faststart", clip_path
                ], capture_output=True, timeout=60)

            clip_paths.append(clip_path)
            done = i + 1
            progress = 35 + int((done / len(scenes)) * 50)
            _update_job(job_id, scenes_done=done, progress=progress, step="generating_tts")

        _update_job(job_id, step="concat", progress=88)
        concat_txt = str(out_dir / "concat.txt")
        with open(concat_txt, "w") as f:
            for p in clip_paths:
                f.write(f"file '{p}'\n")

        out_video = str(out_dir / "output.mp4")
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
             "-c", "copy", "-movflags", "+faststart", out_video],
            capture_output=True, timeout=120
        )
        if r.returncode != 0:
            _update_job(job_id, status="failed", error="Concat failed")
            return

        _update_job(job_id, status="completed", progress=100, step="done", output_path=out_video)

    except Exception as e:
        logger.exception("Reup job failed")
        _update_job(job_id, status="failed", error=str(e))
