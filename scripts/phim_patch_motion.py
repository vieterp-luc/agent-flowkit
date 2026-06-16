"""PATCH each scene's video_prompt for a video, from a motions.json (list by display_order).

Used by /fk-phim Full-Meta-video mode: meta_video_batch.py reads video_prompt per scene.
motions.json = JSON array of simple motion strings, index == scene display_order.

Run: python3 scripts/phim_patch_motion.py <video_id> <motions.json>
"""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8100"


def patch(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="PATCH")
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def main(vid, mjson):
    motions = json.load(open(mjson, encoding="utf-8"))
    scenes = sorted(json.load(urllib.request.urlopen(f"{BASE}/api/scenes?video_id={vid}", timeout=30)),
                    key=lambda s: s.get("display_order", 0))
    n = 0
    for s in scenes:
        d = s.get("display_order", 0)
        if d < len(motions):
            patch(f"/api/scenes/{s['id']}", {"video_prompt": motions[d]})
            n += 1
    print(f"patched video_prompt on {n}/{len(scenes)} scenes")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
