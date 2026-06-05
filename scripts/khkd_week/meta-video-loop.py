#!/usr/bin/env python3
"""Sequentially generate Meta image-to-video clips for each scene.

Usage: meta-video-loop.py <slug>
For each output/<slug>/img/scene_NN.jpg, calls /api/meta/browser/generate-video
with the matching scene's video_prompt, moves the returned file to
output/<slug>/clips/scene_NN.mp4. Skips scenes whose clip already exists.
30s gap between scenes (browser cooldown).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8100"
GAP_SECONDS = 30
META_TIMEOUT = 600
DUP_RETRIES = 2  # if downloaded clip md5 matches a prior clip, retry up to N times


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_scenes(video_id: str) -> list:
    with urllib.request.urlopen(f"{BASE}/api/scenes?video_id={video_id}", timeout=30) as r:
        return json.loads(r.read())


def gen_one(prompt: str, image_path: str) -> dict:
    payload = json.dumps({
        "prompt": prompt,
        "image_path": image_path,
        "timeout": META_TIMEOUT,
        "headless": True,
    })
    proc = subprocess.run(
        ["curl", "-s", "-m", str(META_TIMEOUT + 60),
         "-X", "POST", f"{BASE}/api/meta/browser/generate-video",
         "-H", "Content-Type: application/json", "-d", payload],
        capture_output=True, text=True,
    )
    stdout = (proc.stdout or "").strip()
    if not stdout:
        return {"ok": False, "error": f"empty response (curl exit={proc.returncode}, stderr={proc.stderr[:200]})"}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"non-JSON response: {stdout[:200]} ({e})"}


def main(slug: str) -> None:
    outdir = f"output/{slug}"
    ids = json.load(open(f"{outdir}/ids.json", encoding="utf-8"))
    clips_dir = f"{outdir}/clips"
    os.makedirs(clips_dir, exist_ok=True)

    # Seed md5 set with existing clips so retries can detect duplicates.
    seen_md5: dict[str, str] = {}
    for f in sorted(Path(clips_dir).glob("scene_*.mp4")):
        seen_md5[md5_of(str(f))] = f.name

    scenes = sorted(get_scenes(ids["video_id"]), key=lambda s: s["display_order"])

    for i, s in enumerate(scenes):
        idx = f"{s['display_order']:02d}"
        dst = f"{clips_dir}/scene_{idx}.mp4"
        if os.path.exists(dst):
            print(f"[skip] scene_{idx}.mp4 exists")
            continue
        img = f"{outdir}/img/scene_{idx}.jpg"
        if not os.path.exists(img):
            print(f"[warn] scene_{idx}: no image, skipping")
            continue
        prompt = (s.get("video_prompt") or "").strip()
        if not prompt:
            print(f"[warn] scene_{idx}: no video_prompt")
            continue

        # Try up to DUP_RETRIES+1 times in case Meta serves a duplicate of a
        # previous clip (race between page hydration + baseline capture).
        captured = False
        for attempt in range(DUP_RETRIES + 1):
            tag = "" if attempt == 0 else f" (retry {attempt}/{DUP_RETRIES})"
            print(f"[meta] scene_{idx} -> calling Meta ({META_TIMEOUT}s timeout){tag}...")
            result = gen_one(prompt, img)
            if not result.get("ok"):
                print(f"[ERR] scene_{idx}: {result}")
                break
            src = result["path"]
            digest = md5_of(src)
            if digest in seen_md5:
                print(f"[DUP] scene_{idx} matches {seen_md5[digest]} (md5={digest[:8]})")
                os.remove(src)
                if attempt < DUP_RETRIES:
                    print(f"[gap] sleeping {GAP_SECONDS}s before retry...")
                    time.sleep(GAP_SECONDS)
                    continue
                print(f"[GIVE-UP] scene_{idx}: duplicate after {DUP_RETRIES + 1} tries")
                break
            shutil.move(src, dst)
            seen_md5[digest] = os.path.basename(dst)
            kb = os.path.getsize(dst) // 1024
            print(f"[ok] scene_{idx}.mp4 ({kb} KB, md5={digest[:8]})")
            captured = True
            break

        if not captured:
            continue
        # Gap before next scene (unless this is the last one)
        if i < len(scenes) - 1:
            print(f"[gap] sleeping {GAP_SECONDS}s before next...")
            time.sleep(GAP_SECONDS)


if __name__ == "__main__":
    main(sys.argv[1])
