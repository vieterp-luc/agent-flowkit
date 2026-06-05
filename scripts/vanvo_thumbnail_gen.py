#!/usr/bin/env python3
"""Generate YouTube thumbnail (Pixar style, framework v1.0) for a Văn Vở book.

One Imagen-4 call bakes logo + title + 4-zone composition into a single image.
Reuses the book's Flow project + character ref images for consistency with video.

Usage:
    python scripts/vanvo_thumbnail_gen.py <slug> [--title "OVERRIDE TITLE"]

Pre-req: book has rendered ep01 (its `_project.json` exists with pid + entity_cids).

Each book may declare an optional `thumbnail` dict to customize the prompt:
    BOOK["thumbnail"] = {
        "pose":        "<hero pose + key gesture>",
        "mystery":     "<mystery object glowing in foreground>",
        "proof":       "<setting that proves story is real>",
        "mini_scenes": "1) <scene a>, 2) <scene b>, 3) <scene c>, 4) <scene d>",
        "subtitle":    "<optional ribbon sub-title>",
    }

If `thumbnail` is missing, sensible defaults are derived from caption_bullets +
entities, with a warning to add an explicit block for higher quality.

Output: `output/van_vo/<slug>/ep01/thumbnail_branded.png` (16:9 landscape).
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vanvo_books_data import BOOKS
from vanvo_render_pipeline import API, OUTPUT_BASE, api_get, api_post


def _entity_descriptor(book: dict, name: str) -> str:
    """Return the short visual descriptor for an entity name, stripped of the leading 'name (' wrapper."""
    for ent in book.get("entities", []):
        if ent["name"] == name:
            return ent["image_prompt"]
    return ""


def _derive_defaults(book: dict) -> dict:
    """Heuristic defaults when book has no `thumbnail` block — uses caption_bullets."""
    bullets = book.get("caption_bullets", [])
    mini = " | ".join(bullets[:4]) if bullets else "key story moments from the tale"
    return {
        "pose": "standing confidently center-frame with strong emotional reaction, looking directly at camera, golden halo and rim light",
        "mystery": "a magical glowing object central to the story foreground",
        "proof": "ancient Vietnamese setting matching the tale",
        "mini_scenes": mini,
        "subtitle": "",
    }


def _split_title_two_lines(title: str) -> tuple[str, str]:
    """Split a title into two near-equal lines on a word boundary for the 3D headline."""
    words = title.upper().split()
    if len(words) <= 1:
        return title.upper(), ""
    if len(words) == 2:
        return words[0], words[1]
    # Split so first line is shorter or equal in char count
    half = len(words) // 2
    return " ".join(words[:half]), " ".join(words[half:])


def compose_prompt(book: dict, title: str) -> str:
    entities = book.get("entities", [])
    if not entities:
        raise ValueError(f"Book {book['slug']!r} has no entities — needed for HERO descriptor.")

    hero = entities[0]
    hero_desc = hero["image_prompt"]
    reaction_descs = " AND ".join(e["image_prompt"] for e in entities[1:3]) or "an awestruck supporting character with shocked expression"

    cfg = {**_derive_defaults(book), **book.get("thumbnail", {})}
    line1, line2 = _split_title_two_lines(title)
    title_text = f'"{line1}" and "{line2}"' if line2 else f'"{line1}"'
    title_lines_clause = (
        f"on two stacked lines, line 1 reads exactly \"{line1}\" and line 2 below reads exactly \"{line2}\""
        if line2
        else f"on one line reading exactly \"{line1}\""
    )

    subtitle_clause = ""
    if cfg.get("subtitle"):
        subtitle_clause = (
            f"\n\nOPTIONAL RIBBON BOTTOM: a curled red scroll ribbon with small gold text reading exactly "
            f"\"{cfg['subtitle']}\", placed centered along the bottom edge."
        )

    return f"""Cinematic 3D Pixar Disney YouTube thumbnail for the Vietnamese fairy tale series Cổ Tích Gen Z.

HERO CENTER (60% of frame): {hero_desc}, {cfg['pose']}, HUGE expressive eyes looking at camera, golden rim light and halo glow, bright sunburst behind, heroic.

REACTION (top-right): {reaction_descs}, mouth wide open in shocked disbelief, exaggerated cartoonish reaction.

MYSTERY (foreground bottom-center): {cfg['mystery']}, glowing softly with magical sparkle particles.

PROOF / BACKGROUND: {cfg['proof']}, swirling deep magenta-purple clouds, ancient Vietnamese atmosphere.

4 SMALL CIRCULAR MINI PANELS around the hero edges depicting: {cfg['mini_scenes']}. Each panel is a small comic-style circular vignette, easy to read in 1 second, strong contrast.

TEXT MUST APPEAR EXACTLY AS WRITTEN BELOW with correct Vietnamese diacritics, crisp and legible:

LOGO TOP-LEFT CORNER: a rounded glowing neon light-purple display logo on two stacked lines, line 1 reads exactly "Cổ Tích" smaller, line 2 reads exactly "GEN Z" larger and bolder, white inner stroke and soft purple-pink neon glow halo, framed in a soft rounded glowing frame.

MAIN TITLE LEFT-MIDDLE: a huge 3D extruded chunky gold-yellow display title {title_lines_clause}, very thick black outline, dramatic dark shadow extruding down-right, extremely bold heavy block letters with strong 3D depth, fills about 30 percent of the left side of the frame.{subtitle_clause}

STYLE: cinematic 3D Pixar Disney painterly, hyper-detailed faces with big emotive eyes, ultra detailed textures, vibrant warm amber + gold + magenta-purple palette, neon glow accents, fantasy storybook.

LIGHTING: god rays from above, warm golden aura on hero, magical sparkle particles, dramatic rim light, deep magenta-purple shadow background.

COMPOSITION: 16:9 horizontal landscape. Logo top-left, main title left-middle, hero center, reaction top-right, mystery foreground, mini panels scattered. Background DARK + subjects BRIGHTLY lit, strong contrast. Sharp focus on hero face.

High CTR YouTube thumbnail, ancient Vietnamese fairy tale, all text rendered in correct Vietnamese spelling."""


def gen_thumbnail(slug: str, title_override: str | None = None) -> Path:
    if slug not in BOOKS:
        raise SystemExit(f"Unknown book: {slug}. Available: {list(BOOKS.keys())}")
    book = BOOKS[slug]

    ep_dir = OUTPUT_BASE / slug / "ep01"
    project_meta = ep_dir / "_project.json"
    if not project_meta.exists():
        raise SystemExit(
            f"No _project.json at {project_meta} — render the book first via "
            f"`python scripts/vanvo_render_pipeline.py {slug}`."
        )
    meta = json.loads(project_meta.read_text())
    pid = meta["pid"]

    # Fetch character media_ids fresh from Flow (in case refs were regenerated)
    chars = api_get(f"/api/projects/{pid}/characters")
    name_to_mid = {c["name"]: c.get("media_id") for c in chars}
    media_ids = [mid for mid in name_to_mid.values() if mid]

    if "thumbnail" not in book:
        print(f"⚠️  Book {slug} has no `thumbnail` block — using defaults derived from caption_bullets.")
        print("    For higher-quality thumbnails, add a `thumbnail` dict to the book (see script docstring).")

    title = title_override or book["title"]
    prompt = compose_prompt(book, title)

    print(f"🎨 Generating thumbnail for {book['title']} ({len(media_ids)} char refs)...")
    payload = {
        "prompt": prompt,
        "project_id": pid,
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "character_media_ids": media_ids,
    }
    result = api_post("/api/flow/generate-image", payload, timeout=180)
    url = result["media"][0]["image"]["generatedImage"]["fifeUrl"]

    out = ep_dir / "thumbnail_branded.png"
    urllib.request.urlretrieve(url, out)
    size_kb = out.stat().st_size / 1024
    print(f"✅ {out} ({size_kb:.0f}KB)")
    return out


def main():
    ap = argparse.ArgumentParser(description="Generate Pixar-style YouTube thumbnail for a Văn Vở book.")
    ap.add_argument("slug", help="Book slug (e.g. coc-kien-troi)")
    ap.add_argument("--title", default=None, help="Override the title text rendered on the thumbnail")
    args = ap.parse_args()
    gen_thumbnail(args.slug, args.title)


if __name__ == "__main__":
    main()
