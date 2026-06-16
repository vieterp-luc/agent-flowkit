"""Gen TẤT CẢ ref ảnh (nhân vật + bối cảnh) cho 1 bộ truyện /fk-phim — 1 lệnh.

Đọc output/phim/<story>/story.json → với mỗi characters[] và settings[], gen 1 ảnh ref
qua Meta (ref_prompt + đuôi style sạch, ép 9:16) → output/phim/<story>/ref/<key>.jpg.
Tuần tự (browser khoá), skip ref đã có, re-run để bù ref thiếu.

Run: python3 scripts/phim_gen_refs.py <story_slug>      # vd: huyen_giam
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import meta_image_gen  # reuse gen_one

# Đuôi sạch cho ẢNH REF (1 chủ thể) — KHÔNG nhồi cả visual_style cảnh (gây lẫn núi/đạo bào).
REF_TAIL = "cinematic, dramatic atmospheric lighting, highly detailed, vertical 9:16 portrait format, no text"
GAP_S = 20


def main(slug):
    base = f"output/phim/{slug}"
    story = json.load(open(f"{base}/story.json", encoding="utf-8"))
    ref_dir = f"{base}/ref"
    os.makedirs(ref_dir, exist_ok=True)

    items = [("char", c) for c in story.get("characters", [])]
    items += [("set", s) for s in story.get("settings", [])]
    print(f"=== {story.get('title')} — {len(items)} ref (nhân vật + bối cảnh) ===")
    first = True
    for kind, it in items:
        key = it["key"]
        dest = f"{ref_dir}/{key}.jpg"
        if os.path.exists(dest):
            print(f"[{kind}] {key}: exists, skip"); continue
        if not first:
            time.sleep(GAP_S)
        first = False
        prompt = f"{it['ref_prompt']}, {REF_TAIL}"
        print(f"[{kind}] {key}: gen… ({it.get('name','')})")
        meta_image_gen.gen_one(prompt, dest)
    have = len([f for f in os.listdir(ref_dir) if f.endswith(".jpg")])
    print(f"\n=== DONE — {have} ref trong {ref_dir} ===")


if __name__ == "__main__":
    main(sys.argv[1])
