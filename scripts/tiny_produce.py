"""Orchestrate the tiny-animal ASMR series: per episode create project + 7 scenes (no
narrator), gen Flow images, Meta image→video, then music-backed assemble. Continue-on-error.

Run (detached): python scripts/tiny_produce.py ep1 ep2 ep3 ep4
Progress → output/tiny_animals/tiny_run.log ; music → output/tiny_animals/_bgm/cozy.mp3
"""
import json
import os
import sys
import time
import urllib.request

import meta_video_batch
import tiny_assemble
from tiny_days import EPISODES, STYLE

# Merge extra episodes (distinct story arcs) if present
try:
    from tiny_days_more import EPISODES_MORE
    EPISODES.update(EPISODES_MORE)
except ImportError:
    pass
try:
    from tiny_days_batch3 import EPISODES_B3
    EPISODES.update(EPISODES_B3)
except ImportError:
    pass
try:
    from tiny_days_batch4 import EPISODES_B4
    EPISODES.update(EPISODES_B4)
except ImportError:
    pass

BASE = "http://127.0.0.1:8100"
LOG = "output/tiny_animals/tiny_run.log"
MUSIC = "output/tiny_animals/_bgm/cozy_playful.mp3"


def log(m):
    os.makedirs("output/tiny_animals", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(m + "\n")
    print(m, flush=True)


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload, ensure_ascii=False).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=30).read())


def create_entity_ref(pid, entity):
    """Create 1 Flow character + link to project + gen its reference image (paced).

    The ref image locks the main animal's appearance so it stays consistent across all
    7 scenes. Returns the entity name (for scene character_names), or None if ref gen
    failed/timed out (scenes then fall back to prompt-only).
    """
    cid = post("/api/characters", entity)["id"]
    post(f"/api/projects/{pid}/characters/{cid}", {})
    rid = post("/api/requests", {"type": "GENERATE_CHARACTER_IMAGE",
                                 "character_id": cid, "project_id": pid})["id"]
    start = time.time()
    while time.time() - start < 240:
        r = get(f"/api/requests/{rid}")
        if r["status"] == "COMPLETED":
            log(f"  entity ref ok: {entity['name']}")
            return entity["name"]
        if r["status"] == "FAILED":
            log(f"  ⚠ entity ref FAILED ({r.get('error_message','')[:50]}) — fallback prompt-only")
            return None
        time.sleep(5)
    log("  ⚠ entity ref timeout — fallback prompt-only")
    return None


def create_episode(e):
    proj = post("/api/projects", {"name": e["title"], "description": e["title"],
                                  "story": e["title"], "material": "realistic"})
    pid = proj["id"]
    vid = post("/api/videos", {"project_id": pid, "title": e["title"],
               "video_story": "tiny animal asmr", "display_order": 0, "orientation": "VERTICAL"})["id"]
    # Main-character consistency: ref image attached to every scene via character_names
    char_name = create_entity_ref(pid, e["entity"]) if e.get("entity") else None
    cnames = [char_name] if char_name else []
    for i, (img_p, vid_p) in enumerate(e["scenes"]):
        post("/api/scenes", {"video_id": vid, "display_order": i,
             "prompt": f"{img_p}. {STYLE}.", "video_prompt": vid_p,
             "character_names": cnames, "chain_type": "ROOT"})
    return pid, vid


PACE_S = 12  # gap between image submits — Flow throttles bursts with API_429 ("tạo quá nhanh")


def gen_images(pid, vid, slug):
    """Gen scene images ONE AT A TIME with a pause between each — Flow rate-limits
    bursts (batch-of-N or back-to-back) with API_429. Submit one, wait until it
    settles, sleep PACE_S, then the next. Returns count of images on disk."""
    outdir = f"output/{slug}/img"
    os.makedirs(outdir, exist_ok=True)
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    for idx, s in enumerate(scenes):
        rid = post("/api/requests", {"type": "GENERATE_IMAGE", "scene_id": s["id"],
                   "project_id": pid, "video_id": vid, "orientation": "VERTICAL"})["id"]
        for _ in range(24):  # up to ~6 min/image
            time.sleep(15)
            st = get(f"/api/requests/{rid}").get("status")
            if st in ("COMPLETED", "FAILED"):
                if st == "FAILED":
                    err = get(f"/api/requests/{rid}").get("error_message", "")
                    log(f"  img s{s['display_order']} FAILED: {err[:50]}")
                break
        if idx < len(scenes) - 1:
            time.sleep(PACE_S)  # cool-down between submits
    # download all completed
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    got = 0
    for s in scenes:
        url = s.get("vertical_image_url")
        if url and s.get("vertical_image_status") == "COMPLETED":
            try:
                urllib.request.urlretrieve(url, f"{outdir}/scene_{s['display_order']:02d}.jpg")
                got += 1
            except Exception as ex:
                log(f"  img dl fail s{s['display_order']}: {ex}")
    return got


def main(keys):
    for k in keys:
        e = EPISODES[k]
        slug = f"tiny_animals/{e['slug']}"
        log(f"\n===== {k}: {e['title']} ({e['kind']}) → output/{slug} =====")
        try:
            pid, vid = create_episode(e)
            log(f"  project {pid} video {vid}")
            n = gen_images(pid, vid, slug)
            log(f"  images: {n}/{len(e['scenes'])}")
            if n == 0:
                log(f"  ⚠ HALT — {k} got 0 images (Flow quota likely hit). "
                    "Switch account + re-run remaining episodes.")
                break
            meta_video_batch.main(vid, slug)
            # Per-episode music if defined + file exists, else shared default
            ep_music = e.get("music")
            music = ep_music if (ep_music and os.path.exists(ep_music)) else MUSIC
            if ep_music and music != ep_music:
                log(f"  ⚠ music {ep_music} missing — fallback {MUSIC}")
            tiny_assemble.main(slug, music)
            log(f"  ✓ {slug} DONE (music={os.path.basename(music)})")
        except (Exception, SystemExit) as ex:
            log(f"  ✗ {k} ERROR: {ex}")
    log("\n===== ALL EPISODES FINISHED =====")


if __name__ == "__main__":
    main(sys.argv[1:] or list(EPISODES.keys()))
