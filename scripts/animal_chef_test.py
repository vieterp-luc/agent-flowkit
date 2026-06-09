"""7-scene TEST: a cute animal cooking ONE specific dish like a real chef, with the DISH kept
consistent across scenes (dish has its own entity ref) + realistic appetizing food.

Two entities: the cat chef + the dish (strawberry pancakes). Both attached via character_names
so both stay consistent. Authentic cooking steps for that one dish. Paced gen (1/12s anti-429).

Run: python3 scripts/animal_chef_test.py
"""
import json
import os
import time
import urllib.request

import meta_video_batch
import tiny_assemble

BASE = "http://127.0.0.1:8100"
SLUG = "animal_chef/cat_pancakes_v2"
MUSIC = "output/tiny_animals/_bgm/kitchen_bake.mp3"

STYLE = ("adorable, photorealistic, cozy warm kitchen, realistic appetizing food photography, "
         "highly detailed delicious food, soft natural light, shallow depth of field, wholesome, "
         "vertical 9:16, no text")

CHEF = {"name": "cat chef", "entity_type": "character",
        "image_prompt": ("an adorable fluffy orange tabby cat wearing a white chef hat and apron, "
                         "standing upright on hind legs at a kitchen counter, front paws raised and "
                         "actively cooking, big round green eyes, photorealistic, cute")}
DISH = {"name": "strawberry pancakes", "entity_type": "visual_asset",
        "image_prompt": ("a stack of three fluffy golden pancakes topped with fresh red strawberries "
                         "and dripping maple syrup on a white plate, realistic appetizing food photography, "
                         "highly detailed, delicious")}

# Cat is the ACTIVE cook in every scene (paws performing the step), not a passive observer.
# (image_prompt, motion_prompt, character_names)
SCENES = [
    ("an adorable orange tabby cat chef standing at a counter cracking an egg into a mixing bowl with its paws, ingredients around",
     "the cat chef cracking an egg into the bowl, paws moving, slow realistic cooking", ["cat chef"]),
    ("an adorable cat chef gripping a whisk in its paws, whisking pancake batter in a bowl",
     "the cat chef whisking the batter in circular motion, batter swirling, realistic cooking", ["cat chef"]),
    ("an adorable cat chef tilting a bowl with its paws to pour creamy batter onto a hot buttered pan",
     "the cat chef pouring batter onto the hot pan, sizzle and steam, paws tilting the bowl, realistic", ["cat chef"]),
    ("an adorable cat chef holding a spatula in its paw, flipping a golden pancake in the pan",
     "the cat chef flipping a pancake with the spatula, gentle motion, steam rising, realistic", ["cat chef"]),
    ("an adorable cat chef stacking fluffy golden pancakes onto a white plate with its paws",
     "the cat chef placing a pancake onto the growing stack, paws moving, realistic cooking", ["cat chef", "strawberry pancakes"]),
    ("an adorable cat chef using its paws to place strawberries and drizzle maple syrup over the pancake stack",
     "the cat chef topping the pancakes with strawberries and pouring syrup, paws moving, glossy realistic", ["cat chef", "strawberry pancakes"]),
    ("an adorable cat chef proudly lifting the finished strawberry pancake plate with both paws toward the camera",
     "the cat chef lifting and presenting the pancake plate proudly, gentle happy bounce", ["cat chef", "strawberry pancakes"]),
]


def post(p, d):
    r = urllib.request.Request(BASE + p, data=json.dumps(d).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def get(p):
    return json.loads(urllib.request.urlopen(BASE + p, timeout=30).read())


def gen_ref(pid, entity):
    cid = post("/api/characters", entity)["id"]
    post(f"/api/projects/{pid}/characters/{cid}", {})
    rid = post("/api/requests", {"type": "GENERATE_CHARACTER_IMAGE", "character_id": cid, "project_id": pid})["id"]
    for _ in range(20):
        time.sleep(12)
        if get(f"/api/requests/{rid}")["status"] in ("COMPLETED", "FAILED"):
            break
    print(f"  ref {entity['name']}: {get(f'/api/requests/{rid}')['status']}", flush=True)
    time.sleep(12)


def main():
    pid = post("/api/projects", {"name": "Cat Pancakes V2", "description": "chef dish-consistent test",
               "story": "cat chef makes strawberry pancakes", "material": "realistic"})["id"]
    vid = post("/api/videos", {"project_id": pid, "title": "Cat Pancakes V2",
               "video_story": "cat chef cooking asmr", "display_order": 0, "orientation": "VERTICAL"})["id"]
    gen_ref(pid, CHEF)
    gen_ref(pid, DISH)
    sids = []
    for i, (img_p, vid_p, names) in enumerate(SCENES):
        sids.append(post("/api/scenes", {"video_id": vid, "display_order": i,
                    "prompt": f"{img_p}. {STYLE}.", "video_prompt": vid_p,
                    "character_names": names, "chain_type": "ROOT"})["id"])
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
    print(f"images: {got}/7", flush=True)
    if got == 0:
        print("⚠ 0 images (quota?) — stop"); return
    meta_video_batch.main(vid, SLUG)
    tiny_assemble.main(SLUG, MUSIC)
    print("=== PANCAKES TEST DONE ===", flush=True)


if __name__ == "__main__":
    main()
