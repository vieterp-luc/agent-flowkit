"""One-off: finish ep4 (tiny_mini_elephant) — regen the 4 missing scene images (3-6),
download, Meta video for them, then re-assemble the full 7-scene reel with elephant_calm.

Run AFTER switching to a Flow account with fresh image quota.
    python3 scripts/tiny_finish_ep4.py
"""
import json
import os
import time
import urllib.request

import meta_video_batch
import tiny_assemble

BASE = "http://127.0.0.1:8100"
PID = "53317d4e-58d8-4995-b84f-a6514a7852c5"
VID = "9054ce6f-6e92-4ec4-ac4d-24f20a1dec12"
SLUG = "tiny_animals/tiny_mini_elephant"
MUSIC = "output/tiny_animals/_bgm/elephant_calm.mp3"


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=30).read())


def main():
    scenes = sorted(get(f"/api/scenes?video_id={VID}"), key=lambda s: s["display_order"])
    missing = [s for s in scenes if s.get("vertical_image_status") != "COMPLETED"]
    ids = [s["id"] for s in missing]
    print(f"missing images: {[s['display_order'] for s in missing]}")
    if ids:
        post("/api/requests/batch", {"requests": [
            {"type": "GENERATE_IMAGE", "scene_id": i, "project_id": PID,
             "video_id": VID, "orientation": "VERTICAL"} for i in ids]})
        for _ in range(30):
            time.sleep(15)
            if get(f"/api/requests/batch-status?video_id={VID}&type=GENERATE_IMAGE").get("done"):
                break
    # download all completed images
    outdir = f"output/{SLUG}/img"
    os.makedirs(outdir, exist_ok=True)
    scenes = sorted(get(f"/api/scenes?video_id={VID}"), key=lambda s: s["display_order"])
    got = 0
    for s in scenes:
        url = s.get("vertical_image_url")
        if url and s.get("vertical_image_status") == "COMPLETED":
            try:
                urllib.request.urlretrieve(url, f"{outdir}/scene_{s['display_order']:02d}.jpg")
                got += 1
            except Exception as ex:
                print(f"  dl fail s{s['display_order']}: {ex}")
    print(f"images now: {got}/7")
    # Meta video (skips existing clips 0-2, does the new ones) then re-assemble full 7
    meta_video_batch.main(VID, SLUG)
    tiny_assemble.main(SLUG, MUSIC)
    print("=== ep4 FINISH DONE ===")


if __name__ == "__main__":
    main()
