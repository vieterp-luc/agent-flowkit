"""Finish the incomplete Week-4 What-if videos: regen ONLY missing scene images per
existing video, download, Meta video (skips existing clips), TTS-assemble, logo.

Quota-safe: if a video can't reach 7 completed images (daily image quota hit), it halts
the whole run after saving partial progress — switch Flow account and re-run to continue.
Fewest-missing videos first so the most videos complete before quota runs out.

    python3 scripts/whatif_finish_week4.py
"""
import glob
import json
import os
import time
import urllib.request

import add_logo
import meta_assemble
import meta_video_batch

BASE = "http://127.0.0.1:8100"

# (slug, video_id) — remaining after account switch (3 done: nuoc_ngot, quay_nguoc, mo_di)
DATA = [
    ("neu_ngay_dai_48h", "7634aa0a-c96e-4a2c-9cef-e01431e9e8be"),
    ("neu_khi_quyen_day_gap_doi", "d75df938-feaf-475b-8852-f21adc5cff5e"),
]


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=30).read())


def gen_missing_images(vid, slug):
    """Submit GENERATE_IMAGE for non-COMPLETED scenes (chunks of 4), poll, download.
    Returns number of COMPLETED scene images on disk."""
    pid = get(f"/api/videos/{vid}").get("project_id")
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    missing = [s for s in scenes if s.get("vertical_image_status") != "COMPLETED"]
    print(f"  {slug}: missing {[s['display_order'] for s in missing]}", flush=True)
    ids = [s["id"] for s in missing]
    for i in range(0, len(ids), 4):
        chunk = ids[i:i + 4]
        post("/api/requests/batch", {"requests": [
            {"type": "GENERATE_IMAGE", "scene_id": s, "project_id": pid,
             "video_id": vid, "orientation": "VERTICAL"} for s in chunk]})
        for _ in range(30):
            time.sleep(15)
            if get(f"/api/requests/batch-status?video_id={vid}&type=GENERATE_IMAGE").get("done"):
                break
    # download completed
    outdir = f"output/whatif/{slug}/img"
    os.makedirs(outdir, exist_ok=True)
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    for s in scenes:
        dst = f"{outdir}/scene_{s['display_order']:02d}.jpg"
        if s.get("vertical_image_status") == "COMPLETED" and s.get("vertical_image_url") \
                and not os.path.exists(dst):
            try:
                urllib.request.urlretrieve(s["vertical_image_url"], dst)
            except Exception as ex:
                # Old-account image URLs 403 after switch, but the file usually already
                # exists on disk from the earlier run — that's fine.
                print(f"    dl skip s{s['display_order']} ({ex})", flush=True)
    # completion = images actually on disk (old completed scenes persist even if URL expired)
    return len(glob.glob(f"{outdir}/scene_*.jpg"))


def main():
    for slug, vid in DATA:
        print(f"\n===== {slug} =====", flush=True)
        n = gen_missing_images(vid, slug)
        print(f"  images: {n}/7", flush=True)
        if n < 7:
            print(f"  ⚠ HALT — {slug} only {n}/7 images (quota likely hit). "
                  "Switch Flow account + re-run to continue.", flush=True)
            break
        meta_video_batch.main(vid, f"whatif/{slug}")
        meta_assemble.main(vid, f"whatif/{slug}")
        final = f"output/whatif/{slug}/{slug}_final_Phong_Vien_TTS_09.mp4"
        if os.path.exists(final):
            add_logo.brand(final)
            print(f"  ✓ {slug} DONE + logo", flush=True)
        else:
            print(f"  ⚠ {slug}: assemble produced no final ({final})", flush=True)
    print("\n===== WEEK4 FINISH RUN DONE =====", flush=True)


if __name__ == "__main__":
    main()
