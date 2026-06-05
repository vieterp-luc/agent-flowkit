"""Compose Jekyll & Hyde ep1 YouTube thumbnail locally.

Per Frankenstein post-mortem: painterly oil thumbnails failed visibility
test. Switch to YT convention — FACE HUGE + 2-3 word hook + dark contrast.

Uses scene_03 (Utterson + Lanyon dinner confrontation — strongest character
faces in ep1) as base, crop to faces, overlay bold hook.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

EP = Path("/Users/vieterp/code/Research/agent-flowkit/output/"
          "jekyll_hyde_classics_en/ep01_story_of_the_door")

# scene_03 = Lanyon + Utterson dinner (Sargent style, strong faces)
# scene_04 = Utterson + Hyde confrontation in fog (the iconic showdown)
SRC = EP / "images" / "scene_04.png"
OUT_YT = EP / "thumbnails" / "thumbnail_ep01_yt.png"
OUT_FULL = EP / "thumbnails" / "thumbnail_ep01.png"
OUT_YT.parent.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
LINE1 = "WHO IS HE?"
LINE2 = "JEKYLL & HYDE  —  CHAPTERS 1-3"

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

# Load + cover-crop. Bias crop to left side (Hyde silhouette + Utterson visible).
img = Image.open(SRC).convert("RGB")
src_ratio = img.width / img.height
tgt_ratio = W / H
if src_ratio > tgt_ratio:
    new_h = img.height
    new_w = int(new_h * tgt_ratio)
    # Slightly favour center-left
    left = int((img.width - new_w) * 0.4)
    img = img.crop((left, 0, left + new_w, new_h))
else:
    new_w = img.width
    new_h = int(new_w / tgt_ratio)
    top = (img.height - new_h) // 2
    img = img.crop((0, top, new_w, top + new_h))
img = img.resize((W, H), Image.LANCZOS)

# Boost contrast subtly via S-curve overlay
darken = Image.new("RGB", (W, H), (0, 0, 0))
mask = Image.new("L", (1, H), 0)
for y in range(H):
    if y < 240:
        v = int(180 * (1 - y / 240))
    elif y > H - 240:
        v = int(180 * ((y - (H - 240)) / 240))
    else:
        v = 0
    mask.putpixel((0, y), v)
mask = mask.resize((W, H))
img = Image.composite(darken, img, mask)

draw = ImageDraw.Draw(img)


def stroke_text(draw, xy, text, font, fill, outline_color, outline_w):
    x, y = xy
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text(xy, text, font=font, fill=fill)


# LINE 1 — HUGE
size1 = 170
f1 = ImageFont.truetype(IMPACT, size1)
while draw.textbbox((0, 0), LINE1, font=f1)[2] > W * 0.85:
    size1 -= 4
    f1 = ImageFont.truetype(IMPACT, size1)
bb1 = draw.textbbox((0, 0), LINE1, font=f1)
tw1, th1 = bb1[2] - bb1[0], bb1[3] - bb1[1]
x1 = (W - tw1) // 2
y1 = 30

# Drop shadow
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.text((x1 + 8, y1 + 10), LINE1, font=f1, fill=(0, 0, 0, 220))
shadow = shadow.filter(ImageFilter.GaussianBlur(8))
img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
draw = ImageDraw.Draw(img)

stroke_text(draw, (x1, y1), LINE1, f1,
            fill=(255, 215, 0), outline_color=(120, 10, 10), outline_w=6)

# LINE 2 — smaller serif
size2 = 50
f2 = ImageFont.truetype(SERIF_BOLD, size2)
while draw.textbbox((0, 0), LINE2, font=f2)[2] > W * 0.82:
    size2 -= 2
    f2 = ImageFont.truetype(SERIF_BOLD, size2)
bb2 = draw.textbbox((0, 0), LINE2, font=f2)
x2 = (W - (bb2[2] - bb2[0])) // 2
y2 = H - 100

shadow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd2 = ImageDraw.Draw(shadow2)
sd2.text((x2 + 3, y2 + 5), LINE2, font=f2, fill=(0, 0, 0, 200))
shadow2 = shadow2.filter(ImageFilter.GaussianBlur(4))
img = Image.alpha_composite(img.convert("RGBA"), shadow2).convert("RGB")
draw = ImageDraw.Draw(img)

stroke_text(draw, (x2, y2), LINE2, f2,
            fill=(245, 235, 215), outline_color=(40, 25, 15), outline_w=2)

img.save(OUT_YT, "PNG", optimize=True)
img.save(OUT_FULL, "PNG", optimize=True)
print(f"OK -> {OUT_YT} ({OUT_YT.stat().st_size // 1024} KB)")
