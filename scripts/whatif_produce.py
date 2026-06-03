"""Orchestrate the 'Nếu... thì sao' series: for each day, create project + 7 scenes,
gen Flow images, Meta image→video, and assemble — sequentially, continue-on-error.

Run (detached): python scripts/whatif_produce.py day2 day3 day4 day5 day6 day7
Progress → output/_shared/whatif_run.log
"""
import json
import os
import sys
import time
import urllib.request

import meta_assemble
import meta_video_batch
from whatif_days import DAYS, STYLE

BASE = "http://127.0.0.1:8100"
LOG = "output/_shared/whatif_run.log"


def log(m):
    os.makedirs("output/_shared", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(m + "\n")
    print(m, flush=True)


def post(path, payload):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def patch(path, payload):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="PATCH")
    urllib.request.urlopen(req, timeout=20)


def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=30).read().decode())


def create_day(d):
    proj = post("/api/projects", {"name": d["title"], "description": d["title"],
                                  "story": d["story"], "material": "realistic"})
    pid = proj["id"]
    vid = post("/api/videos", {"project_id": pid, "title": d["title"],
               "video_story": "what-if 7 scene", "display_order": 0, "orientation": "VERTICAL"})["id"]
    for i, (narr, img_p, vid_p) in enumerate(d["scenes"]):
        s = post("/api/scenes", {"video_id": vid, "display_order": i,
                 "prompt": f"{img_p}. {STYLE}.", "video_prompt": vid_p,
                 "narrator_text": narr, "character_names": [], "chain_type": "ROOT"})
        patch(f"/api/scenes/{s['id']}", {"narrator_text": narr})
    return pid, vid


def gen_images(pid, vid, slug):
    outdir = f"output/{slug}/img"
    os.makedirs(outdir, exist_ok=True)
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    ids = [s["id"] for s in scenes]
    for batch in (ids[:4], ids[4:]):  # small batches → avoid reCAPTCHA
        reqs = [{"type": "GENERATE_IMAGE", "scene_id": i, "project_id": pid,
                 "video_id": vid, "orientation": "VERTICAL"} for i in batch]
        post("/api/requests/batch", {"requests": reqs})
        for _ in range(24):  # poll up to ~6 min
            time.sleep(15)
            st = get(f"/api/requests/batch-status?video_id={vid}&type=GENERATE_IMAGE")
            if st.get("done"):
                break
    # download whatever completed
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    got = 0
    for s in scenes:
        url = s.get("vertical_image_url")
        if url and s.get("vertical_image_status") == "COMPLETED":
            try:
                urllib.request.urlretrieve(url, f"{outdir}/scene_{s['display_order']:02d}.jpg")
                got += 1
            except Exception as e:
                log(f"  img dl fail s{s['display_order']}: {e}")
    return got


def main(keys):
    for k in keys:
        d = DAYS[k]
        slug = d["slug"]
        log(f"\n===== {k}: {d['title']} ({slug}) =====")
        try:
            pid, vid = create_day(d)
            log(f"  project {pid} video {vid}")
            n = gen_images(pid, vid, slug)
            log(f"  images: {n}/7")
            meta_video_batch.main(vid, slug)          # → clips/ (own log)
            meta_assemble.main(vid, slug)             # default Phong_Vien 0.9 + pause
            log(f"  ✓ {slug} DONE")
        except Exception as e:
            log(f"  ✗ {k} ERROR: {e}")
    log("\n===== ALL DAYS FINISHED =====")


if __name__ == "__main__":
    main(sys.argv[1:] or list(DAYS.keys()))
