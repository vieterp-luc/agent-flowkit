"""Produce 1 /fk-phim episode: gen scene images via Meta (+ref). FLOW-FREE.

Reads:  output/phim/<story>/story.json        (visual_style)
        output/phim/<story>/<ep>/scenes.json  ({title, scenes:[{prompt, ref, narrator}]})
Writes: output/phim/<story>/<ep>/img/scene_NN.jpg

Narrator + motion now live in scenes.json / motions.json and are read locally by the build
scripts (phim_scene_source.load "local"), so NO Flow project/scene is created here — image
gen is the only step. Per scene: prompt = "<prompt>, <visual_style>"; ref from ref/<ref>.jpg.
Meta is sequential + slow → skip existing images, gap 20s. Failures logged, continue (rerun retries).

Run: python3 scripts/phim_produce_ep.py <story> <ep>     e.g. ngo_hai_tung_le ep01
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_image_gen import gen_one  # noqa: E402

GAP_S = 20


def main(story, ep):
    base = f"output/phim/{story}"
    epdir = f"{base}/{ep}"
    style = json.load(open(f"{base}/story.json", encoding="utf-8"))["visual_style"]
    scenes = json.load(open(f"{epdir}/scenes.json", encoding="utf-8"))["scenes"]
    ref_dir = f"{base}/ref"

    os.makedirs(f"{epdir}/img", exist_ok=True)
    fails = []
    for i, s in enumerate(scenes):
        dest = f"{epdir}/img/scene_{i:02d}.jpg"
        if os.path.exists(dest):
            print(f"scene_{i:02d}: exists, skip"); continue
        ref = f"{ref_dir}/{s['ref']}.jpg" if s.get("ref") else None
        if ref and not os.path.exists(ref):
            print(f"scene_{i:02d}: ⚠️ ref missing {ref} → no-ref"); ref = None
        prompt = f"{s['prompt']}, {style}"
        print(f"scene_{i:02d}: gen{' +ref ' + s['ref'] if ref else ''} … {s['prompt'][:50]}")
        try:
            if not gen_one(prompt, dest, ref=ref):
                fails.append(i)
        except Exception as e:
            print(f"  ERR {e}"); fails.append(i)
        time.sleep(GAP_S)

    have = sum(os.path.exists(f"{epdir}/img/scene_{i:02d}.jpg") for i in range(len(scenes)))
    print(f"\n=== {have}/{len(scenes)} images ready ===")
    if fails:
        print(f"FAILED scenes (rerun to retry): {fails}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
