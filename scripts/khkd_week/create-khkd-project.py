#!/usr/bin/env python3
"""Create a KHKD project from JSON spec: project -> video -> scenes."""
import json
import sys
import os
import urllib.request

BASE = "http://127.0.0.1:8100"


def post(path: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def patch(path: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(spec_path: str) -> None:
    spec = json.loads(open(spec_path, encoding="utf-8").read())
    slug = spec["slug"]
    out_dir = f"output/{slug}"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Create project + entities
    project = post("/api/projects", spec["project"])
    pid = project["id"]
    print(f"[OK] Project: {pid} | {project['name']}")

    # 2. Create video
    video = post("/api/videos", {**spec["video"], "project_id": pid})
    vid = video["id"]
    print(f"[OK] Video: {vid} | {video['title']}")

    # 3. Create scenes (track IDs by display_order for parent linking)
    scene_ids: dict[int, str] = {}
    for s in spec["scenes"]:
        payload = {
            "video_id": vid,
            "display_order": s["display_order"],
            "chain_type": s["chain_type"],
            "character_names": s["character_names"],
            "prompt": s["prompt"],
            "video_prompt": s["video_prompt"],
            "narrator_text": s["narrator_text"],
        }
        if s["chain_type"] == "CONTINUATION":
            payload["parent_scene_id"] = scene_ids[s["parent_index"]]
        sc = post("/api/scenes", payload)
        scene_ids[s["display_order"]] = sc["id"]
        # narrator_text isn't accepted on create — PATCH it
        patch(f"/api/scenes/{sc['id']}", {"narrator_text": s["narrator_text"]})
        print(f"[OK] Scene #{s['display_order']} ({s['chain_type']}): {sc['id']}")

    # Save IDs for later steps
    ids_path = f"{out_dir}/ids.json"
    json.dump(
        {"project_id": pid, "video_id": vid, "scene_ids": scene_ids},
        open(ids_path, "w", encoding="utf-8"),
        indent=2,
    )
    print(f"[OK] Saved IDs -> {ids_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: create-khkd-project.py <spec.json>")
        sys.exit(1)
    main(sys.argv[1])
