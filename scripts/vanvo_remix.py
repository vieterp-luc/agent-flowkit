#!/usr/bin/env python3
"""Re-render a Van Vo book WITHOUT regenerating images.

Use this when you only changed narrator text in vanvo_books_data.py and want
to refresh TTS + Ken Burns + concat + thumbnail + caption — but reuse existing
scene images (which are expensive to regen + may trigger reCAPTCHA).

Usage:
    python vanvo_remix.py thach-sanh          # re-TTS all scenes + remix
    python vanvo_remix.py tam-cam 7,11        # re-TTS only scene 7 + 11, rest reuses cached TTS
    python vanvo_remix.py thach-sanh all      # force re-TTS all (default)

Scene indices:
    0 = intro
    1+ = body scenes from book["scripts"]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vanvo_books_data import BOOKS
from vanvo_render_pipeline import (
    OUTPUT_BASE, INTRO_NARR, TTS_VOICE, TTS_SPEED, api_post,
    gen_ken_burns_clips, concat_clips, build_narrator, mix_final,
    build_thumbnail, write_caption, ffprobe_dur,
)


def remix_book(slug: str, scenes_to_regen_tts: list[int] | None = None) -> None:
    if slug not in BOOKS:
        print(f"Unknown book: {slug}. Available: {list(BOOKS.keys())}")
        sys.exit(1)

    book = BOOKS[slug]
    ep = OUTPUT_BASE / slug / "ep01"
    tts_dir = ep / "tts"
    img_dir = ep / "images"

    if not img_dir.exists() or not list(img_dir.glob("scene_*.png")):
        print(f"❌ No images found for {slug} at {img_dir}")
        print("   Run full pipeline first: python vanvo_render_pipeline.py", slug)
        sys.exit(1)

    narrators = [INTRO_NARR] + book["scripts"]
    total = len(narrators)

    if scenes_to_regen_tts is None:
        scenes_to_regen_tts = list(range(total))

    print(f"📝 {book['title']} — re-TTS scenes: {scenes_to_regen_tts}")
    for n in scenes_to_regen_tts:
        if n >= total:
            print(f"  ⚠️ scene_{n:02d} out of range (max {total-1}) — skip")
            continue
        wav = tts_dir / f"scene_{n:02d}.wav"
        wav.unlink(missing_ok=True)
        text = narrators[n]
        payload = {"template": TTS_VOICE, "speed": TTS_SPEED,
                   "output_path": str(wav), "text": text}
        api_post("/api/tts/generate", payload, timeout=600)
        print(f"  scene_{n:02d}: re-TTS ok ({len(text.split())} từ)")

    print("\n🎬 Re-render: Ken Burns + concat + narrator + mix + thumbnail + caption...")
    gen_ken_burns_clips(ep, book["motions"])
    video = concat_clips(ep)
    narrator = build_narrator(ep)
    final = mix_final(ep, video, narrator)
    build_thumbnail(ep, book)
    write_caption(ep, book)

    dur = ffprobe_dur(final)
    size_mb = final.stat().st_size / 1024 / 1024
    print(f"\n✅ {final}")
    print(f"   {size_mb:.1f}MB / {dur:.0f}s ({dur/60:.1f}min)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    slug = sys.argv[1]
    scenes = None
    if len(sys.argv) > 2 and sys.argv[2] != "all":
        scenes = [int(x.strip()) for x in sys.argv[2].split(",")]
    remix_book(slug, scenes)


if __name__ == "__main__":
    main()
