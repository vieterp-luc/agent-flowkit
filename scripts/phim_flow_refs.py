"""Tạo ref nhân vật + bối cảnh cho 1 bộ truyện /fk-phim qua FLOW (skill /fk-gen-refs).

Đọc output/phim/<slug>/story.json → tạo 1 Flow project với mọi characters[]+settings[] thành
entity `visual_asset` (ra 1 ảnh DỌC mỗi cái, không phải character-sheet) → gen ref bằng Flow
(GENERATE_CHARACTER_IMAGE) → poll → tải `reference_image_url` về output/phim/<slug>/ref/<key>.jpg.
Lưu project_id vào story.json để tái dùng. Refs Flow KHÔNG watermark, commercial-safe.

Run: python3 scripts/phim_flow_refs.py <story_slug>
"""
import json
import os
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8100"
STYLE_TAIL = "cinematic, dramatic atmospheric lighting, highly detailed, vertical portrait, no text"


def get(p):
    return json.loads(urllib.request.urlopen(BASE + p, timeout=30).read())


def post(p, payload, t=60):
    req = urllib.request.Request(BASE + p, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=t).read())


def main(slug):
    base = f"output/phim/{slug}"
    sp = f"{base}/story.json"
    story = json.load(open(sp, encoding="utf-8"))
    ref_dir = f"{base}/ref"
    os.makedirs(ref_dir, exist_ok=True)

    # entity = mọi characters[] + settings[], type visual_asset (ảnh dọc đơn)
    ents = [(c["key"], c) for c in story.get("characters", [])]
    ents += [(s["key"], s) for s in story.get("settings", [])]

    # tái dùng project nếu story.json đã lưu flow_project_id
    pid = story.get("flow_project_id")
    if not pid:
        chars = [{"name": k, "entity_type": "visual_asset",
                  "description": f"{e['ref_prompt']}, {STYLE_TAIL}"} for k, e in ents]
        proj = post("/api/projects", {
            "name": f"PHIM REF — {story.get('title')}",
            "description": f"Ref nhân vật + bối cảnh cho /fk-phim story {slug}",
            "story": story.get("premise", ""), "material": "realistic",
            "characters": chars,
        })
        pid = proj.get("id") or proj["project_id"]
        story["flow_project_id"] = pid
        json.dump(story, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[project] tạo {pid} + {len(chars)} entity")
    else:
        print(f"[project] dùng lại {pid}")

    entities = get(f"/api/projects/{pid}/characters")
    todo = [e for e in entities if not (e.get("media_id") or "")]
    if todo:
        reqs = [{"type": "GENERATE_CHARACTER_IMAGE", "character_id": e["id"], "project_id": pid} for e in todo]
        post("/api/requests/batch", {"requests": reqs})
        print(f"[gen] submit {len(reqs)} ref… (poll)")
        for _ in range(80):
            st = get(f"/api/requests/batch-status?project_id={pid}&type=GENERATE_CHARACTER_IMAGE")
            print(f"  {time.strftime('%H:%M:%S')} done={st.get('done')} ok={st.get('completed')}/{st.get('total')} fail={st.get('failed')}", flush=True)
            if st.get("done"):
                break
            time.sleep(15)

    # tải ref về theo name (= key)
    entities = get(f"/api/projects/{pid}/characters")
    n = 0
    for e in entities:
        url = e.get("reference_image_url")
        key = e.get("name")
        if url and key:
            dest = f"{ref_dir}/{key}.jpg"
            urllib.request.urlretrieve(url, dest)
            n += 1
            print(f"  ↓ {key}.jpg ({os.path.getsize(dest)//1024} KB)")
        else:
            print(f"  ⚠️ {e.get('name')}: chưa có reference_image_url (media_id={(e.get('media_id') or '')[:8]})")
    print(f"\n=== DONE — tải {n}/{len(entities)} ref về {ref_dir} ===")


if __name__ == "__main__":
    main(sys.argv[1])
