"""Pipeline functions for rendering book podcast episodes.

Reusable library: each function is idempotent (returns existing artifact if found).
Used by scripts/render-podcast-episode.py.
"""
import json
import logging
import re
import subprocess
import time
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

API_BASE = "http://127.0.0.1:8100"


def _gemini_call_with_retry(url: str, payload: dict, max_attempts: int = 5,
                             base_delay: float = 5.0) -> dict:
    """Call Gemini REST with exponential backoff for 429/502/503."""
    last_err = None
    for attempt in range(max_attempts):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                          headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=120)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < max_attempts - 1:
                wait = base_delay * (2 ** attempt)
                logger.warning("Gemini %d, retry %d/%d after %.0fs", e.code, attempt + 1, max_attempts, wait)
                time.sleep(wait)
                last_err = e
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < max_attempts - 1:
                time.sleep(base_delay)
                continue
            raise
    raise last_err  # type: ignore


def _api_post_with_retry(path: str, payload: dict, timeout: int = 120,
                          max_attempts: int = 5, base_delay: float = 5.0) -> dict:
    """POST to FlowKit API with backoff for 429/502/503/504 errors."""
    last_err = None
    for attempt in range(max_attempts):
        try:
            r = requests.post(f"{API_BASE}{path}", json=payload, timeout=timeout)
            if r.status_code in (429, 502, 503, 504) and attempt < max_attempts - 1:
                wait = base_delay * (2 ** attempt)
                logger.warning("API %d on %s, retry %d/%d after %.0fs",
                               r.status_code, path, attempt + 1, max_attempts, wait)
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            last_err = e
            if attempt < max_attempts - 1:
                time.sleep(base_delay)
                continue
            raise
    raise last_err  # type: ignore
TTS_TEMPLATES = {
    # Use template name (not ref_audio path) — TTS API resolves audio + ref_text from registry
    "phap_van": "Phap_Van_podcast_TTS",
    "hong_hanh": "Hong_Hanh_podcast_TTS",
    "podcast_male": "podcast_male_TTS",
}


def slugify_vi(text: str) -> str:
    """Vietnamese-aware slug: ascii fold + kebab-case."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s-]", "", text).lower().strip()
    return re.sub(r"[\s_]+", "-", text)


def load_calendar(book_slug: str) -> tuple[dict, Path]:
    path = Path(f"output/{book_slug}/calendar.json")
    if not path.exists():
        raise FileNotFoundError(f"Calendar not found: {path}")
    return json.loads(path.read_text()), path


def get_episode(cal: dict, ep_id: int) -> dict:
    for ep in cal["episodes"]:
        if ep["id"] == ep_id:
            return ep
    raise ValueError(f"Episode {ep_id} not found in calendar")


_calendar_lock = threading.Lock() if False else None  # placeholder; use file-system lock


def update_episode(book_slug: str, ep_id: int, **fields) -> None:
    """Atomic update of an episode in calendar.json. Safe under parallel processes via file lock + per-pid tmp."""
    import os, fcntl
    cal, path = load_calendar(book_slug)
    lock_path = path.with_suffix(".json.lock")

    # Acquire exclusive file lock (cross-process safe on POSIX)
    with open(lock_path, "w") as lock_fp:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX)
        # Re-read inside lock to avoid stale data
        cal = json.loads(path.read_text())
        ep = get_episode(cal, ep_id)
        ep.update(fields)
        cal["completed"] = sum(1 for e in cal["episodes"] if e["status"] == "done")
        # Per-pid tmp name avoids race between parallel processes
        tmp = path.with_suffix(f".json.tmp.{os.getpid()}")
        tmp.write_text(json.dumps(cal, ensure_ascii=False, indent=2))
        tmp.replace(path)
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)


def extract_topic_script(ep: dict, book: dict, ep_dir: Path,
                         target_seconds: int = 90) -> dict:
    """Step: extract Gemini script focused on episode topic."""
    out = ep_dir / "script.json"
    if out.exists():
        logger.info("[skip] script.json exists")
        return json.loads(out.read_text())["data"]["script"][0]

    payload = {
        "mode": "manual",
        "format": "quote",
        "source": {
            "outline": f"{book['title']}: 30 nguyên tắc giao tiếp ứng xử của {book['author']}",
            "metadata": book,
        },
        "options": {
            "count": 1,
            "target_seconds": target_seconds,
            "topic": f"{ep['title']} — {ep['key_idea']}",
        },
    }
    data = _api_post_with_retry("/api/book/extract-script", payload, timeout=120)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data["data"]["script"][0]


def gen_flow_images(script: dict, book_slug: str, ep_id: int, ep: dict,
                    ep_dir: Path, scene_count: int = 7) -> list[Path]:
    """Step: create Flow project + scenes + gen images. Idempotent."""
    images_dir = ep_dir / "images"
    scene_ids_file = ep_dir / "scene_ids.json"

    expected = [images_dir / f"scene_{i}.jpg" for i in range(scene_count)]
    if all(p.exists() and p.stat().st_size > 1000 for p in expected):
        logger.info("[skip] %d images exist", scene_count)
        return expected

    # Create project + video + scenes
    if not scene_ids_file.exists():
        proj = requests.post(f"{API_BASE}/api/projects", json={
            "name": f"{book_slug.upper()} EP{ep_id:02d} {ep['title'][:30]}",
            "description": f"{book_slug} series episode {ep_id}",
            "language": "vi",
            "material": "realistic",
            "orientation": "VERTICAL",
        }).json()
        vid = requests.post(f"{API_BASE}/api/videos", json={
            "project_id": proj["id"],
            "title": f"EP {ep_id:02d}",
            "orientation": "VERTICAL",
        }).json()
        # Pick N scene_prompts (spread coverage)
        prompts = [i["scene_prompt"] for i in script["insights"]]
        if len(prompts) < scene_count:
            # Repeat last prompt to fill if needed
            prompts = (prompts * ((scene_count // len(prompts)) + 1))[:scene_count]
        else:
            # Even spread sample
            step = max(1, len(prompts) // scene_count)
            prompts = [prompts[i * step] for i in range(scene_count)]

        scene_ids = []
        for idx, prompt in enumerate(prompts):
            s = requests.post(f"{API_BASE}/api/scenes", json={
                "video_id": vid["id"], "display_order": idx,
                "prompt": prompt, "image_prompt": prompt,
            }).json()
            scene_ids.append(s["id"])

        scene_ids_file.write_text(json.dumps({
            "project_id": proj["id"], "video_id": vid["id"], "scene_ids": scene_ids,
        }, indent=2))

    ids = json.loads(scene_ids_file.read_text())
    scene_id_list = ids["scene_ids"]

    def _scene_states() -> list[dict]:
        return [requests.get(f"{API_BASE}/api/scenes/{sid}").json() for sid in scene_id_list]

    def _need_gen() -> list[int]:
        states = _scene_states()
        return [i for i, s in enumerate(states)
                if not s.get("vertical_image_url") or s.get("vertical_image_status") != "COMPLETED"]

    # Submit batch only for scenes that don't have image yet
    pending_idx = _need_gen()
    if pending_idx:
        for i in pending_idx:
            sid = scene_id_list[i]
            requests.patch(f"{API_BASE}/api/scenes/{sid}", json={"vertical_image_status": "PENDING"})
        reqs = [{
            "type": "GENERATE_IMAGE", "orientation": "VERTICAL",
            "project_id": ids["project_id"], "video_id": ids["video_id"],
            "scene_id": scene_id_list[i],
        } for i in pending_idx]
        requests.post(f"{API_BASE}/api/requests/batch", json={"requests": reqs})
        logger.info("Submitted gen-image for %d/%d scenes", len(pending_idx), scene_count)

    # Poll scene-level state (not request status — those are unreliable due to reCAPTCHA)
    deadline = time.time() + 600
    last_progress = -1
    while time.time() < deadline:
        states = _scene_states()
        ok = sum(1 for s in states if s.get("vertical_image_url") and s.get("vertical_image_status") == "COMPLETED")
        if ok != last_progress:
            logger.info("    scenes ready: %d/%d", ok, scene_count)
            last_progress = ok
        if ok == scene_count:
            break
        # If some FAILED with no image url, retry just those
        retry_idx = [i for i, s in enumerate(states)
                     if s.get("vertical_image_status") == "FAILED" and not s.get("vertical_image_url")]
        if retry_idx and ok + len(retry_idx) < scene_count:
            # Don't retry; let timeout handle to avoid loop. Caller can re-run.
            pass
        elif retry_idx:
            logger.info("    retrying %d failed scenes", len(retry_idx))
            for i in retry_idx:
                sid = scene_id_list[i]
                requests.patch(f"{API_BASE}/api/scenes/{sid}", json={"vertical_image_status": "PENDING"})
            reqs = [{
                "type": "GENERATE_IMAGE", "orientation": "VERTICAL",
                "project_id": ids["project_id"], "video_id": ids["video_id"],
                "scene_id": scene_id_list[i],
            } for i in retry_idx]
            requests.post(f"{API_BASE}/api/requests/batch", json={"requests": reqs})
        time.sleep(15)

    # Download whatever is ready (may raise if any still missing)
    images_dir.mkdir(parents=True, exist_ok=True)
    out_paths = []
    states = _scene_states()
    for idx, s in enumerate(states):
        url = s.get("vertical_image_url")
        if not url:
            raise RuntimeError(f"Scene {idx} has no image URL after polling")
        path = images_dir / f"scene_{idx}.jpg"
        with requests.get(url, stream=True) as resp:
            path.write_bytes(resp.content)
        out_paths.append(path)
    return out_paths


def apply_ken_burns(images: list[Path], ep_dir: Path,
                    durations: list[int], motions: list[str]) -> list[Path]:
    """Step: apply Ken Burns motion to each image. Idempotent."""
    clips_dir = ep_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    out_clips = []
    for idx, (img, dur, motion) in enumerate(zip(images, durations, motions)):
        out = clips_dir / f"scene_{idx}.mp4"
        if out.exists() and out.stat().st_size > 10000:
            out_clips.append(out)
            continue
        r = requests.post(f"{API_BASE}/api/ken-burns/clip", json={
            "image_path": str(img),
            "duration_seconds": dur,
            "motion": motion,
            "resolution": "1080x1920",
            "output_path": str(out),
        }, timeout=120)
        if not r.json().get("ok"):
            raise RuntimeError(f"Ken Burns scene {idx} failed: {r.text}")
        out_clips.append(out)
    return out_clips


def concat_scenes(clips: list[Path], durations: list[int], ep_dir: Path) -> Path:
    """Step: concat clips with xfade. Idempotent."""
    out = ep_dir / "concat_scenes.mp4"
    if out.exists() and out.stat().st_size > 10000:
        return out
    items = [{"path": str(c), "duration": d} for c, d in zip(clips, durations)]
    r = requests.post(f"{API_BASE}/api/ken-burns/concat", json={
        "clips": items, "xfade_duration": 0.5,
        "output_path": str(out),
    }, timeout=120)
    if not r.json().get("ok"):
        raise RuntimeError(f"Concat failed: {r.text}")
    return out


def gen_tts(narrator_text: str, voice: str, ep_dir: Path) -> Path:
    """Step: generate TTS. Long timeout, idempotent."""
    out = ep_dir / "tts" / "narrator.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 10000:
        return out
    template_name = TTS_TEMPLATES[voice]
    r = requests.post(f"{API_BASE}/api/tts/generate", json={
        "text": narrator_text,
        "template": template_name,  # API resolves ref_audio + ref_text from registry
        "speed": 0.95,
        "output_path": str(out),
    }, timeout=600)
    if not (out.exists() and out.stat().st_size > 10000):
        raise RuntimeError(f"TTS failed: {r.text[:200]}")
    return out


def gen_music(ep_dir: Path, prompt: Optional[str] = None,
              skip_gen: bool = False) -> Path:
    """Step: generate or reuse instrumental music. Returns mp3 path."""
    if skip_gen:
        # Reuse most recent track from shared
        shared = Path("output/_shared/gemini_music")
        tracks = sorted(shared.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
        if tracks:
            return tracks[0]
    default_prompt = (
        "instrumental ambient music ONLY, NO vocals, NO singing, NO lyrics, "
        "calm contemplative meditation soundscape, soft warm strings and gentle piano, "
        "podcast background music, slow tempo, peaceful, low energy, "
        "suitable for narration overlay"
    )
    r = requests.post(f"{API_BASE}/api/gemini/browser/generate-music", json={
        "prompt": prompt or default_prompt,
        "model": "Pro",
        "timeout": 360,
        "headless": True,
        "audio_format": "mp3",
    }, timeout=420)
    d = r.json()
    if not d.get("ok"):
        raise RuntimeError(f"Music gen failed: {d}")
    return Path(d["path"])


def mix_final(concat_video: Path, tts_audio: Path, music_src: Path,
              ep_dir: Path, target_dur: int) -> Path:
    """Step: trim video+music to TTS duration (+2s buffer), mix, output final.mp4.

    Video duration is now driven by TTS to avoid silent music tail.
    """
    out = ep_dir / "final.mp4"
    if out.exists() and out.stat().st_size > 10000:
        return out

    # End video shortly after narrator finishes (small buffer for natural fade)
    tts_dur = get_video_duration(tts_audio)
    video_dur = get_video_duration(concat_video)
    final_dur = min(int(tts_dur) + 2, int(video_dur))

    music_wav = ep_dir / "music" / "bgm.wav"
    music_wav.parent.mkdir(parents=True, exist_ok=True)
    # Loop music + fade out 2s before end
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(music_src),
        "-t", str(final_dur), "-ar", "48000", "-ac", "2",
        "-af", f"afade=t=out:st={final_dur - 2}:d=2",
        str(music_wav),
    ], check=True, capture_output=True)

    # Final mix — video trimmed to final_dur (= TTS + 2s buffer)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(concat_video), "-i", str(tts_audio), "-i", str(music_wav),
        "-filter_complex",
        "[1:a]volume=1.5[tts];[2:a]volume=0.15[music];"
        "[tts][music]amix=inputs=2:duration=longest:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-movflags", "+faststart", "-t", str(final_dur),
        str(out),
    ], check=True, capture_output=True)
    return out


def gen_caption(script: dict, ep: dict, ep_dir: Path, book: dict) -> Path:
    """Step: generate Vietnamese caption + hashtags via Gemini key-rotation pool."""
    out = ep_dir / "caption.txt"
    if out.exists() and out.stat().st_size > 50:
        return out

    # Lazy import — pool reads keys at module load
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent.services.gemini_key_pool import call_gemini_sync

    book_tag = "#" + slugify_vi(book["title"]).replace("-", "")
    system_prompt = (
        "You write Vietnamese TikTok/Reels captions for book podcast Shorts.\n\n"
        "Output ONLY plain text:\n"
        "Line 1-2: Hook tiếng Việt 1-2 câu (~30-40 từ tổng) — câu thầm thì, gợi suy ngẫm.\n"
        "[empty line]\n"
        "Line 4: 7-10 hashtags Vietnamese + English mix.\n\n"
        "Rules:\n"
        "- Hook KHÔNG mention tên sách/tác giả\n"
        f"- Hashtags MUST include: {book_tag}, niche tags (#sachhay #podcast #tinhhoasach), topic tags\n"
        "- 1-2 emoji optional\n"
        "- NO call-to-action, NO 'follow', 'subscribe' speech\n"
    )
    user_prompt = (
        f"Episode topic: {ep['title']}\n"
        f"Quote: {script['quote']}\n"
        f"Outro: {script['outro']}\n\n"
        "Write a caption."
    )
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
    }
    result = call_gemini_sync(payload, model="gemini-2.5-flash", timeout=60)
    text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
    out.write_text(text)
    return out


def get_video_duration(path: Path) -> float:
    """Read video duration via ffprobe."""
    r = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def extend_last_scene_if_needed(images: list[Path], clips: list[Path],
                                 durations: list[int], motions: list[str],
                                 ep_dir: Path, tts_dur: float) -> tuple[list[Path], list[int]]:
    """If TTS longer than concat video, re-render last scene with longer duration."""
    concat_dur = sum(durations) - 0.5 * (len(durations) - 1)
    if tts_dur <= concat_dur:
        return clips, durations

    needed = int(tts_dur - concat_dur + 3)  # +3s buffer
    durations[-1] += needed
    last_clip = clips[-1]
    last_clip.unlink(missing_ok=True)  # force re-render

    r = requests.post(f"{API_BASE}/api/ken-burns/clip", json={
        "image_path": str(images[-1]),
        "duration_seconds": durations[-1],
        "motion": motions[-1],
        "resolution": "1080x1920",
        "output_path": str(last_clip),
    }, timeout=120)
    if not r.json().get("ok"):
        raise RuntimeError(f"Re-render last scene failed: {r.text}")

    # Force re-concat (delete to trigger)
    (ep_dir / "concat_scenes.mp4").unlink(missing_ok=True)
    return clips, durations
