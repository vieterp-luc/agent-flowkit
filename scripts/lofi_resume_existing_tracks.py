"""One-off: complete lofi pipeline using existing tracks (skip music gen).

Reads tracks from <run_dir>/music/, runs concat → loop → mix → image → ken-burns → combine.
"""
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.services.lofi_pipeline import (
    load_preset,
    _concat_music,
    _loop_audio,
    _mix_with_ambience,
    _resolve_ambience_files,
    _generate_image,
    _image_to_kenburns,
    _combine_av,
    _build_youtube_meta,
)


async def main(run_dir: Path, preset_id: str, duration_min: int) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    preset = load_preset(preset_id)
    target_sec = duration_min * 60
    music_dir = run_dir / "music"
    tracks = sorted(music_dir.glob("track_*.mp4"))
    if len(tracks) < 2:
        print(f"✗ need >= 2 tracks in {music_dir}, found {len(tracks)}")
        return 1
    print(f"→ Using {len(tracks)} tracks: {[t.name for t in tracks]}")

    breakdown: dict = {}
    t0 = time.time()
    concat_block = _concat_music(tracks, run_dir / "concat_music.mp3")
    looped = _loop_audio(concat_block, target_sec, run_dir / "looped_music.mp3")
    ambience_paths = _resolve_ambience_files(preset.get("ambience", []))
    mixed = _mix_with_ambience(
        looped, ambience_paths, run_dir / "mixed_audio.mp3",
        music_vol=preset.get("music_volume", 0.75),
        amb_vol=preset.get("ambience_volume", 0.25),
    )
    breakdown["audio_post_sec"] = round(time.time() - t0, 1)

    t0 = time.time()
    image_path = run_dir / "visual.png"
    if not image_path.exists():
        await _generate_image(preset["image_prompt"], "lofi-shared", image_path)
    breakdown["image_gen_sec"] = round(time.time() - t0, 1)

    t0 = time.time()
    kenburns = _image_to_kenburns(image_path, target_sec, run_dir / "ken_burns.mp4")
    breakdown["kenburns_sec"] = round(time.time() - t0, 1)

    t0 = time.time()
    final = _combine_av(kenburns, mixed, run_dir / "final.mp4")
    breakdown["combine_sec"] = round(time.time() - t0, 1)

    yt_meta = _build_youtube_meta(preset, duration_min)
    meta_path = run_dir / "youtube_meta.json"
    meta_path.write_text(json.dumps(yt_meta, indent=2, ensure_ascii=False))

    breakdown["total_sec"] = round(sum(v for v in breakdown.values()), 1)
    print(f"\n✓ Done: {final}")
    print(f"  meta: {meta_path}")
    print(f"  breakdown: {breakdown}")
    return 0


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", type=Path)
    p.add_argument("--preset", required=True)
    p.add_argument("--duration", type=int, required=True, help="minutes")
    a = p.parse_args()
    sys.exit(asyncio.run(main(a.run_dir, a.preset, a.duration)))
