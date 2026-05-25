#!/usr/bin/env python3
"""PATCH narrator_text into scenes based on spec.json."""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8100"


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


def get_json(path: str) -> list:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(spec_path: str) -> None:
    spec = json.loads(open(spec_path, encoding="utf-8").read())
    slug = spec["slug"]
    ids = json.loads(open(f"output/{slug}/ids.json", encoding="utf-8").read())
    vid = ids["video_id"]

    scenes = get_json(f"/api/scenes?video_id={vid}")
    by_order = {s["display_order"]: s["id"] for s in scenes}

    for s in spec["scenes"]:
        sid = by_order[s["display_order"]]
        patch(f"/api/scenes/{sid}", {"narrator_text": s["narrator_text"]})
        print(f"[OK] scene #{s['display_order']}: {s['narrator_text'][:60]}...")


if __name__ == "__main__":
    main(sys.argv[1])
