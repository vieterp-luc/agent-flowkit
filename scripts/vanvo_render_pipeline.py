#!/usr/bin/env python3
"""Van Vo pipeline — render long-form Vietnamese fairy tale videos with Gen Z slang.

Used by /fk-van-vo skill. Modular per-book, resumable, idempotent.

Pipeline stages per book:
  1. Flow project + video + 15 scenes (scene 0 intro + scenes 1-14 story)
  2. Batch GENERATE_IMAGE via /api/requests/batch
  3. TTS via Thang_QC_TTS @ 0.9
  4. Ken Burns clips (face-safe motion mapping)
  5. Concat clips + narrator + bgm mix → ep01_final.mp4
  6. Thumbnail (ffmpeg drawtext) + caption.txt

Usage:
    python vanvo_render_pipeline.py              # run all books
    python vanvo_render_pipeline.py thach-sanh   # run single book
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

API = "http://127.0.0.1:8100"
ROOT = Path(__file__).parent.parent
OUTPUT_BASE = ROOT / "output" / "van_vo"
FONT_VN = "/Library/Fonts/Arial Unicode.ttf"
MUSIC_SRC = ROOT / "output/lofi/vintage_cafe_60min_1778576410/concat_music.mp3"
TTS_VOICE = "Thang_QC_TTS"
TTS_SPEED = 0.9

STYLE = ("anime manhwa Korean color grading, vibrant cyan + gold + neon magenta palette, "
         "dramatic rim lighting, comic book panel framing. STRICTLY NO TEXT no logos no signs "
         "no letters on clothing. 16:9 horizontal cinematic.")

INTRO_NARR = "Chào mừng anh em đến với seri cổ tích thời gen z."
INTRO_IMG = (
    "Cinematic branding intro card for a Vietnamese fairy tale series: an ornate ancient "
    "Vietnamese storybook lying open on a dark velvet surface with glowing magical pages "
    "emanating cyan + gold + neon magenta sparkles, traditional Vietnamese motifs (lotus, "
    "dragon, banyan tree silhouettes) floating around in the background, dramatic spotlight "
    "from above. Atmospheric mystical mood. STRICTLY NO TEXT no logos no signs no letters. "
    "16:9 horizontal cinematic intro shot."
)

# Project-level image_style applied to every Flow image gen call
PROJECT_IMAGE_STYLE = (
    "Anime manhwa Korean color style, vibrant cyan + gold + neon magenta palette, "
    "dramatic rim lighting, comic book panel framing. CHARACTERS: 2020s Vietnamese "
    "streetwear hybrid — oversized hoodies/bombers, ripped jeans/shorts, sneakers, gold "
    "chains, aviator sunglasses, undercut moi hair platinum/blonde. Clothing SOLID COLOR "
    "ONLY — no graffiti, no printed pattern, no logo. NATURAL confident pose — AVOID gym "
    "flex. BACKGROUND: authentic era setting matching the tale. STRICTLY NO TEXT, NO "
    "subtitles, NO signs, NO letters on clothing. HORIZONTAL 16:9 cinematic."
)


# ---------- API helpers ----------

def api_post(path: str, payload: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def api_get(path: str, timeout: int = 30) -> dict:
    with urllib.request.urlopen(f"{API}{path}", timeout=timeout) as resp:
        return json.loads(resp.read())


def ffprobe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def run(cmd: list, **kw):
    subprocess.run(cmd, check=True, capture_output=True, **kw)


# ---------- Pipeline stages ----------

def create_project(book: dict) -> str:
    """Create Flow project. Returns project_id."""
    payload = {
        "name": f"VanVo_{book['slug']}",
        "description": f"Văn Vở phong cách Gen Z — {book['title']}",
        "story": book["story_summary"],
        "material": "realistic",
        "image_style": PROJECT_IMAGE_STYLE,
        "language": "vi",
        "orientation": "HORIZONTAL",
    }
    r = api_post("/api/projects", payload)
    return r["id"]


def create_video(pid: str, book: dict) -> str:
    """Create video record. Returns video_id."""
    payload = {
        "project_id": pid,
        "title": f"ep01_{book['slug']}",
        "video_story": f"{book['title']} kể phong cách Văn Vở — {len(book['scripts'])+1} scenes (1 intro + {len(book['scripts'])} story).",
        "display_order": 1,
        "orientation": "HORIZONTAL",
    }
    return api_post("/api/videos", payload)["id"]


def create_scenes(vid: str, book: dict) -> list[str]:
    """Create 15 scene records (0=intro, 1-14=story). Returns list of scene_ids."""
    scene_ids = []
    # Scene 0: intro
    payload = {
        "video_id": vid,
        "display_order": 1,  # Flow uses 1-indexed; we map our scene_0 → display 1
        "prompt": INTRO_NARR,
        "image_prompt": INTRO_IMG,
    }
    scene_ids.append(api_post("/api/scenes", payload)["id"])
    # Scenes 1-14: story
    for i, (narr, img) in enumerate(zip(book["scripts"], book["image_prompts"]), start=2):
        full_img = f"{img} {STYLE}"
        payload = {
            "video_id": vid,
            "display_order": i,
            "prompt": narr,
            "image_prompt": full_img,
        }
        scene_ids.append(api_post("/api/scenes", payload)["id"])
    return scene_ids


def batch_generate_images(pid: str, vid: str, scene_ids: list[str]) -> None:
    """[Legacy] Submit batch image gen request — triggers reCAPTCHA easily, avoid."""
    payload = {
        "requests": [
            {"type": "GENERATE_IMAGE", "project_id": pid, "video_id": vid,
             "scene_id": sid, "orientation": "HORIZONTAL"}
            for sid in scene_ids
        ]
    }
    api_post("/api/requests/batch", payload, timeout=60)


def paced_generate_images(pid: str, vid: str, scene_ids: list[str],
                          inter_request_delay: float = 2.0,
                          poll_every: int = 5, max_wait_per: int = 180) -> None:
    """Submit image gen requests ONE AT A TIME, wait each to complete before next.
    Avoids reCAPTCHA bot detection by spacing out requests like a human.

    Each scene takes ~30s gen + 2s delay = ~32s. 15 scenes ≈ 8 minutes.
    """
    total = len(scene_ids)
    for i, sid in enumerate(scene_ids, 1):
        payload = {"type": "GENERATE_IMAGE", "project_id": pid, "video_id": vid,
                   "scene_id": sid, "orientation": "HORIZONTAL"}
        req = api_post("/api/requests", payload, timeout=30)
        req_id = req["id"]

        # Wait for this single request to complete
        start = time.time()
        while time.time() - start < max_wait_per:
            r = api_get(f"/api/requests/{req_id}")
            status = r["status"]
            if status == "COMPLETED":
                print(f"  paced image [{i}/{total}]: ok")
                break
            if status == "FAILED":
                err = r.get("error_message", "")
                if "reCAPTCHA" in err or "UNUSUAL_ACTIVITY" in err:
                    raise RuntimeError(f"reCAPTCHA hit at scene [{i}/{total}] — halt")
                raise RuntimeError(f"Image gen failed scene [{i}/{total}]: {err}")
            time.sleep(poll_every)
        else:
            raise TimeoutError(f"Image gen [{i}/{total}] timeout {max_wait_per}s")

        # Pace before next request
        if i < total:
            time.sleep(inter_request_delay)


def wait_images_done(vid: str, expected: int, poll_every: int = 15, max_wait: int = 900) -> None:
    """Poll until all images for this video are done."""
    start = time.time()
    while time.time() - start < max_wait:
        pending = api_get("/api/requests/pending")
        my_pending = [x for x in pending if x.get("video_id") == vid]
        if not my_pending:
            return
        print(f"  pending images: {len(my_pending)}")
        time.sleep(poll_every)
    raise TimeoutError(f"Images didn't finish in {max_wait}s")


def download_images_and_tts(vid: str, ep_dir: Path, book: dict) -> None:
    """Download all scene images + generate TTS per scene."""
    img_dir = ep_dir / "images"
    tts_dir = ep_dir / "tts"
    img_dir.mkdir(parents=True, exist_ok=True)
    tts_dir.mkdir(parents=True, exist_ok=True)

    scenes = api_get(f"/api/scenes?video_id={vid}")
    scenes_sorted = sorted(scenes, key=lambda x: x["display_order"])

    for s in scenes_sorted:
        n = s["display_order"] - 1  # display 1 → file scene_00, display 2 → scene_01, etc.
        # Image
        img_path = img_dir / f"scene_{n:02d}.png"
        if not img_path.exists() or img_path.stat().st_size < 50000:
            url = s.get("horizontal_image_url")
            # Retry up to 6 times (30s total) for URL to appear (race condition)
            for attempt in range(6):
                if url:
                    break
                time.sleep(5)
                s = api_get(f"/api/scenes/{s['id']}")
                url = s.get("horizontal_image_url")
            if not url:
                raise RuntimeError(f"Scene {n} image URL never appeared after 30s")
            urllib.request.urlretrieve(url, img_path)
        # TTS
        tts_path = tts_dir / f"scene_{n:02d}.wav"
        if not tts_path.exists() or tts_path.stat().st_size < 10000:
            # narrator text is in scene.prompt (may have Canon RAW prefix added by Flow)
            text = s["prompt"]
            if "Real RAW photograph" in text:
                idx = text.find("light. ")
                if idx > 0:
                    text = text[idx+7:]
            payload = {"template": TTS_VOICE, "speed": TTS_SPEED,
                       "output_path": str(tts_path), "text": text}
            api_post("/api/tts/generate", payload, timeout=600)
        print(f"  scene_{n:02d}: img + tts ok")


def gen_ken_burns_clips(ep_dir: Path, motions: list[str]) -> None:
    """Generate Ken Burns clips matching TTS duration. motions[0] = intro, motions[1..N] = story."""
    img_dir = ep_dir / "images"
    tts_dir = ep_dir / "tts"
    clips_dir = ep_dir / "clips"
    clips_dir.mkdir(exist_ok=True)
    # Delete old clips to ensure fresh durations
    for f in clips_dir.glob("scene_*.mp4"):
        f.unlink()

    total_scenes = len(motions)
    for n in range(total_scenes):
        img = img_dir / f"scene_{n:02d}.png"
        wav = tts_dir / f"scene_{n:02d}.wav"
        out = clips_dir / f"scene_{n:02d}.mp4"
        dur = min(ffprobe_dur(wav) + 1.5, 60.0)
        motion = motions[n]
        payload = {"image_path": str(img), "duration_seconds": dur, "motion": motion,
                   "resolution": "1920x1080", "output_path": str(out)}
        r = api_post("/api/ken-burns/clip", payload)
        if not r.get("ok"):
            raise RuntimeError(f"Ken Burns scene {n} failed: {r}")
        print(f"  scene_{n:02d}: {motion} {dur:.1f}s")


def concat_clips(ep_dir: Path) -> Path:
    """Concat all clips with xfade 0.5s — dynamic scene count."""
    clips_dir = ep_dir / "clips"
    out = ep_dir / "concat_scenes.mp4"
    out.unlink(missing_ok=True)
    # Auto-discover clip files by sorted filename
    clip_files = sorted(clips_dir.glob("scene_*.mp4"))
    clips_info = [
        {"path": str(p), "duration": ffprobe_dur(p)}
        for p in clip_files
    ]
    payload = {"clips": clips_info, "xfade_duration": 0.5, "output_path": str(out)}
    api_post("/api/ken-burns/concat", payload, timeout=600)
    return out


def build_narrator(ep_dir: Path) -> Path:
    """Concat all TTS wavs with 1s silence between — dynamic scene count."""
    tts_dir = ep_dir / "tts"
    silence = ep_dir / "silence_1s.wav"
    if not silence.exists():
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", "1.0", "-q:a", "0", str(silence)])
    tts_files = sorted(tts_dir.glob("scene_*.wav"))
    list_file = ep_dir / "tts_list.txt"
    with open(list_file, "w") as f:
        for i, p in enumerate(tts_files):
            f.write(f"file '{p.as_posix()}'\n")
            if i < len(tts_files) - 1:
                f.write(f"file '{silence.as_posix()}'\n")
    out = ep_dir / "narrator_concat.wav"
    out.unlink(missing_ok=True)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:a", "pcm_s16le", "-ar", "24000", str(out)])
    return out


def mix_final(ep_dir: Path, video: Path, narrator: Path) -> Path:
    """Mix video + narrator only (NO background music — user feedback)."""
    final = ep_dir / "ep01_final.mp4"
    final.unlink(missing_ok=True)
    run(["ffmpeg", "-y",
         "-i", str(video), "-i", str(narrator),
         "-filter_complex", "[1:a]volume=1.5[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
    return final


def build_thumbnail(ep_dir: Path, book: dict) -> Path:
    """Build 1280x720 thumbnail from scene_02 with text overlay."""
    base = ep_dir / "images" / "scene_02.png"
    out = ep_dir / "thumbnail.png"
    title_text = book["title"].upper()
    vf = (
        "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
        "drawbox=x=0:y=0:w=1280:h=170:color=black@0.55:t=fill,"
        "drawbox=x=0:y=550:w=1280:h=170:color=black@0.65:t=fill,"
        f"drawtext=fontfile='{FONT_VN}':text='SERI CỔ TÍCH THỜI GEN Z':"
        "fontcolor=#00f0ff:fontsize=48:x=(w-text_w)/2:y=58:"
        "shadowcolor=black:shadowx=3:shadowy=3,"
        f"drawtext=fontfile='{FONT_VN}':text='{title_text}':"
        "fontcolor=#ffd700:fontsize=130:x=(w-text_w)/2:y=585:"
        "shadowcolor=black:shadowx=4:shadowy=4"
    )
    run(["ffmpeg", "-y", "-i", str(base), "-vf", vf,
         "-frames:v", "1", "-update", "1", str(out)])
    return out


def write_caption(ep_dir: Path, book: dict) -> Path:
    """Write caption.txt — MXH-ready with hook + bullets + hashtags."""
    out = ep_dir / "caption.txt"
    slug_tag = book["slug"].replace("-", "")
    hashtags = (
        f"#cotich #{slug_tag} #vanhoc #vietnam #genzliterature #vanvo "
        f"#vietnamesefolktale #podcast #storyteller"
    )
    text = f"""🎬 SERI CỔ TÍCH THỜI GEN Z — {book['title'].upper()} 🎬

{book.get('caption_hook', 'Anh em đã nghe truyện này phiên bản Gen Z chưa? 😱')}

Trong tập này:
{chr(10).join('✨ ' + b for b in book.get('caption_bullets', []))}

{book.get('caption_moral', 'Câu chuyện dạy ta nhiều bài học sâu sắc về cuộc đời này.')}

🎧 Voice: AI Vietnamese narrator
🎨 Visual: Manhwa hybrid style (cổ tích × streetwear 2020s)
🎵 Music: Lofi vintage cafe

👉 Theo dõi để nghe tiếp series cổ tích VN với góc nhìn Gen Z!

{hashtags}
"""
    out.write_text(text, encoding="utf-8")
    return out


# ---------- Main per-book runner ----------

def run_book(book: dict) -> None:
    print(f"\n{'='*60}\n📖 {book['title']} ({book['slug']})\n{'='*60}")
    ep_dir = OUTPUT_BASE / book["slug"] / "ep01"
    ep_dir.mkdir(parents=True, exist_ok=True)
    final_path = ep_dir / "ep01_final.mp4"

    # Skip if already produced
    if final_path.exists() and (ep_dir / "thumbnail.png").exists() and (ep_dir / "caption.txt").exists():
        print(f"  ✓ Already produced: {final_path}")
        return

    # Stage 1-2: Project + scenes
    project_meta = ep_dir / "_project.json"
    if project_meta.exists():
        meta = json.loads(project_meta.read_text())
        pid, vid, scene_ids = meta["pid"], meta["vid"], meta["scene_ids"]
        print(f"  Resumed project {pid}, video {vid}")
    else:
        pid = create_project(book)
        vid = create_video(pid, book)
        scene_ids = create_scenes(vid, book)
        project_meta.write_text(json.dumps({"pid": pid, "vid": vid, "scene_ids": scene_ids}))
        print(f"  Created project {pid}, video {vid}, {len(scene_ids)} scenes")

    # Stage 3: Batch image gen + wait — only if scenes don't already have images on Flow
    img_dir = ep_dir / "images"
    img_dir.mkdir(exist_ok=True)
    existing_imgs = len([p for p in img_dir.glob("scene_*.png") if p.stat().st_size > 50000])
    total_scenes = len(book["scripts"]) + 1  # intro + body
    if existing_imgs < total_scenes:
        # Check Flow scene records for completed images (resume case)
        scenes = api_get(f"/api/scenes?video_id={vid}")
        scenes_done_set = {s["id"] for s in scenes if s.get("horizontal_image_status") == "COMPLETED"}
        scenes_todo = [sid for sid in scene_ids if sid not in scenes_done_set]
        if scenes_todo:
            print(f"  Paced image gen ({existing_imgs}/{total_scenes} local, {len(scenes_done_set)}/{total_scenes} on Flow, {len(scenes_todo)} todo)...")
            paced_generate_images(pid, vid, scenes_todo, inter_request_delay=2.0)
        else:
            print(f"  Skipping image gen — Flow has all {total_scenes} images ready, just need download")

    # Stage 4: Download images + gen TTS
    print("  Downloading images + generating TTS...")
    download_images_and_tts(vid, ep_dir, book)

    # Stage 5: Ken Burns clips
    print("  Generating Ken Burns clips...")
    gen_ken_burns_clips(ep_dir, book["motions"])

    # Stage 6: Concat
    print("  Concatenating clips...")
    video = concat_clips(ep_dir)

    # Stage 7: Narrator + mix
    print("  Building narrator + mixing final...")
    narrator = build_narrator(ep_dir)
    final = mix_final(ep_dir, video, narrator)

    # Stage 8: Thumbnail + caption
    print("  Building thumbnail + caption...")
    thumb = build_thumbnail(ep_dir, book)
    cap = write_caption(ep_dir, book)

    dur = ffprobe_dur(final)
    size_mb = final.stat().st_size / 1024 / 1024
    print(f"\n  ✅ DONE: {final}")
    print(f"     {size_mb:.1f}MB / {dur:.0f}s ({dur/60:.1f}min)")
    print(f"     thumbnail: {thumb}")
    print(f"     caption: {cap}")


# ---------- Entry point ----------

def main():
    from vanvo_books_data import BOOKS
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        if target not in BOOKS:
            print(f"Unknown book: {target}. Available: {list(BOOKS.keys())}")
            sys.exit(1)
        run_book(BOOKS[target])
    else:
        for slug, book in BOOKS.items():
            try:
                run_book(book)
            except Exception as e:
                print(f"\n  ❌ FAILED {slug}: {e}")
                continue


if __name__ == "__main__":
    main()
