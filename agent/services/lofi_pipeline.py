"""Long-form lo-fi video generator — combines Gemini Lyria music + ambience + ken-burns visual.

Pipeline:
  1. Load preset from assets/lofi-presets.json
  2. Generate 8 unique music tracks via Gemini Lyria Pro (sequential due to browser lock)
  3. Concat → ~24min unique block
  4. Loop block to target duration with per-iteration pitch shift (disguises repetition)
  5. Mix with ambience .wav layer (music 70-75%, ambience 25-30%)
  6. Generate 1 cinematic image via Flow API
  7. Convert image → ken-burns slow zoom video at target duration
  8. Combine A+V into final mp4
  9. Build YouTube metadata JSON
"""
import asyncio
import json
import logging
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PRESETS_PATH = Path("assets/lofi-presets.json")
AMBIENCE_DIR = Path("assets/ambience")
GEMINI_MUSIC_DIR = Path("output/_shared/gemini_music")
LOFI_OUT_ROOT = Path("output/lofi")

MUSIC_TRACK_COUNT = 8  # Gen 8 unique tracks → ~24min unique block. Pitch-shift on each loop disguises repetition further.
KENBURNS_FPS = 30
KENBURNS_RES = "1920x1080"


class LofiPipelineError(RuntimeError):
    pass


# ─── Preset loading ─────────────────────────────────────────


def load_preset(preset_id: str) -> dict:
    if not PRESETS_PATH.exists():
        raise LofiPipelineError(f"Preset file not found: {PRESETS_PATH}")
    presets = json.loads(PRESETS_PATH.read_text())
    if preset_id not in presets:
        raise LofiPipelineError(
            f"Unknown preset '{preset_id}'. Valid: {list(presets.keys())}"
        )
    return presets[preset_id]


def list_presets() -> list[dict]:
    if not PRESETS_PATH.exists():
        return []
    presets = json.loads(PRESETS_PATH.read_text())
    return [{"id": k, "title": v.get("title", k)} for k, v in presets.items()]


# ─── Audio sub-pipeline ─────────────────────────────────────


# Variation suffixes added to prompts to (a) avoid Gemini duplicate-suppression and
# (b) yield N musically-distinct tracks for less obvious looping
_PROMPT_VARIATIONS = (
    "",
    ", with a slightly more melancholic feel",
    ", with a brighter and more uplifting energy",
    ", with more space, reverb and ambient texture",
    ", with intimate close-mic feel and softer dynamics",
    ", with warmer brass and woodwind colors",
    ", with crystalline piano lead and sparser arrangement",
    ", with a subtle outdoor wind ambience layer",
)


MIN_TRACKS_REQUIRED = 4  # Allow partial success — need at least 4 tracks for usable variation
INTER_REQUEST_DELAY_S = 5  # Pause between gens to avoid rate-limit bursts


# Pitch-shift sequence applied per loop iteration to disguise loop boundaries.
# Values in cents (100¢ = 1 semitone). Cycles per loop iteration; 0¢ = original.
_LOOP_PITCH_CENTS = (0, 30, -20, 50, -50, 20, -30, 40)


async def _generate_music_tracks(
    music_prompt: str, count: int, output_dir: Path
) -> list[Path]:
    """Generate `count` unique tracks via Gemini Lyria Pro. Each track has 1 retry on timeout.
    Returns successful tracks (may be < count); raises if fewer than MIN_TRACKS_REQUIRED.
    """
    from agent.services.gemini_browser import init_browser, GeminiBrowserError

    output_dir.mkdir(parents=True, exist_ok=True)
    browser = await init_browser(headless=True)
    tracks: list[Path] = []
    for i in range(count):
        suffix = _PROMPT_VARIATIONS[i % len(_PROMPT_VARIATIONS)]
        prompt_i = f"{music_prompt}{suffix}"
        if i > 0:
            await asyncio.sleep(INTER_REQUEST_DELAY_S)

        track_path = await _gen_one_track_with_retry(
            browser, prompt_i, i + 1, count, output_dir
        )
        if track_path:
            tracks.append(track_path)

    if len(tracks) < MIN_TRACKS_REQUIRED:
        raise LofiPipelineError(
            f"only {len(tracks)}/{count} music tracks succeeded — need at least {MIN_TRACKS_REQUIRED}"
        )
    if len(tracks) < count:
        logger.warning("lofi: partial music success — %d/%d (proceeding)", len(tracks), count)
    return tracks


async def _gen_one_track_with_retry(browser, prompt: str, idx: int, total: int, output_dir: Path) -> Optional[Path]:
    """Try to gen 1 track; on timeout retry once after 30s. Returns saved Path or None."""
    from agent.services.gemini_browser import GeminiBrowserError

    for attempt in (1, 2):
        suffix_label = "retry" if attempt == 2 else "first"
        logger.info("lofi: gen music %d/%d (%s)", idx, total, suffix_label)
        try:
            src_path = await browser.generate_music(prompt, timeout_s=300, model="Pro")
            dst = output_dir / f"track_{idx:02d}.mp4"
            shutil.move(str(src_path), str(dst))
            return dst
        except GeminiBrowserError as e:
            if "TIMEOUT" in str(e) and attempt == 1:
                logger.warning("lofi: track %d timeout — retry in 30s", idx)
                await asyncio.sleep(30)
                continue
            logger.error("lofi: track %d failed permanently: %s", idx, e)
            return None
    return None


def _concat_music(tracks: list[Path], output: Path) -> Path:
    """Concat N mp4 tracks into a single mp3 block."""
    list_file = output.parent / "_concat_list.txt"
    list_file.write_text("\n".join(f"file '{t.absolute()}'" for t in tracks))
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-vn", "-c:a", "libmp3lame", "-b:a", "192k",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    list_file.unlink(missing_ok=True)
    return output


def _ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ]).decode().strip()
    return float(out)


def _probe_sample_rate(path: Path) -> int:
    out = subprocess.check_output([
        "ffprobe", "-v", "quiet", "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate", "-of", "csv=p=0", str(path),
    ]).decode().strip()
    return int(out)


def _pitch_shift_block(input_path: Path, cents: int, output: Path) -> Path:
    """Pitch-shift audio by `cents` (±) without changing tempo.

    `asetrate` reinterprets the stream's sample rate (changing pitch+tempo together) and
    must be parameterised by the source SR. `aresample` then restores it, and `atempo`
    compensates the speed change so duration stays constant. Net effect: pitch only.
    """
    ratio = 2 ** (cents / 1200.0)
    src_sr = _probe_sample_rate(input_path)
    asetrate = int(src_sr * ratio)
    atempo = 1.0 / ratio
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(input_path),
        "-af", f"asetrate={asetrate},aresample={src_sr},atempo={atempo:.6f}",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def _loop_audio(input_path: Path, target_sec: int, output: Path) -> Path:
    """Loop input audio to target_sec, applying a rotating pitch shift per iteration.

    Each loop iteration uses a different pitch offset from `_LOOP_PITCH_CENTS` so that
    listeners perceive variation instead of identical repetition. The first iteration is
    always 0¢ (untouched). Final result is trimmed to exact target_sec.
    """
    block_dur = _ffprobe_duration(input_path)
    if block_dur >= target_sec:
        # Block already long enough — just trim.
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(input_path), "-t", str(target_sec),
            "-c:a", "libmp3lame", "-b:a", "192k", str(output),
        ]
        subprocess.run(cmd, check=True)
        return output

    import math
    n_loops = math.ceil(target_sec / block_dur)
    tmp_dir = output.parent / "_loop_segments"
    tmp_dir.mkdir(exist_ok=True)
    segments: list[Path] = []
    for i in range(n_loops):
        cents = _LOOP_PITCH_CENTS[i % len(_LOOP_PITCH_CENTS)]
        if cents == 0:
            seg = input_path  # reuse original block, no re-encode needed
        else:
            seg = tmp_dir / f"seg_{i:02d}_{cents:+d}c.mp3"
            _pitch_shift_block(input_path, cents, seg)
        segments.append(seg)

    list_file = tmp_dir / "_loop_list.txt"
    list_file.write_text("\n".join(f"file '{s.absolute()}'" for s in segments))
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-t", str(target_sec),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    # Cleanup intermediates (keep concat list for debugging? no, remove)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return output


def _mix_with_ambience(
    music: Path,
    ambience_files: list[Path],
    output: Path,
    music_vol: float = 0.75,
    amb_vol: float = 0.25,
) -> Path:
    """Mix music + N ambience layers (looped) into final audio track."""
    if not ambience_files:
        # No ambience → just copy music with volume adjusted
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(music),
            "-filter:a", f"volume={music_vol}",
            "-c:a", "libmp3lame", "-b:a", "192k", str(output),
        ]
        subprocess.run(cmd, check=True)
        return output

    inputs: list[str] = ["-i", str(music)]
    for amb in ambience_files:
        inputs += ["-stream_loop", "-1", "-i", str(amb)]

    n_amb = len(ambience_files)
    parts = [f"[0:a]volume={music_vol}[m]"]
    per_amb = amb_vol / max(n_amb, 1)
    for i in range(n_amb):
        parts.append(f"[{i+1}:a]volume={per_amb}[a{i}]")
    mix_inputs = "[m]" + "".join(f"[a{i}]" for i in range(n_amb))
    parts.append(f"{mix_inputs}amix=inputs={n_amb+1}:duration=first:dropout_transition=0[out]")

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        *inputs,
        "-filter_complex", ";".join(parts),
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def _resolve_ambience_files(names: list[str]) -> list[Path]:
    files: list[Path] = []
    for name in names:
        candidate = AMBIENCE_DIR / f"{name}.wav"
        if candidate.exists():
            files.append(candidate)
        else:
            logger.warning("lofi: ambience %s missing — skipping", candidate)
    return files


# ─── Visual sub-pipeline ────────────────────────────────────


async def _generate_image(prompt: str, project_id: str, output: Path) -> Path:
    """Generate cinematic image via Flow API. Reuses existing thumbnail endpoint logic."""
    from agent.services.flow_client import get_flow_client
    from agent.sdk.services.result_handler import parse_result
    import aiohttp

    client = get_flow_client()
    if not client.connected:
        raise LofiPipelineError("flow_extension_not_connected")

    raw = await client.generate_images(
        prompt=prompt,
        project_id=project_id,
        aspect_ratio="IMAGE_ASPECT_RATIO_LANDSCAPE",
        user_paygate_tier="PAYGATE_TIER_TWO",
        character_media_ids=None,
    )
    result = parse_result(raw, "GENERATE_IMAGE")
    if not result.success or not result.url:
        raise LofiPipelineError(f"image_gen_failed: {result.error or 'no url'}")

    output.parent.mkdir(parents=True, exist_ok=True)
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(result.url) as r:
            r.raise_for_status()
            output.write_bytes(await r.read())
    return output


def _image_to_kenburns(image: Path, target_sec: int, output: Path) -> Path:
    """Render image as ken-burns slow zoom video (1080p, 30fps)."""
    fps = KENBURNS_FPS
    total_frames = target_sec * fps
    # Slow zoom 1.0 → 1.10 over duration; 30s = 900 frames; 0.0001 per frame ≈ 1.09 over 900 frames
    zoom_step = max(0.10 / total_frames, 0.00005)
    vf = (
        f"scale=2400:-1,"
        f"zoompan=z='min(zoom+{zoom_step:.6f},1.10)':"
        f"d={total_frames}:s={KENBURNS_RES}:fps={fps}"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-i", str(image),
        "-vf", vf,
        "-t", str(target_sec),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "fast", "-crf", "23",
        "-fps_mode", "cfr", "-r", str(fps),
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def _combine_av(video: Path, audio: Path, output: Path) -> Path:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video), "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


# ─── YouTube metadata ───────────────────────────────────────


def _build_youtube_meta(preset: dict, duration_min: int) -> dict:
    title = preset["title"]
    if duration_min >= 60:
        title += f" — {duration_min // 60}h"
    else:
        title += f" — {duration_min}min"

    desc = (
        f"{preset.get('description', '')}\n\n"
        f"⏱ Duration: {duration_min} minutes\n"
        f"🎨 Palette: {preset.get('color_palette', '')}\n\n"
        f"Made with care 🌿\n"
        f"#lofi #slowliving #studymusic"
    )
    return {
        "title": title,
        "description": desc,
        "tags": preset.get("youtube_tags", []),
        "category_id": "10",  # Music
        "privacy": "private",
    }


# ─── Orchestrator ───────────────────────────────────────────


async def generate_lofi_video(
    preset_id: str,
    duration_min: int = 60,
    visual_mode: str = "static",
    project_id_for_image: Optional[str] = None,
) -> dict:
    """Full pipeline: preset → music + ambience + visual → final mp4 + metadata.

    Returns dict with paths and timing breakdown.
    """
    if visual_mode != "static":
        raise LofiPipelineError(
            f"visual_mode '{visual_mode}' not yet supported (Phase 2 only ships static)"
        )

    preset = load_preset(preset_id)
    target_sec = duration_min * 60
    timestamp = int(time.time())
    out_dir = LOFI_OUT_ROOT / f"{preset_id}_{duration_min}min_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    music_dir = out_dir / "music"

    breakdown: dict = {}

    # 1. Music tracks (4 × ~90s wall each)
    t0 = time.time()
    tracks = await _generate_music_tracks(
        preset["music_prompt"], MUSIC_TRACK_COUNT, music_dir
    )
    breakdown["music_gen_sec"] = round(time.time() - t0, 1)

    # 2. Concat → 3. Loop → 4. Mix
    t0 = time.time()
    concat_block = _concat_music(tracks, out_dir / "concat_music.mp3")
    looped = _loop_audio(concat_block, target_sec, out_dir / "looped_music.mp3")
    ambience_paths = _resolve_ambience_files(preset.get("ambience", []))
    mixed = _mix_with_ambience(
        looped,
        ambience_paths,
        out_dir / "mixed_audio.mp3",
        music_vol=preset.get("music_volume", 0.75),
        amb_vol=preset.get("ambience_volume", 0.25),
    )
    breakdown["audio_post_sec"] = round(time.time() - t0, 1)

    # 5. Image gen
    t0 = time.time()
    image_path = out_dir / "visual.png"
    image_pid = project_id_for_image or "lofi-shared"
    await _generate_image(preset["image_prompt"], image_pid, image_path)
    breakdown["image_gen_sec"] = round(time.time() - t0, 1)

    # 6. Ken-burns
    t0 = time.time()
    kenburns = _image_to_kenburns(image_path, target_sec, out_dir / "ken_burns.mp4")
    breakdown["kenburns_sec"] = round(time.time() - t0, 1)

    # 7. Combine A+V
    t0 = time.time()
    final = _combine_av(kenburns, mixed, out_dir / "final.mp4")
    breakdown["combine_sec"] = round(time.time() - t0, 1)

    # 8. YouTube metadata
    yt_meta = _build_youtube_meta(preset, duration_min)
    meta_path = out_dir / "youtube_meta.json"
    meta_path.write_text(json.dumps(yt_meta, indent=2, ensure_ascii=False))

    breakdown["total_sec"] = round(sum(v for v in breakdown.values() if isinstance(v, (int, float))), 1)
    logger.info("lofi: complete — %s (%s)", final, breakdown)

    return {
        "ok": True,
        "preset": preset_id,
        "duration_min": duration_min,
        "final_video_path": str(final),
        "metadata_path": str(meta_path),
        "image_path": str(image_path),
        "breakdown": breakdown,
    }
