"""Generate the 8 per-episode BGM tracks for tiny-animals ep5-12 in ONE Gemini browser
session (start once, gen all, stop), then transcode each MP4 -> output/tiny_animals/_bgm/<name>.mp3.

Standalone process (not the server) so it can't hang the API. Run via venv:
    venv/bin/python scripts/tiny_gen_music.py
Skips tracks whose mp3 already exists.
"""
import asyncio
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.services.gemini_browser import GeminiBrowser, GeminiBrowserError

BGM = Path("output/tiny_animals/_bgm")

TRACKS = {
    "rescue_warmth": "tender warm lofi for a rescued animal slowly getting better, gentle hopeful piano and soft strings, comforting and healing, mellow wholesome, instrumental, seamless loop",
    "spa_serene": "serene spa lofi, soft gentle koto and calm warm pads, deeply relaxing zen, slow soothing wholesome, instrumental, seamless loop",
    "lullaby_night": "soft sleepy lullaby lofi, gentle music box and warm pads, dreamy starry night, very calm and soothing for sleep, instrumental, seamless loop",
    "rainy_window": "cozy rainy day lofi, mellow rhodes piano and soft vinyl warmth, calm and reflective, wholesome, instrumental, seamless loop",
    "kitchen_bake": "cheerful cozy kitchen lofi, light playful marimba and ukulele, warm baking vibe, wholesome gentle bounce, instrumental, seamless loop",
    "nest_build": "gentle uplifting lofi, soft plucky strings and warm bells, satisfying building progress, cozy wholesome, instrumental, seamless loop",
    "friends_play": "playful happy lofi, light pizzicato strings and glockenspiel, sweet friendship bounce, wholesome cheerful, instrumental, seamless loop",
    "festival_party": "warm festive lofi, gentle celebration bells and soft mellow brass, cozy birthday party joy, wholesome cheerful, instrumental, seamless loop",
}


def transcode(mp4: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-vn", "-ac", "2", "-ar", "48000",
                    "-b:a", "192k", str(dst)], check=True, capture_output=True)


async def main():
    logging.basicConfig(level=logging.WARNING)
    BGM.mkdir(parents=True, exist_ok=True)
    todo = {n: p for n, p in TRACKS.items() if not (BGM / f"{n}.mp3").exists()}
    print(f"gen {len(todo)}/{len(TRACKS)} tracks (skip {len(TRACKS)-len(todo)} existing)", flush=True)
    if not todo:
        return
    browser = GeminiBrowser(headless=True)
    await browser.start()
    try:
        for i, (name, prompt) in enumerate(todo.items(), 1):
            try:
                src = await browser.generate_music(prompt, timeout_s=300, model="Pro")
                transcode(src, BGM / f"{name}.mp3")
                print(f"  [{i}/{len(todo)}] ✓ {name}.mp3", flush=True)
            except (GeminiBrowserError, subprocess.CalledProcessError) as e:
                print(f"  [{i}/{len(todo)}] ✗ {name}: {e}", flush=True)
    finally:
        await browser.stop()
    print("=== MUSIC GEN DONE ===", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
