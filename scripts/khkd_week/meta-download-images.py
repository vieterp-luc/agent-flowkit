#!/usr/bin/env python3
"""Download Flow scene images for a project to local img/scene_NN.jpg (2-digit padded).

Usage: meta-download-images.py <slug>
Reads output/<slug>/ids.json for video_id, queries /api/scenes, downloads each
scene's vertical_image_url to output/<slug>/img/scene_NN.jpg.
"""
import json
import os
import sys
import urllib.request

BASE = "http://127.0.0.1:8100"


def get_scenes(video_id: str) -> list:
    with urllib.request.urlopen(f"{BASE}/api/scenes?video_id={video_id}", timeout=30) as r:
        return json.loads(r.read())


def main(slug: str) -> None:
    outdir = f"output/{slug}"
    ids = json.load(open(f"{outdir}/ids.json", encoding="utf-8"))
    img_dir = f"{outdir}/img"
    os.makedirs(img_dir, exist_ok=True)

    scenes = sorted(get_scenes(ids["video_id"]), key=lambda s: s["display_order"])
    for s in scenes:
        idx = f"{s['display_order']:02d}"
        dst = f"{img_dir}/scene_{idx}.jpg"
        if os.path.exists(dst):
            print(f"[skip] scene_{idx}.jpg exists")
            continue
        url = s.get("vertical_image_url")
        if not url:
            print(f"[warn] scene_{idx}: no vertical_image_url (gen not done?)")
            continue
        print(f"[dl] scene_{idx} ...")
        urllib.request.urlretrieve(url, dst)
        print(f"[ok] scene_{idx}.jpg ({os.path.getsize(dst)//1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1])
