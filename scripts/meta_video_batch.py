"""Generic Meta AI image→video batch driver for a Flow Kit video's scenes.

For each scene: POST /api/meta/browser/generate-video with output/<slug>/img/scene_NN.jpg
+ the scene's video_prompt → move the result mp4 to output/<slug>/clips/scene_NN.mp4.
Sequential (browser lock), ~30s gap, timeout 600. Skips scenes whose clip already exists,
so re-running retries only the missing ones. Run detached + poll output/<slug>/meta_gen.log.

Run: python scripts/meta_video_batch.py <video_id> <slug>
"""
import json
import os
import shutil
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8100"
GAP_S = 30


def main(vid, slug):
    out = f"output/{slug}"
    img, clips, log = f"{out}/img", f"{out}/clips", f"{out}/meta_gen.log"
    os.makedirs(clips, exist_ok=True)

    def logline(m):
        with open(log, "a") as f:
            f.write(m + "\n")
        print(m, flush=True)

    scenes = json.load(urllib.request.urlopen(f"{BASE}/api/scenes?video_id={vid}", timeout=30))
    scenes.sort(key=lambda s: s.get("display_order", 0))
    logline(f"=== START Meta image→video: {slug} ({len(scenes)} scenes) ===")
    ok = 0
    for s in scenes:
        n = s["display_order"]
        dest = f"{clips}/scene_{n:02d}.mp4"
        src_img = f"{img}/scene_{n:02d}.jpg"
        if os.path.exists(dest):
            logline(f"scene_{n:02d}: exists, skip"); ok += 1; continue
        if not os.path.exists(src_img):
            logline(f"scene_{n:02d}: IMAGE MISSING"); continue
        if ok or n > 0:
            time.sleep(GAP_S)
        prompt = (s.get("video_prompt") or s.get("prompt") or "").split("\n\nAudio")[0].strip()
        logline(f"scene_{n:02d}: generating…")
        payload = json.dumps({"prompt": prompt, "image_path": src_img,
                              "timeout": 600, "headless": True}).encode()
        req = urllib.request.Request(BASE + "/api/meta/browser/generate-video",
                                     data=payload, headers={"Content-Type": "application/json"})
        try:
            res = json.loads(urllib.request.urlopen(req, timeout=680).read().decode())
        except Exception as e:
            logline(f"scene_{n:02d}: REQUEST ERROR {e}"); continue
        if res.get("ok"):
            shutil.move(res["path"], dest)
            logline(f"scene_{n:02d}: OK → {dest} ({os.path.getsize(dest)//1024} KB)"); ok += 1
        else:
            logline(f"scene_{n:02d}: FAILED {res.get('error')}")
    logline(f"=== DONE {ok}/{len(scenes)} clips ===")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
