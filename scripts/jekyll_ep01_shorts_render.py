"""Render 3 Jekyll & Hyde ep1 Shorts (1080x1920) using lamplit_shorts_pipeline."""
import sys
from pathlib import Path

ROOT = Path("/Users/vieterp/code/Research/agent-flowkit")
sys.path.insert(0, str(ROOT / "scripts"))

# Override module-level config in lamplit_shorts_pipeline + reuse helpers
import lamplit_shorts_pipeline as L

# Point at Jekyll project + Shorts output dir
L.EP_ROOT = ROOT / "output/jekyll_hyde_classics_en"
L.OUT_DIR = L.EP_ROOT / "shorts"
L.OUT_DIR.mkdir(parents=True, exist_ok=True)

# 3 Shorts — pick climax moments per pilot strategy
# Constraint: total = LEAD_SEC + TTS_dur + TAIL_SEC ≤ 60s
# LEAD=1.5 TAIL=4.0 → TTS_dur ≤ 54.5s
# sum_1 = 59.8s (TOO LONG — skip or trim)
# sum_2 = 51.5s ✓ (will scene + cheque mystery)
# sum_3 = 48.1s ✓ (Lanyon dinner)
# sum_4 = 56.2s (slightly over — would render 61.7s, near YT cutoff)
# sum_5 = 55.0s (60.5s total, exactly at cap — borderline)
# sum_6 = 55.2s (over)
# Picks: sum_2, sum_3, sum_5 — all under cap, span chapters 2-3

L.SHORTS = [
    {
        "ep": 1, "slug": "ep01_story_of_the_door",
        "scene": "scene_02.png",
        "tts": "02_sum_2.wav",
        "hook1": "A WILL",
        "hook2": "FOR A STRANGER",
        "ep_label": "JEKYLL & HYDE  ·  EP 1",
        "section_label": "THE WILL",
        "out_name": "short_ep01_a.mp4",
    },
    {
        "ep": 1, "slug": "ep01_story_of_the_door",
        "scene": "scene_03.png",
        "tts": "03_sum_3.wav",
        "hook1": "AN OLD FRIEND",
        "hook2": "TURNS AWAY",
        "ep_label": "JEKYLL & HYDE  ·  EP 1",
        "section_label": "LANYON'S BREAK",
        "out_name": "short_ep01_b.mp4",
    },
    {
        "ep": 1, "slug": "ep01_story_of_the_door",
        "scene": "scene_05.png",
        "tts": "05_sum_5.wav",
        "hook1": "INSIDE THE",
        "hook2": "SAME HOUSE",
        "ep_label": "JEKYLL & HYDE  ·  EP 1",
        "section_label": "ONE BUILDING",
        "out_name": "short_ep01_c.mp4",
    },
]


# Wrap render_short to use out_name override
orig_render = L.render_short


def render_with_name(cfg):
    out_name = cfg.get("out_name", f"short_ep{cfg['ep']:02d}.mp4")
    # Monkey-patch the OUT_DIR Path lookup by overriding via cfg → manipulate
    # Simplest: call original then rename
    rendered = orig_render(cfg)
    target = L.OUT_DIR / out_name
    if rendered != target:
        if target.exists():
            target.unlink()
        rendered.rename(target)
    return target


for cfg in L.SHORTS:
    print(f"\n=== {cfg['out_name']} ({cfg['hook1']} {cfg['hook2']}) ===")
    render_with_name(cfg)

print("\n--- ALL SHORTS ---")
for f in sorted(L.OUT_DIR.glob("short_ep01_*.mp4")):
    print(f"  {f.name}  ({f.stat().st_size // 1024} KB)")
