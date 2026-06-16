"""Overlay the KHKD channel logo on finished v5 videos (bottom-right watermark).

Settings: 90x90 px, 12px padding, 90% opacity. Reads each video's *_final_*.mp4,
writes a sibling *_branded.mp4 (original preserved). Skips keys whose branded file
already exists.

Run: python scripts/khkd_brand.py [key1 key2 ...]   # no args → all v5 keys
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from khkd_v5_videos import VIDEOS

LOGO = "/Users/vieterp/Documents/khkd_video_logo.png"
SIZE, PAD, OPACITY = 90, 12, 0.9
# video #1 lives under the long auto-slug dir; the rest under their short keys
ALL = ["khoa_hoc_kinh_di_ong_dieu_hau_tarantula"] + list(VIDEOS)


def find_final(key):
    d = f"output/{key}"
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        if f.endswith(".mp4") and "_final_" in f and not f.endswith("_branded.mp4"):
            return f"{d}/{f}"
    return None


def brand(src):
    out = src.replace(".mp4", "_branded.mp4")
    flt = (f"[1:v]scale={SIZE}:{SIZE},format=rgba,colorchannelmixer=aa={OPACITY}[lg];"
           f"[0:v][lg]overlay=W-w-{PAD}:H-h-{PAD}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", LOGO,
                    "-filter_complex", flt, "-c:v", "libx264", "-preset", "medium",
                    "-crf", "18", "-c:a", "copy", out], check=True)
    return out


def main(keys):
    for key in keys:
        src = find_final(key)
        if not src:
            print(f"{key}: no final, skip"); continue
        out = src.replace(".mp4", "_branded.mp4")
        if os.path.exists(out):
            print(f"{key}: branded exists, skip"); continue
        brand(src)
        print(f"{key}: ✅ {os.path.basename(out)}")


if __name__ == "__main__":
    main(sys.argv[1:] or ALL)
