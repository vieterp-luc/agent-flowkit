"""3-scene TEST for option B: wholesome kids' content with a CLEARLY-ANIMATED (3D Pixar/CGI
cartoon, NOT photorealistic) toddler character — legitimate children's-animation style.

Safety: STYLE forces stylized cartoon (no photoreal minors). Entity ref keeps the character
consistent. Paced image gen (1-at-a-time +12s) to avoid Flow API_429.

Run: python3 scripts/kids_cartoon_test.py
"""
import json
import os
import time
import urllib.request

import meta_video_batch
import tiny_assemble

BASE = "http://127.0.0.1:8100"
SLUG = "kids_cartoon/playtime_test"
MUSIC = "output/tiny_animals/_bgm/spring_meadow.mp3"

STYLE = ("wholesome 3D animated children's cartoon, Pixar / Disney CGI style, soft rounded "
         "stylized character, bright cheerful colors, clearly animated NOT photorealistic, "
         "vertical 9:16, no text")

ENTITY = {"name": "cartoon toddler girl", "entity_type": "character",
          "image_prompt": ("an adorable 3D cartoon toddler girl about 3 years old, big round "
                           "expressive eyes, rosy cheeks, cute pigtails, simple colorful dress, "
                           "Pixar-style stylized character, wholesome, clearly animated cartoon, NOT photorealistic")}

SCENES = [
    ("a cheerful 3D cartoon toddler girl waving hello and smiling in a sunny cartoon park, Pixar style",
     "the cartoon girl waving her hand and smiling, gentle happy bounce, cheerful"),
    ("a happy 3D cartoon toddler girl playing with a big colorful beach ball on green grass, Pixar style",
     "the cartoon girl patting a colorful ball, giggling, gentle playful bounce"),
    ("a joyful 3D cartoon toddler girl clapping with floating balloons around her, Pixar style",
     "the cartoon girl clapping happily, balloons drifting up softly, cheerful"),
]


def post(p, d):
    r = urllib.request.Request(BASE + p, data=json.dumps(d).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def get(p):
    return json.loads(urllib.request.urlopen(BASE + p, timeout=30).read())


def main():
    proj = post("/api/projects", {"name": "Kids Cartoon Test", "description": "B test",
                                  "story": "wholesome kids cartoon", "material": "realistic"})
    pid = proj["id"]
    vid = post("/api/videos", {"project_id": pid, "title": "Kids Cartoon Test",
               "video_story": "wholesome kids cartoon", "display_order": 0, "orientation": "VERTICAL"})["id"]
    # entity ref for consistency
    cid = post("/api/characters", ENTITY)["id"]
    post(f"/api/projects/{pid}/characters/{cid}", {})
    rid = post("/api/requests", {"type": "GENERATE_CHARACTER_IMAGE", "character_id": cid, "project_id": pid})["id"]
    for _ in range(20):
        time.sleep(12)
        if get(f"/api/requests/{rid}")["status"] in ("COMPLETED", "FAILED"):
            break
    print("entity ref:", get(f"/api/requests/{rid}")["status"], flush=True)
    cnames = [ENTITY["name"]]
    sids = []
    for i, (img_p, vid_p) in enumerate(SCENES):
        sids.append(post("/api/scenes", {"video_id": vid, "display_order": i,
                    "prompt": f"{img_p}. {STYLE}.", "video_prompt": vid_p,
                    "character_names": cnames, "chain_type": "ROOT"})["id"])
    # paced image gen (1-at-a-time +12s)
    outdir = f"output/{SLUG}/img"
    os.makedirs(outdir, exist_ok=True)
    for idx, sid in enumerate(sids):
        r = post("/api/requests", {"type": "GENERATE_IMAGE", "scene_id": sid, "project_id": pid,
                 "video_id": vid, "orientation": "VERTICAL"})["id"]
        for _ in range(24):
            time.sleep(15)
            if get(f"/api/requests/{r}")["status"] in ("COMPLETED", "FAILED"):
                break
        if idx < len(sids) - 1:
            time.sleep(12)
    scenes = sorted(get(f"/api/scenes?video_id={vid}"), key=lambda s: s["display_order"])
    got = 0
    for s in scenes:
        if s.get("vertical_image_status") == "COMPLETED" and s.get("vertical_image_url"):
            urllib.request.urlretrieve(s["vertical_image_url"], f"{outdir}/scene_{s['display_order']:02d}.jpg")
            got += 1
    print(f"images: {got}/3", flush=True)
    if got < 3:
        print("⚠ not all images (quota/filter?) — stopping"); return
    meta_video_batch.main(vid, SLUG)
    tiny_assemble.main(SLUG, MUSIC)
    print("=== KIDS TEST DONE ===", flush=True)


if __name__ == "__main__":
    main()
