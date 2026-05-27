"""Render YouTube Shorts feeders from Lamplit Library Frankenstein episodes.

For each (ep, section), produce a 1080x1920 vertical Short:
- Scene image cover-cropped to 1080x1920 + slow Ken Burns zoom-in
- Hook text panel (top, visible 0-3.5s, fade out)
- Narrator TTS with 1.5s lead silence (visual hook beat)
- CTA text panel (bottom, fade in last 4.5s)
- Soft vignette + film grain feel via subtle gradient overlay

Output: output/frankenstein_classics_en/shorts/short_ep{NN}.mp4
"""
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path("/Users/vieterp/code/Research/agent-flowkit")
EP_ROOT = ROOT / "output/frankenstein_classics_en"
OUT_DIR = EP_ROOT / "shorts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30
LEAD_SEC = 1.5
TAIL_SEC = 4.0

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"

# Per-Short config: (ep_dir, scene_idx, tts_filename, hook_line1, hook_line2,
#                    ep_number, chapter_title, sub_label)
SHORTS = [
    {
        "ep": 9, "slug": "ep09_justines_trial",
        "scene": "scene_04.png",
        "tts": "04_sum_4.wav",
        "hook1": "AN INNOCENT",
        "hook2": "CONDEMNED",
        "ep_label": "FRANKENSTEIN · EPISODE 9",
        "section_label": "JUSTINE'S TRIAL",
    },
    {
        "ep": 11, "slug": "ep11_creature_on_glacier",
        "scene": "scene_02.png",
        "tts": "02_sum_2.wav",
        "hook1": "THE MONSTER",
        "hook2": "RETURNS",
        "ep_label": "FRANKENSTEIN · EPISODE 11",
        "section_label": "SEA OF ICE",
    },
    {
        "ep": 12, "slug": "ep12_creatures_tale_begins",
        "scene": "scene_05.png",
        "tts": "05_sum_5.wav",
        "hook1": "BORN INTO",
        "hook2": "A CRUEL WORLD",
        "ep_label": "FRANKENSTEIN · EPISODE 12",
        "section_label": "FIRST REJECTION",
    },
]


def build_hook_overlay(line1: str, line2: str) -> Path:
    """Top hook overlay PNG with semi-transparent dark band + 2-line text."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Top dark band 0..480
    band = Image.new("RGBA", (W, 540), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(540):
        a = int(220 * (1 - max(0, y - 380) / 160)) if y >= 380 else 220
        bd.line([(0, y), (W, y)], fill=(8, 5, 3, a))
    img.alpha_composite(band, (0, 0))

    # Line 1 — Impact, huge yellow with crimson outline
    size1 = 180
    f1 = ImageFont.truetype(IMPACT, size1)
    while True:
        bbox = draw.textbbox((0, 0), line1, font=f1)
        if bbox[2] - bbox[0] <= W * 0.92:
            break
        size1 -= 4
        f1 = ImageFont.truetype(IMPACT, size1)
    bb1 = draw.textbbox((0, 0), line1, font=f1)
    x1 = (W - (bb1[2] - bb1[0])) // 2
    y1 = 110

    # Line 2 — slightly smaller
    size2 = 180
    f2 = ImageFont.truetype(IMPACT, size2)
    while True:
        bbox = draw.textbbox((0, 0), line2, font=f2)
        if bbox[2] - bbox[0] <= W * 0.92:
            break
        size2 -= 4
        f2 = ImageFont.truetype(IMPACT, size2)
    bb2 = draw.textbbox((0, 0), line2, font=f2)
    x2 = (W - (bb2[2] - bb2[0])) // 2
    y2 = y1 + (bb1[3] - bb1[1]) + 30

    for text, x, y, font in [(line1, x1, y1, f1), (line2, x2, y2, f2)]:
        # Crimson outline
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), text, font=font, fill=(140, 12, 12, 255))
        # Yellow fill
        draw.text((x, y), text, font=font, fill=(255, 215, 0, 255))

    out = Path(tempfile.mktemp(suffix=".png"))
    img.save(out, "PNG")
    return out


def build_cta_overlay(ep_label: str, section_label: str) -> Path:
    """Bottom CTA: section label + 'FULL CHAPTER ON LAMPLIT LIBRARY'."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Bottom dark band 1380..1920
    band = Image.new("RGBA", (W, 540), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(540):
        a = int(220 * (y / 160)) if y < 160 else 220
        bd.line([(0, y), (W, y)], fill=(8, 5, 3, a))
    img.alpha_composite(band, (0, H - 540))

    # Section label — Impact, white
    f_sect = ImageFont.truetype(IMPACT, 96)
    bb = draw.textbbox((0, 0), section_label, font=f_sect)
    x_sect = (W - (bb[2] - bb[0])) // 2
    y_sect = H - 480
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            if dx == 0 and dy == 0:
                continue
            draw.text((x_sect + dx, y_sect + dy), section_label,
                      font=f_sect, fill=(20, 12, 8, 255))
    draw.text((x_sect, y_sect), section_label, font=f_sect, fill=(245, 235, 210, 255))

    # Ep label — Georgia, smaller, antique gold
    f_ep = ImageFont.truetype(SERIF, 56)
    bb_ep = draw.textbbox((0, 0), ep_label, font=f_ep)
    x_ep = (W - (bb_ep[2] - bb_ep[0])) // 2
    y_ep = y_sect + (bb[3] - bb[1]) + 50
    draw.text((x_ep, y_ep), ep_label, font=f_ep, fill=(210, 175, 110, 255))

    # CTA line 1 + 2
    f_cta1 = ImageFont.truetype(SERIF_BOLD, 68)
    cta1 = ">>  WATCH FULL CHAPTER"
    bb1 = draw.textbbox((0, 0), cta1, font=f_cta1)
    x_c1 = (W - (bb1[2] - bb1[0])) // 2
    y_c1 = y_ep + 130
    draw.text((x_c1, y_c1), cta1, font=f_cta1, fill=(255, 215, 0, 255))

    f_cta2 = ImageFont.truetype(SERIF, 44)
    cta2 = "Lamplit Library  ·  Link in description"
    bb2 = draw.textbbox((0, 0), cta2, font=f_cta2)
    x_c2 = (W - (bb2[2] - bb2[0])) // 2
    y_c2 = y_c1 + 100
    draw.text((x_c2, y_c2), cta2, font=f_cta2, fill=(220, 210, 190, 255))

    out = Path(tempfile.mktemp(suffix=".png"))
    img.save(out, "PNG")
    return out


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def render_short(cfg: dict) -> Path:
    ep_dir = EP_ROOT / cfg["slug"]
    scene = ep_dir / "images" / cfg["scene"]
    tts = ep_dir / "tts" / cfg["tts"]
    out = OUT_DIR / f"short_ep{cfg['ep']:02d}.mp4"

    tts_dur = probe_duration(tts)
    total_dur = LEAD_SEC + tts_dur + TAIL_SEC
    print(f"  scene={scene.name} tts={tts_dur:.1f}s total={total_dur:.1f}s")

    hook_png = build_hook_overlay(cfg["hook1"], cfg["hook2"])
    cta_png = build_cta_overlay(cfg["ep_label"], cfg["section_label"])

    # Ken Burns: slow zoom-in over total_dur
    frames = int(total_dur * FPS)
    z_step = round(0.20 / frames, 6)  # zoom 1.0 -> ~1.20 over duration
    # Cover-fit scene to 1080x1920 before zoompan
    # Approach: pre-scale image to 1620x2880 (1.5x target), then zoompan to 1080x1920
    base_scale = "scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880"
    zoompan = (f"zoompan=z='min(zoom+{z_step},1.20)':d={frames}"
               f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")

    # Hook fade out at t=3.5s (1s fade)
    # CTA fade in at t=(total-TAIL_SEC)=total-4 (0.6s fade)
    hook_fade = "fade=t=out:st=3.0:d=1.0:alpha=1"
    cta_fade_in_start = max(0, tts_dur + LEAD_SEC - 0.5)
    cta_fade = f"fade=t=in:st={cta_fade_in_start:.2f}:d=0.6:alpha=1"

    filter_complex = (
        f"[0:v]{base_scale},{zoompan},format=yuv420p[bg];"
        f"[1:v]format=rgba,{hook_fade}[hook];"
        f"[2:v]format=rgba,{cta_fade}[cta];"
        f"[bg][hook]overlay=0:0:enable='between(t,0,5)'[v1];"
        f"[v1][cta]overlay=0:0:enable='gte(t,{cta_fade_in_start - 0.1:.2f})'[vout];"
        f"[3:a]adelay={int(LEAD_SEC*1000)}|{int(LEAD_SEC*1000)},apad=pad_dur={TAIL_SEC},"
        f"volume=1.4,dynaudnorm=g=15[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", f"{total_dur:.2f}", "-i", str(scene),
        "-loop", "1", "-t", f"{total_dur:.2f}", "-i", str(hook_png),
        "-loop", "1", "-t", f"{total_dur:.2f}", "-i", str(cta_png),
        "-i", str(tts),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-shortest",
        str(out),
    ]
    print(f"  rendering {out.name} ...")
    subprocess.run(cmd, capture_output=True, check=True)
    hook_png.unlink(missing_ok=True)
    cta_png.unlink(missing_ok=True)
    print(f"  ✓ {out} ({out.stat().st_size // 1024} KB)")
    return out


def main():
    print(f"Output dir: {OUT_DIR}")
    for cfg in SHORTS:
        print(f"\n=== ep{cfg['ep']} {cfg['section_label']} ===")
        render_short(cfg)
    print("\n--- ALL SHORTS RENDERED ---")
    for f in sorted(OUT_DIR.glob("short_ep*.mp4")):
        dur = probe_duration(f)
        print(f"  {f.name}: {dur:.1f}s  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
