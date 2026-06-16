"""Scene-source loader — decouples the /fk-phim Meta pipeline from Flow.

load(vid, slug) → list of {display_order, narrator_text, video_prompt, prompt} sorted by order.
- vid == "local": read output/<slug>/scenes.json (narrator/prompt) + output/<slug>/motions.json
  (video_prompt by index; falls back to a simple rotation if absent). NO Flow / API call.
- else: fetch from the Flow-backed scenes API by video_id (legacy path, unchanged).

Used by meta_video_batch.py, meta_assemble.py, phim_longform_build.py so the same builders
work whether scenes live in the DB (API) or only as local JSON (Flow-free).
"""
import json
import os
import urllib.request

BASE = "http://127.0.0.1:8100"
DEFAULT_MOTIONS = [
    "Slow gentle zoom in on the subject.",
    "Slow gentle zoom out.",
    "Slow gentle pan to the right.",
    "Slow gentle push in, subtle motion.",
]


def load(vid, slug):
    if vid == "local":
        d = json.load(open(f"output/{slug}/scenes.json", encoding="utf-8"))
        mp = f"output/{slug}/motions.json"
        motions = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else []
        out = []
        for i, s in enumerate(d["scenes"]):
            vp = motions[i] if i < len(motions) else DEFAULT_MOTIONS[i % len(DEFAULT_MOTIONS)]
            out.append({"display_order": i, "narrator_text": s.get("narrator", ""),
                        "video_prompt": vp, "prompt": s.get("prompt", "")})
        return out
    scenes = json.load(urllib.request.urlopen(f"{BASE}/api/scenes?video_id={vid}", timeout=30))
    scenes.sort(key=lambda s: s.get("display_order", 0))
    return scenes
