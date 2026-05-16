"""Render a single book podcast episode end-to-end from calendar.

Usage:
  venv/bin/python scripts/render_podcast_episode.py <book_slug> <ep_id> [options]

Example:
  venv/bin/python scripts/render_podcast_episode.py dac_nhan_tam 5 --voice hong_hanh
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Allow running as `python scripts/render_podcast_episode.py`
sys.path.insert(0, str(Path(__file__).parent))

import podcast_render_lib as lib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("podcast_render")


# Default 7-scene Ken Burns template (durations + motions)
SCENE_TEMPLATE_7 = {
    "durations": [12, 14, 14, 14, 14, 14, 14],  # 96s, minus 6×0.5 xfade = 93s
    "motions": ["zoom_in", "pan_left", "pan_right", "zoom_in", "pan_left", "pan_right", "zoom_out"],
}


def build_scene_template(scene_count: int) -> dict:
    """Generate balanced durations + motions for any scene count 4-8."""
    motions_pool = ["zoom_in", "pan_left", "pan_right", "zoom_out", "pan_left", "pan_right", "zoom_in"]
    motions = motions_pool[:scene_count - 1] + ["zoom_out"]
    # Default 14s body, 12s outer scenes
    durations = [12] + [14] * (scene_count - 2) + [14]
    return {"durations": durations, "motions": motions}


def main():
    parser = argparse.ArgumentParser(description="Render a podcast episode from calendar")
    parser.add_argument("book_slug", help="e.g. dac_nhan_tam")
    parser.add_argument("ep_id", type=int, help="episode id from calendar")
    parser.add_argument("--voice", choices=["phap_van", "hong_hanh", "podcast_male"], default="hong_hanh")
    parser.add_argument("--scene-count", type=int, default=5,
                        help="Number of scenes. Default 5 = ~60s fits TTS narrator (was 7, wasted 2 scenes).")
    parser.add_argument("--target-seconds", type=int, default=90)
    parser.add_argument("--speed", type=float, default=0.95, help="TTS speed (0.5-1.5, slower=lower)")
    parser.add_argument("--skip-music-gen", action="store_true",
                        help="Reuse most recent track from output/_shared/gemini_music/")
    parser.add_argument("--force", action="store_true",
                        help="Re-render all steps (ignore existing artifacts)")
    parser.add_argument("--brand", default="sach-thi-tham",
                        help="Channel slug for logo overlay (default sach-thi-tham). Logo is always applied.")
    parser.add_argument("--logo-size", type=int, default=150)
    parser.add_argument("--logo-pos", default="top-left",
                        choices=["top-left", "top-right", "bottom-left", "bottom-right"])
    args = parser.parse_args()

    cal, _ = lib.load_calendar(args.book_slug)
    ep = lib.get_episode(cal, args.ep_id)
    book = cal["book"]

    if ep["status"] == "done" and not args.force:
        logger.info("EP %02d already rendered: %s", args.ep_id, ep["video_path"])
        return 0

    # Setup folder
    title_slug = lib.slugify_vi(ep["title"])
    ep_dir = lib.BOOKS_BASE / args.book_slug / f"ep_{args.ep_id:02d}_{title_slug}"
    ep_dir.mkdir(parents=True, exist_ok=True)

    if args.force:
        logger.info("--force: clearing existing artifacts")
        for f in ["script.json", "scene_ids.json", "concat_scenes.mp4",
                  "_main.mp4", "final.mp4", "final_logo.mp4", "caption.txt"]:
            (ep_dir / f).unlink(missing_ok=True)
        for sub in ["clips", "tts", "music"]:
            for f in (ep_dir / sub).glob("*"):
                f.unlink()

    lib.update_episode(args.book_slug, args.ep_id, status="rendering")
    logger.info("=== Rendering EP %02d: %s ===", args.ep_id, ep["title"])

    # Step 1: Extract topic-focused script
    logger.info("[1/9] Extract topic script")
    script = lib.extract_topic_script(ep, book, ep_dir, target_seconds=args.target_seconds)

    # Step 2: Flow image gen
    logger.info("[2/9] Gen %d images via Flow", args.scene_count)
    images = lib.gen_flow_images(script, args.book_slug, args.ep_id, ep, ep_dir,
                                  scene_count=args.scene_count, book=book)

    # Step 3: Ken Burns motion
    template = build_scene_template(args.scene_count)
    durations = list(template["durations"])
    motions = list(template["motions"])
    if len(durations) != len(images):
        # Adjust template to match actual image count
        durations = [12] + [14] * (len(images) - 2) + [14]
        motions = (motions * 2)[:len(images) - 1] + ["zoom_out"]
    logger.info("[3/9] Apply Ken Burns motion")
    clips = lib.apply_ken_burns(images, ep_dir, durations, motions)

    # Step 4: Concat
    logger.info("[4/9] Concat with xfade")
    concat = lib.concat_scenes(clips, durations, ep_dir)

    # Step 5: TTS
    logger.info("[5/9] Gen TTS (%s)", args.voice)
    parts = [script["quote"]] + [i["narrator_text"] for i in script["insights"]] + [script["outro"]]
    narrator_text = " ".join(parts)
    tts = lib.gen_tts(narrator_text, args.voice, ep_dir, speed=args.speed)
    tts_dur = lib.get_video_duration(tts)
    logger.info("    TTS duration: %.1fs", tts_dur)

    # Step 5b: Sync video duration to TTS if needed
    concat_dur = lib.get_video_duration(concat)
    if tts_dur > concat_dur:
        logger.info("[5b] TTS (%.1fs) > video (%.1fs), extending last scene", tts_dur, concat_dur)
        clips, durations = lib.extend_last_scene_if_needed(
            images, clips, durations, motions, ep_dir, tts_dur,
        )
        concat = lib.concat_scenes(clips, durations, ep_dir)
        concat_dur = lib.get_video_duration(concat)

    target_dur = max(int(concat_dur), int(tts_dur) + 1)

    # Step 6: Music
    logger.info("[6/9] Gen music (skip=%s)", args.skip_music_gen)
    music_src = lib.gen_music(ep_dir, skip_gen=args.skip_music_gen)
    logger.info("    Music: %s", music_src.name)

    # Step 7: Mix → _main.mp4 (intermediate; step 9 overlays logo → final.mp4)
    logger.info("[7/9] Audio mix → _main.mp4")
    main_video = lib.mix_final(concat, tts, music_src, ep_dir, target_dur)

    # Step 8: Caption
    logger.info("[8/9] Gen caption")
    caption = lib.gen_caption(script, ep, ep_dir, book)

    # Step 9: Logo overlay (always required) → final.mp4
    logger.info("[9/9] Logo overlay (channel=%s %dpx %s) → final.mp4",
                args.brand, args.logo_size, args.logo_pos)
    final = lib.apply_branding(main_video, args.brand,
                                logo_size=args.logo_size,
                                logo_pos=args.logo_pos)

    # Update calendar
    scene_ids_path = ep_dir / "scene_ids.json"
    project_id = None
    if scene_ids_path.exists():
        import json
        project_id = json.loads(scene_ids_path.read_text()).get("project_id")

    lib.update_episode(
        args.book_slug, args.ep_id,
        status="done",
        video_path=f"{ep_dir.name}/final.mp4",
        project_id=project_id,
        rendered_at=datetime.now().isoformat(timespec="seconds"),
    )

    logger.info("✓ DONE: %s (%s)", final, caption)
    return 0


if __name__ == "__main__":
    sys.exit(main())
