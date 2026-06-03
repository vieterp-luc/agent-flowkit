"""Rebuild a video's clips from harvested /prompt pages — match each scene's typed
prompt to the newest harvested generation and download THAT exact video (no regen).

Run: python scripts/meta_rebuild_from_harvest.py <video_id> <slug> [harvest_json]
Default harvest_json = /tmp/harvest45.json
"""
import json
import re
import sys
import urllib.request

BASE = "http://127.0.0.1:8100"


def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def main(vid, slug, hjson):
    items = json.load(open(hjson))["items"]
    for it in items:
        it["_t"] = norm(it.get("text"))
    scenes = sorted(json.load(urllib.request.urlopen(f"{BASE}/api/scenes?video_id={vid}", timeout=30)),
                    key=lambda s: s["display_order"])
    clips = f"output/{slug}/clips"
    matched = 0
    for s in scenes:
        n = s["display_order"]
        vp = norm(s.get("video_prompt"))
        # distinctive slice of the typed motion prompt (skip generic tail words)
        phrase = vp[:55]
        hit = next((it for it in items if it.get("src") and phrase in it["_t"]), None)
        if not hit:  # fallback: shorter / mid slice
            hit = next((it for it in items if it.get("src") and vp[:35] in it["_t"]), None)
        if not hit:
            print(f"scene_{n:02d}: NO MATCH ({phrase[:40]}…)")
            continue
        dest = f"{clips}/scene_{n:02d}.mp4"
        req = urllib.request.Request(hit["src"], headers={"User-Agent": "Mozilla/5.0"})
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            open(dest, "wb").write(data)
            print(f"scene_{n:02d} ← {hit['url'].split('/')[-1][:12]} {len(data)//1024}KB")
            matched += 1
        except Exception as e:
            print(f"scene_{n:02d}: DL FAIL {e}")
    print(f"=== matched {matched}/{len(scenes)} ===")


if __name__ == "__main__":
    hjson = sys.argv[3] if len(sys.argv) > 3 else "/tmp/harvest45.json"
    main(sys.argv[1], sys.argv[2], hjson)
