#!/usr/bin/env python3
"""fk-build render pipeline — Flow chained stage images + Veo transitions + concat + music + brand.

Used by /fk-build skill. Modular, resumable, idempotent.
Halt-on-quota at every stage-gen and Veo submission step.

Pipeline stages:
  A  Validate + load analysis.json (written by Phase A of skill)
  B  Flow image generation: GENERATE_IMAGE (Stage 0) + EDIT_IMAGE waves (Stages 1..N-1)
     Modeled on fk-video-vetranh: upload source → visual_asset entity → N scenes → wave-by-wave submit
  C  Flow Veo transition videos (upload stage images → ephemeral project → probe + batch)
  D  Concat clips → mix BGM → brand logo overlay → final_branded.mp4

Usage:
    python3 scripts/fk-build-render-stages.py --image path/to/source.jpg --slug house_modern_villa_001
    python3 scripts/fk-build-render-stages.py --slug house_modern_villa_001 --resume
    python3 scripts/fk-build-render-stages.py --slug house_modern_villa_001 --dry-run
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:8100"
ROOT = Path(__file__).parent.parent
OUTPUT_BASE = ROOT / "output" / "fk_build"

# Quota-error patterns to detect in stderr / response bodies
QUOTA_PATTERNS = ("QUOTA", "quota", "limit", "exceeded", "429", "rate limit",
                  "RESOURCE_EXHAUSTED", "too many requests")

# Stage 0 archetype mapping (subject → default description)
STAGE_0_ARCHETYPES = {
    "house":               "a decayed dilapidated shell with peeling paint, broken windows, overgrown yard, and exposed weathered materials",
    "garden":              "a barren wasteland — bare dirt, knee-high weeds, no plants, no hardscape, no furniture",
    "room":                "a bare empty shell — stripped plaster walls, bare concrete subfloor, single bare bulb hanging, no furniture whatsoever",
    "building":            "an empty bare plot of graded earth with temporary chain-link construction fencing, excavation equipment parked on side, building materials staged",
    "object/food":         "raw ingredients arranged in bowls and on a cutting board — mise-en-place on the same surface, no finished item",
    "object/furniture":    "a pile of rough raw lumber planks, hand tools (saw, clamps, sandpaper, screws, chisels) on a workshop floor",
    "object/electronics":  "scattered electronic components (bare PCB, chips, battery cells, metal frame, screen panel, screws) laid on an antistatic mat",
    "object/sculpture":    "a raw uncarved stone block or rough clay lump on a pedestal with chisels and mallets leaning against it",
    "object/painting":     "a blank stretched canvas on an easel with paint tubes, brushes, and a clean mixing palette arranged nearby",
    "object/model":        "a sealed retail box and loose sprues with instruction manual open beside them and loose pieces scattered on a building mat",
    "object/instrument":   "raw tonewoods blanks, string sets in packaging, tuning pegs, and luthier tools spread on a workbench",
    "object/other":        "raw materials and basic tools laid out neatly on the same neutral surface as the finished object",
}

# Per-subject N=4 milestone table (interpolated for other N values)
MILESTONES_N4 = {
    "house":              [("Decayed shell",       0), ("Demolished + scaffolding", 25), ("Walls/roof rebuilt + primed", 50), ("Windows, doors, paint + landscaping", 75), ("Final", 100)],
    "garden":             [("Wasteland",           0), ("Cleared + graded",        25), ("Hardscape installed",        50), ("Softscape mid-growth",               75), ("Final", 100)],
    "room":               [("Bare shell",          0), ("Walls painted + flooring", 25), ("Major furniture in place",   50), ("Decor + soft furnishings + lighting",  75), ("Final", 100)],
    "building":           [("Empty plot",          0), ("Foundation + ground floor frame", 25), ("Mid-rise frame + partial skin", 50), ("Curtain wall + facade complete", 75), ("Final", 100)],
    "object/food":        [("Raw ingredients",     0), ("Baked unfrosted layers",  25), ("Crumb-coat + base frosting", 50), ("Decorated tiers + piping",           75), ("Final", 100)],
    "object/furniture":   [("Raw lumber + tools",  0), ("Pieces cut + dry-fit",    25), ("Joinery glued + clamped",    50), ("Sanded + first stain coat",           75), ("Final", 100)],
    "object/electronics": [("Components scattered",0), ("PCB + frame assembled",   25), ("Screen + battery installed", 50), ("Closed body, screen on",             75), ("Final", 100)],
    "object/sculpture":   [("Raw block + chisels", 0), ("Rough form blocked out",  25), ("Mid-detail carving",         50), ("Fine detail + initial polish",        75), ("Final", 100)],
    "object/painting":    [("Blank canvas",        0), ("Underpainting / sketch",  25), ("Mid-layer color blocking",   50), ("Detail pass + highlights",            75), ("Final", 100)],
    "object/model":       [("Sealed box / sprues", 0), ("Base + lower walls",      25), ("Mid-structure + sub-assemblies", 50), ("Towers + roof + flags partial",  75), ("Final", 100)],
    "object/instrument":  [("Wood blanks + tools", 0), ("Body shaped + top glued", 25), ("Neck attached + fretboard",  50), ("Hardware + finish coat",             75), ("Final", 100)],
    "object/other":       [("Raw materials",       0), ("25% assembled",           25), ("50% assembled",              50), ("75% assembled + finishing",           75), ("Final", 100)],
}

# Per-subject music mood color
MUSIC_COLORS = {
    "house":               "industrious, hopeful, accomplished",
    "building":            "grand, constructive, majestic accomplishment",
    "garden":              "organic, earthy, peaceful, blooming joyful",
    "room":                "cozy, warm, cinematic reveal",
    "object/food":         "playful, appetizing, warm",
    "object/furniture":    "artisanal, woody, warm craft",
    "object/electronics":  "clean, modern, minimal — no drums",
    "object/sculpture":    "contemplative, classical",
    "object/painting":     "dreamy, romantic, impressionistic",
    "object/model":        "nostalgic, playful",
    "object/instrument":   "warm, craft, melodic",
    "object/other":        "satisfying, warm, transformational",
}

# Per-subject Veo phase-action snippets (compact, fallback when no milestone-keyed entry)
VEO_PHASE_ACTIONS = {
    "house":               "Workers hauling materials, scaffolding rising, walls forming brick-by-brick, windows snapping in, roof tiles sliding into place",
    "building":            "Cranes swinging, foundation poured, structural frame rising floor-by-floor, curtain wall panels clicking into place",
    "garden":              "Clearing → soil prep → hardscape laying → soil tilling → planting → fast-growth blooming",
    "room":                "Stripping → painting walls → flooring rolling out → furniture sliding in → decor appearing → lights flicking on",
    "object/food":         "Mixing batter, pouring into pans, baking flash, layers stacking, frosting sweeps, piping appearing in fast strokes",
    "object/furniture":    "Cutting flash, pieces dry-fitting, glue + clamp tightening, sanding passes, stain coat rolling on",
    "object/electronics":  "Components snapping onto PCB, frame closing, screen lighting up, final body sealed",
    "object/sculpture":    "Chisel chips flying, rough form emerging, detail carving, polishing pass revealing sheen",
    "object/painting":     "Brush strokes appearing, underpainting, color blocking, glazing layers, highlights dotted on",
    "object/model":        "Pieces clicking together, walls rising, towers growing, minifigs placed, flags snapping on",
    "object/instrument":   "Body glued + clamped, neck joined, fretboard pressed on, tuning pegs installed, strings wound, polish coat",
    "object/other":        "Components assembling, structure taking shape, finishing details applied",
}

# Per-subject, per-milestone Veo action (Fix B: phase-specific instead of full sequence)
# Picked by build_veo_prompt using milestone_to_name. Falls back to VEO_PHASE_ACTIONS.
VEO_PHASE_ACTIONS_BY_MILESTONE = {
    "room": {
        "Walls painted + flooring": "Workers stripping debris off the walls, then rolling cream-beige paint onto every wall, then wide-plank oak flooring rolling out and locking into place across the bare concrete subfloor",
        "Major furniture in place": "Cream-beige sectional sofa carried in and positioned in the FOREGROUND-LEFT corner, walnut coffee table set in front of the sofa, walnut TV console floating onto the RIGHT wall, 65-inch TV mounted on the RIGHT wall above the console — NO decor, NO plants, NO candles yet",
        "Decor + soft furnishings + lighting": "Tall cypress plant placed in a terracotta pot beside the TV console, amber pillar candles arranged on the coffee table and LIT (visible warm flame), wall sconces installed and turned on, cream wool rug rolled out under the coffee table, sheer + opaque beige curtains drawn on the LEFT wall flanking the balcony glass, warm cove LED perimeter flicking on along the ceiling — evening warmth settling in",
        "Final": "Last ambient adjustments — full evening twilight outside, warm interior LED at full glow, decor settled into place, no movement",
        # Special key used by build_veo_prompt when n_stages==1 (one-shot full build with workers)
        "__FULL__": "A small crew of workers visible in frame: hammering and screwing, hands carrying buckets of cream-beige paint and rollers, then rolling out wide-plank oak flooring, then sliding the cream sectional sofa into the foreground-LEFT corner, sliding the walnut coffee table and walnut TV console into place, mounting the TV on the RIGHT wall, then placing a tall cypress plant in a terracotta pot, lighting amber pillar candles with a visible warm flame, switching on wall sconces, rolling out the cream wool rug, drawing beige curtains on the LEFT wall, and finally the warm cove LED perimeter flicking on as twilight settles — continuous build with visible workers, hands, and tools throughout",
    },
}

def get_veo_phase_action(subject_key: str, milestone_to_name: str) -> str:
    """Fix B: pick milestone-specific action; fallback to subject's full sequence."""
    by_milestone = VEO_PHASE_ACTIONS_BY_MILESTONE.get(subject_key, {})
    if milestone_to_name in by_milestone:
        return by_milestone[milestone_to_name]
    return VEO_PHASE_ACTIONS.get(subject_key, VEO_PHASE_ACTIONS["object/other"])


# ---------- helpers ----------

def die(msg: str):
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def halt_quota(msg: str):
    print(f"\nQUOTA HALT: {msg}")
    print("Re-run with --resume after quota resets.")
    sys.exit(2)


def is_quota_error(text: str) -> bool:
    return any(p in text for p in QUOTA_PATTERNS)


def api_post(path: str, payload: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if is_quota_error(body) or is_quota_error(str(e.code)):
            halt_quota(f"POST {path} → HTTP {e.code}: {body[:200]}")
        raise RuntimeError(f"POST {path} HTTP {e.code}: {body[:200]}") from e


def api_get(path: str, timeout: int = 30) -> dict:
    try:
        with urllib.request.urlopen(f"{API}{path}", timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GET {path} HTTP {e.code}: {body[:200]}") from e


def run(cmd: list, **kw):
    """Run a subprocess, raise on non-zero exit."""
    result = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(str(c) for c in cmd)}\n{result.stderr[-500:]}")
    return result


def ffprobe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def image_file_ok(path: Path, min_bytes: int = 30_000) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def health_check():
    """Ensure Flow server is healthy."""
    try:
        resp = api_get("/health", timeout=10)
        if not resp.get("extension_connected"):
            die("FlowKit /health returned extension_connected=false. Run /fk-doctor.")
    except Exception as e:
        die(f"FlowKit server unreachable: {e}. Run /fk-doctor.")


def derive_subject_key(subject: str, subtype: str | None) -> str:
    """Return compound key for milestone/archetype lookups."""
    if subject == "object" and subtype:
        return f"object/{subtype}"
    return subject


def get_milestones(subject_key: str, n_stages: int) -> list[tuple[str, int]]:
    """Return list of (milestone_name, pct) with length n_stages+1 (stage 0..N)."""
    base = MILESTONES_N4.get(subject_key, MILESTONES_N4["object/other"])
    if n_stages == 4:
        return base  # already 5 entries (0..4)
    # Interpolate: always keep Stage 0 (idx 0) and Stage N (last) fixed; distribute middle
    result = [base[0]]
    for i in range(1, n_stages):
        pct = round(i * 100 / n_stages)
        # Name by nearest base milestone
        nearest = min(base[1:-1], key=lambda m: abs(m[1] - pct), default=base[1])
        result.append((nearest[0], pct))
    result.append(base[-1])  # Stage N = Final 100%
    return result


def build_lock_block(analysis: dict) -> str:
    """Build LOCK BLOCK preamble + LAYOUT MAP + INVENTORY + camera/wall + time-of-day lock.

    Fix A: time_of_day from scene_context is pulled into a dedicated lock line so every
    stage prompt anchors the same lighting (prevents day↔night drift between stages).
    """
    lb = analysis.get("lock_blocks", {})
    layout = lb.get("layout_map", "")
    inventory = lb.get("inventory", "")
    sc = analysis.get("scene_context", {})
    camera_angle = sc.get("camera_angle", "")
    time_of_day = sc.get("time_of_day", "")
    preamble = (
        "VERTICAL PORTRAIT 9:16 (1080x1920) framing. "
        "STRICTLY NO TEXT, NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS in the image."
    )
    parts = [preamble]
    if time_of_day:
        parts.append(
            f"TIME-OF-DAY LOCK (NEVER drift between stages): {time_of_day}\n"
            "Keep exterior light tone + interior color temperature IDENTICAL across all stages."
        )
    if camera_angle:
        parts.append(
            f"CAMERA LOCK (NEVER deviate from this exact framing across all stages):\n{camera_angle}\n"
            "Do not switch to head-on / centered / symmetric framing — keep the exact angle and depth perspective from the input."
        )
    if layout:
        parts.append(f"LAYOUT MAP (positional lock — every wall/zone fixed):\n{layout}")
    if inventory:
        parts.append(f"INVENTORY:\n{inventory}")
    return "\n\n".join(parts)


# ---------- Stage B: Flow image generation (GENERATE_IMAGE + EDIT_IMAGE waves) ----------
# Modeled on fk-video-vetranh: upload source image → visual_asset entity → N scenes → wave-by-wave submit

def build_stage0_prompt(analysis: dict, subject_key: str) -> str:
    archetype = analysis.get("stage_0_archetype", STAGE_0_ARCHETYPES.get(subject_key, STAGE_0_ARCHETYPES["object/other"]))
    lock_block = build_lock_block(analysis)
    subject_display = analysis.get("subject", "subject")

    subject_rule_map = {
        "house":     "Show the property in DECAYED state — peeling paint, broken windows, overgrown yard. Lot dimensions and house footprint preserved.",
        "building":  "Show empty bare plot of graded earth with temp construction fencing, materials staged on side, no foundation poured yet.",
        "garden":    "Apply build-garden Stage 0 rule — pond pit visible if final has pond; wasteland surface dominates 80-90% visual weight.",
        "room":      "Show bare empty shell — stripped plaster walls, bare subfloor, single bare bulb hanging, NO furniture.",
    }
    subject_rule = subject_rule_map.get(analysis.get("subject", ""), (
        "Show ONLY the raw materials + tools needed to make this object, arranged on the same surface as input. "
        "The finished object MUST be absent. Surface, background, and lighting stay IDENTICAL."
    ))

    return f"""[VERTICAL PORTRAIT 9:16, 1080x1920]
Transform this image so the {subject_display} is COMPLETELY removed and replaced with {archetype}.

LOCKED — keep IDENTICAL to original:
- Camera angle, focal length, framing
- Sky / weather / time-of-day / ambient lighting
- Fence, wall boundaries, neighboring buildings, external trees, street/sidewalk pattern (outdoor subjects)
- Room SHELL: walls, ceiling, floor subfloor, window/door openings (room subjects)
- Surface the object rests on, background, lighting setup (object subjects)

{lock_block}

Stage 0 must look RADICALLY DIFFERENT from input — wasteland/raw-materials character dominates 80-90% visual weight; future layout hints ≤ 10%.
{subject_rule}
DO NOT introduce components, plants, or materials not listed in INVENTORY.
STRICTLY NO TEXT, NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS.
Photorealistic, ultra-detailed, cinematic. IDENTICAL camera angle to input."""


def build_stage_k_prompt(analysis: dict, k: int, n_stages: int, milestones: list, subject_key: str) -> str:
    lock_block = build_lock_block(analysis)
    subject_display = analysis.get("subject", "subject")
    milestone_name, pct = milestones[k]
    prev_milestone, prev_pct = milestones[k - 1]

    future_milestones = [m[0] for m in milestones[k + 1:-1]]  # exclude Stage N (Final)

    inherited_block = f"Everything already built/installed at Stage {k-1} ({prev_milestone}, {prev_pct}%). Same camera angle, lighting, surroundings."
    new_block = f"Progress to {milestone_name} milestone — approximately {pct}% complete. Add ONLY the structural elements characteristic of this phase."

    # Strong negative discipline: enforce that mid-stage shots are BARE structurally — no ambient decor.
    is_final_stage = (k == n_stages - 1)  # last GENERATED stage before Stage N (source)
    if not is_final_stage:
        decor_ban = (
            "ABSOLUTELY NO ambient decor at this stage: no candles (lit or unlit), no lit lamps, "
            "no glowing wall sconces, no LED cove/strip glow, no potted plants, no decorative pillows, "
            "no books, no framed photos, no dried decor, no rugs, no sheer curtain layer. "
            "These ALL arrive only at the final stage. The room/scene must look STRUCTURALLY done but "
            "BARE — like a model home before staging."
        )
        missing_list = (", ".join(future_milestones) + " (do not add yet)") if future_milestones else "Final staging/decor pass."
        missing_block = f"{missing_list}\n  {decor_ban}"
    else:
        missing_block = (", ".join(future_milestones) + " (do not add yet)") if future_milestones else "Nothing — this is the final construction stage."

    return f"""[VERTICAL PORTRAIT 9:16, 1080x1920]
Starting from this image (Stage {k-1} of {subject_display} build — showing {prev_milestone} at {prev_pct}% completion), advance it to Stage {k} — approximately {pct}% complete at the "{milestone_name}" milestone.

LOCKED — keep IDENTICAL to Stage {k-1}:
- Camera angle, focal length, framing
- Sky / lighting / surroundings
- Everything already built / installed in Stage {k-1}

INHERITED from Stage {k-1} (must look IDENTICAL at these elements):
- {inherited_block}

NEW IN Stage {k} (added/changed in this step):
- {new_block}

STILL MISSING in Stage {k} (appears in later stages — DO NOT add yet):
- {missing_block}

{lock_block}

CONTINUITY RULES:
- Position/orientation LOCK: every zone at EXACT position from LAYOUT MAP.
- Identity LOCK: every plant/component/material matches INVENTORY — only completion/maturity/finish changes per stage.
- Camera LOCK: never move.
DO NOT introduce components, plants, or materials not listed in INVENTORY.
STRICTLY NO TEXT, NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS.
Photorealistic, ultra-detailed."""


def upload_source_image(source_jpg: Path) -> str:
    """Upload source.jpg via /api/flow/upload-image (vetranh Step 0 pattern). Returns media_id."""
    payload = json.dumps({
        "file_path": str(source_jpg),
        "file_name": source_jpg.name,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/api/flow/upload-image",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"flow/upload-image HTTP {e.code}: {err_body[:200]}") from e
    media_id = result.get("media_id") or result.get("id")
    if not media_id or len(media_id) < 32:
        raise RuntimeError(f"flow/upload-image returned unexpected media_id: {result}")
    return media_id


def api_patch(path: str, payload: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PATCH {path} HTTP {e.code}: {body[:200]}") from e


def poll_imggen_wave(vid: str, request_type: str, poll_every: int = 12, max_wait: int = 600) -> bool:
    """Poll batch-status for GENERATE_IMAGE or EDIT_IMAGE until done:true."""
    start = time.time()
    while time.time() - start < max_wait:
        status = api_get(f"/api/requests/batch-status?video_id={vid}&type={request_type}")
        if is_quota_error(json.dumps(status)):
            halt_quota(f"Quota error in {request_type} batch-status: {status}")
        done = status.get("done", False)
        total = status.get("total", 0)
        completed = status.get("completed", 0)
        failed = status.get("failed", 0)
        print(f"  {request_type} progress: {completed}/{total} done, {failed} failed ({int(time.time()-start)}s)")
        if done:
            if failed > 0:
                print(f"  WARNING: {failed} image gen request(s) failed. Run /fk-doctor for details.")
                return False
            return True
        time.sleep(poll_every)
    print(f"  WARNING: {request_type} wave did not complete within {max_wait}s.")
    return False


def download_stage_image(scene_id: str, stage_path: Path) -> bool:
    """Download vertical_image_url from a scene to stage_path. Returns True if successful."""
    scene = api_get(f"/api/scenes/{scene_id}")
    url = scene.get("vertical_image_url")
    if not url:
        print(f"  WARNING: No vertical_image_url for scene {scene_id}")
        return False
    urllib.request.urlretrieve(url, str(stage_path))
    return stage_path.exists() and stage_path.stat().st_size > 30_000


def crop_to_9_16_if_needed(img_path: Path) -> None:
    """If image is not 9:16, center-crop it in-place using ffmpeg."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(img_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return
    parts = result.stdout.strip().split(",")
    if len(parts) != 2:
        return
    w, h = int(parts[0]), int(parts[1])
    ratio = w / h
    if abs(ratio - 9 / 16) < 0.05:
        return  # already ~9:16
    tmp = img_path.with_suffix(".tmp.jpg")
    run(["ffmpeg", "-y", "-i", str(img_path), "-vf", "crop=ih*9/16:ih", str(tmp)])
    tmp.replace(img_path)
    print(f"    Cropped {img_path.name} to 9:16 (was {w}x{h})")


def phase_b_generate_stages(slug_dir: Path, analysis: dict, n_stages: int, subject_key: str,
                              milestones: list, dry_run: bool, resume: bool) -> None:
    """Generate N stage images via Flow (GENERATE_IMAGE Wave 1 + EDIT_IMAGE Waves 2..N).
    Stage N = source.jpg copy — no generation needed.
    Modeled on fk-video-vetranh Step 0-2 pattern.
    """
    print(f"\n[Phase B] Flow image gen — {n_stages} generated stages + Stage N copy...")
    stages_dir = slug_dir / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir = slug_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    source_jpg = slug_dir / "source.jpg"
    if not source_jpg.exists():
        die(f"source.jpg not found at {source_jpg} — run Phase A (analysis) first via /fk-build skill.")

    # Stage N = source.jpg copy (no gen — it's already the final state)
    stage_n_file = stages_dir / f"stage_{n_stages:02d}.jpg"
    if not stage_n_file.exists():
        import shutil
        shutil.copy2(source_jpg, stage_n_file)
        print(f"  stage_{n_stages:02d}: copied from source.jpg (= Stage N = final)")
    else:
        print(f"  stage_{n_stages:02d}: already exists (source copy)")

    # Check if all generated stages already exist (full resume)
    if resume and all(image_file_ok(stages_dir / f"stage_{k:02d}.jpg") for k in range(n_stages)):
        print("  All generated stage images exist — skipped (--resume)")
        return

    if dry_run:
        for k in range(n_stages):
            prompt_file = prompts_dir / f"stage_{k:02d}_image_prompt.txt"
            if k == 0:
                prompt = build_stage0_prompt(analysis, subject_key)
            else:
                prompt = build_stage_k_prompt(analysis, k, n_stages, milestones, subject_key)
            prompt_file.write_text(prompt, encoding="utf-8")
            req_type = "GENERATE_IMAGE" if k == 0 else "EDIT_IMAGE"
            print(f"  stage_{k:02d}: [DRY RUN] {req_type} prompt written to {prompt_file.name}")
        return

    # --- B0: Upload source image to get media_id for visual_asset entity ---
    imggen_meta_path = stages_dir / "flow_imggen.json"
    imggen_meta: dict = {}
    if resume and imggen_meta_path.exists():
        imggen_meta = json.loads(imggen_meta_path.read_text())
        print(f"  Reusing Flow imggen project {imggen_meta.get('img_pid')} / video {imggen_meta.get('img_vid')}")

    if not imggen_meta.get("source_media_id"):
        print("  Uploading source.jpg via /api/flow/upload-image...")
        source_media_id = upload_source_image(source_jpg)
        imggen_meta["source_media_id"] = source_media_id
        imggen_meta_path.write_text(json.dumps(imggen_meta, indent=2))
        print(f"  source_media_id: {source_media_id[:8]}...")
    else:
        source_media_id = imggen_meta["source_media_id"]
        print(f"  source_media_id: cached ({source_media_id[:8]}...)")

    # --- Create Flow project + video for image gen ---
    if not imggen_meta.get("img_pid"):
        subject_display = analysis.get("subject", "subject").title()
        style_desc = analysis.get("style_descriptor", "")
        entity_desc = (
            f"{subject_display} — {style_desc}. "
            + analysis.get("scene_context", {}).get("era", "")
            + " style, palette: " + str(analysis.get("scene_context", {}).get("palette", []))
            + ". Camera: " + analysis.get("scene_context", {}).get("camera_angle", "")
            + ". Lighting: " + analysis.get("scene_context", {}).get("lighting", "")
        ).strip(". ")

        r = api_post("/api/projects", {
            "name": f"fk-build-imggen-{slug_dir.name}",
            "description": "Phase B image gen workspace",
            "story": f"{subject_display} build — reverse-engineered stage images",
            "material": "realistic",
            "orientation": "VERTICAL",
            "characters": [],
        })
        img_pid = r["id"]
        r2 = api_post("/api/videos", {
            "project_id": img_pid,
            "title": f"{slug_dir.name}-stages",
            "video_story": "Build stage images",
            "display_order": 0,
            "orientation": "VERTICAL",
        })
        img_vid = r2["id"]

        # Create visual_asset entity (style reference = the finished subject)
        r3 = api_post("/api/characters", {
            "project_id": img_pid,
            "name": subject_display,
            "entity_type": "visual_asset",
            "description": entity_desc,
        })
        entity_id = r3["id"]

        # Patch media_id onto entity (API may not auto-link per vetranh pattern)
        api_patch(f"/api/characters/{entity_id}", {"media_id": source_media_id})
        print(f"  Created Flow imggen project {img_pid}, video {img_vid}, entity {entity_id[:8]}...")

        imggen_meta.update({"img_pid": img_pid, "img_vid": img_vid, "entity_id": entity_id, "scene_ids": []})
        imggen_meta_path.write_text(json.dumps(imggen_meta, indent=2))
    else:
        img_pid = imggen_meta["img_pid"]
        img_vid = imggen_meta["img_vid"]

    # --- B1: Create N scenes for stage image generation ---
    scene_ids: list[str] = imggen_meta.get("scene_ids", [])
    if not scene_ids:
        print(f"  Creating {n_stages} image gen scenes (ROOT + CONTINUATION chain)...")
        subject_display_name = analysis.get("subject", "subject").title()
        prev_sid: str | None = None
        for k in range(n_stages):
            prompt_file = prompts_dir / f"stage_{k:02d}_image_prompt.txt"
            if k == 0:
                prompt = build_stage0_prompt(analysis, subject_key)
            else:
                prompt = build_stage_k_prompt(analysis, k, n_stages, milestones, subject_key)
            prompt_file.write_text(prompt, encoding="utf-8")

            chain_type = "ROOT" if k == 0 else "CONTINUATION"
            r = api_post("/api/scenes", {
                "video_id": img_vid,
                "display_order": k,
                "prompt": prompt,
                "character_names": [subject_display_name],
                "chain_type": chain_type,
                "parent_scene_id": prev_sid,
            })
            sid = r["id"]
            scene_ids.append(sid)
            prev_sid = sid
            print(f"    scene_{k:02d}: {sid[:8]}... ({chain_type})")

        imggen_meta["scene_ids"] = scene_ids
        imggen_meta_path.write_text(json.dumps(imggen_meta, indent=2))

    # --- B2: Wave 1 — GENERATE_IMAGE for Stage 0 ---
    stage_0_file = stages_dir / "stage_00.jpg"
    if resume and image_file_ok(stage_0_file):
        print("  stage_00: skipped (exists, --resume)")
    else:
        print("  Wave 1 — GENERATE_IMAGE (Stage 0)...")
        api_post("/api/requests/batch", {"requests": [{
            "type": "GENERATE_IMAGE",
            "scene_id": scene_ids[0],
            "project_id": img_pid,
            "video_id": img_vid,
            "orientation": "VERTICAL",
        }]})
        ok = poll_imggen_wave(img_vid, "GENERATE_IMAGE")
        if not ok:
            halt_quota("GENERATE_IMAGE Wave 1 failed. Run /fk-doctor; resume with --resume after quota reset.")
        if not download_stage_image(scene_ids[0], stage_0_file):
            die("stage_00.jpg download failed or too small (<30KB). Check Flow scene.")
        crop_to_9_16_if_needed(stage_0_file)
        print(f"  stage_00: ok ({stage_0_file.stat().st_size // 1024}KB)")

    # --- B2: Waves 2..N — EDIT_IMAGE for Stages 1..N-1 ---
    for k in range(1, n_stages):
        stage_file = stages_dir / f"stage_{k:02d}.jpg"
        if resume and image_file_ok(stage_file):
            print(f"  stage_{k:02d}: skipped (exists, --resume)")
            continue

        # Verify parent stage image is ready (guard against partial resume)
        parent_file = stages_dir / f"stage_{k-1:02d}.jpg"
        if not image_file_ok(parent_file):
            die(f"stage_{k-1:02d}.jpg missing or too small — cannot submit Wave {k+1}. Check previous wave.")

        print(f"  Wave {k+1} — EDIT_IMAGE (Stage {k}: {milestones[k][0]}, {milestones[k][1]}%)...")
        api_post("/api/requests/batch", {"requests": [{
            "type": "EDIT_IMAGE",
            "scene_id": scene_ids[k],
            "project_id": img_pid,
            "video_id": img_vid,
            "orientation": "VERTICAL",
        }]})
        ok = poll_imggen_wave(img_vid, "EDIT_IMAGE")
        if not ok:
            halt_quota(f"EDIT_IMAGE Wave {k+1} (Stage {k}) failed. Run /fk-doctor; resume with --resume.")
        if not download_stage_image(scene_ids[k], stage_file):
            die(f"stage_{k:02d}.jpg download failed or too small. Check Flow scene {scene_ids[k]}.")
        crop_to_9_16_if_needed(stage_file)
        print(f"  stage_{k:02d}: ok ({stage_file.stat().st_size // 1024}KB)")

    print(f"  Phase B complete — {n_stages} stage images + Stage N copy in {stages_dir}")


# ---------- Stage C: Veo transition videos ----------

def upload_stage_image(stage_path: Path) -> str:
    """Upload a stage image via /api/flow/upload-image. Returns media_id (UUID).

    Mirrors upload_source_image (vetranh Step 0 pattern) — JSON body, not multipart.
    """
    return upload_source_image(stage_path)


def build_veo_prompt(analysis: dict, k: int, n_stages: int, milestones: list, subject_key: str) -> str:
    """Build a SHORT Veo i2v_fl prompt (target < 1100 chars).

    Veo gets layout + identity from the start+end frame images — text should only describe
    MOTION between them. Long prompts (>3KB) cause Veo workflow polling timeouts.
    Fix B: phase-specific action (not full sequence).
    Fix D: style anchor pulled from analysis.json to block Veo's default inventions.
    """
    subject_display = analysis.get("subject", "subject")
    milestone_from, pct_from = milestones[k]
    milestone_to, pct_to = milestones[k + 1]

    # When N==1, whole build happens in one clip — use __FULL__ key (workers + full sequence).
    if n_stages == 1:
        by_milestone = VEO_PHASE_ACTIONS_BY_MILESTONE.get(subject_key, {})
        phase_actions = by_milestone.get("__FULL__", VEO_PHASE_ACTIONS.get(subject_key, VEO_PHASE_ACTIONS["object/other"]))
    else:
        phase_actions = get_veo_phase_action(subject_key, milestone_to)

    # Fix D — style anchor from analysis (palette + descriptor) blocks Veo invention
    palette = analysis.get("scene_context", {}).get("palette", [])
    style_desc = analysis.get("style_descriptor", "")
    time_of_day = analysis.get("scene_context", {}).get("time_of_day", "")
    palette_str = ", ".join(palette[:5]) if palette else "neutral"
    tod_line = f" Time-of-day: {time_of_day}." if time_of_day else ""

    return f"""8-second hyper-fast timelapse of {subject_display} build, phase {k+1}/{n_stages}: {milestone_from} ({pct_from}%) → {milestone_to} ({pct_to}%).

Camera LOCKED on a tripod — never moves; identical to first-frame and last-frame images.
Last frame must match the provided end-frame image EXACTLY.

STYLE ANCHOR ({style_desc}): palette = {palette_str}. ABSOLUTELY DO NOT introduce: modern starburst/sputnik chandeliers, grey scandinavian furniture, abstract modern art, anything not present in the start+end frames.{tod_line}

HUMAN ELEMENT: workers ARE visible and welcome in frame — hands, tools, bodies doing the construction work. Show the crew transforming the space. The build feels human, not magic.

Action during these 8 seconds: {phase_actions}.

Style: realistic high-end timelapse, cinematic color grade, sharp focus, vertical 9:16.
Negative: text, typography, watermark, logos, camera movement, multiple shots, dialogue, modern chandelier, sputnik light, grey scandi style, abstract art."""


def poll_batch_until_done(vid: str, poll_every: int = 30, max_wait: int = 900) -> bool:
    """Poll /api/requests/batch-status until done:true. Returns True on full success."""
    start = time.time()
    while time.time() - start < max_wait:
        status = api_get(f"/api/requests/batch-status?video_id={vid}&type=GENERATE_VIDEO")
        if is_quota_error(json.dumps(status)):
            halt_quota(f"Quota error in batch-status: {status}")
        done = status.get("done", False)
        total = status.get("total", 0)
        completed = status.get("completed", 0)
        failed = status.get("failed", 0)
        print(f"  Veo progress: {completed}/{total} done, {failed} failed ({int(time.time()-start)}s elapsed)")
        if done:
            if status.get("all_succeeded") is False or failed > 0:
                print(f"  WARNING: {failed} Veo request(s) failed. Run /fk-doctor for details.")
                return False
            return True
        time.sleep(poll_every)
    print(f"  WARNING: Veo batch did not complete within {max_wait}s.")
    return False


def download_clip(scene_id: str, clip_path: Path) -> bool:
    """Download vertical_video_url from scene to clip_path. Returns True if successful."""
    scene = api_get(f"/api/scenes/{scene_id}")
    url = scene.get("vertical_video_url")
    if not url:
        print(f"  WARNING: No vertical_video_url for scene {scene_id}")
        return False
    urllib.request.urlretrieve(url, str(clip_path))
    return clip_path.exists() and clip_path.stat().st_size > 50_000


def phase_c_veo_transitions(slug_dir: Path, analysis: dict, n_stages: int, subject_key: str,
                             milestones: list, dry_run: bool, resume: bool) -> None:
    """Generate N Veo transition clips from stage images."""
    print(f"\n[Phase C] Generating {n_stages} Veo transition clips...")
    stages_dir = slug_dir / "stages"
    clips_dir = slug_dir / "clips"
    prompts_dir = slug_dir / "prompts"
    clips_dir.mkdir(exist_ok=True)
    prompts_dir.mkdir(exist_ok=True)

    flow_meta_path = clips_dir / "flow_project.json"
    upload_cache_path = clips_dir / ".upload_cache.json"

    # Check if all clips already exist (full resume)
    if resume and all(image_file_ok(clips_dir / f"clip_{k:02d}.mp4", 50_000) for k in range(n_stages)):
        print("  All clips exist — skipped (--resume)")
        return

    if dry_run:
        for k in range(n_stages):
            veo_prompt = build_veo_prompt(analysis, k, n_stages, milestones, subject_key)
            prompt_file = prompts_dir / f"transition_{k:02d}_video_prompt.txt"
            prompt_file.write_text(veo_prompt, encoding="utf-8")
            print(f"  clip_{k:02d}: [DRY RUN] Veo prompt written to {prompt_file.name}")
        return

    # Load or create Flow project
    if resume and flow_meta_path.exists():
        meta = json.loads(flow_meta_path.read_text())
        pid, vid = meta["pid"], meta["vid"]
        scene_ids = meta.get("scene_ids", [])
        print(f"  Reusing Flow project {pid}, video {vid}")
    else:
        # Create ephemeral project
        r = api_post("/api/projects", {
            "name": f"fk-build-{slug_dir.name}",
            "description": "Internal render workspace for fk-build",
            "story": f"{analysis.get('subject','object')} build timelapse",
            "material": "realistic",
            "characters": [],
        })
        pid = r["id"]
        r2 = api_post("/api/videos", {
            "project_id": pid,
            "title": slug_dir.name,
            "video_story": "Timelapse build",
            "display_order": 0,
            "orientation": "VERTICAL",
        })
        vid = r2["id"]
        scene_ids = []
        print(f"  Created Flow project {pid}, video {vid}")

    # Load or init upload cache
    upload_cache = {}
    if upload_cache_path.exists():
        upload_cache = json.loads(upload_cache_path.read_text())

    # Upload stage images (N+1 images for N transitions)
    print(f"  Uploading {n_stages + 1} stage images...")
    for k in range(n_stages + 1):
        stage_key = f"stage_{k:02d}"
        if stage_key in upload_cache:
            print(f"    {stage_key}: cached (media_id {upload_cache[stage_key][:8]}...)")
            continue
        stage_path = stages_dir / f"{stage_key}.jpg"
        if not stage_path.exists():
            die(f"{stage_key}.jpg missing — run Phase B first.")
        media_id = upload_stage_image(stage_path)
        upload_cache[stage_key] = media_id
        upload_cache_path.write_text(json.dumps(upload_cache, indent=2))
        print(f"    {stage_key}: uploaded → {media_id[:8]}...")

    # Create N scenes (or reuse from resume)
    if not scene_ids:
        print(f"  Creating {n_stages} scenes...")
        for k in range(n_stages):
            veo_prompt = build_veo_prompt(analysis, k, n_stages, milestones, subject_key)
            prompt_file = prompts_dir / f"transition_{k:02d}_video_prompt.txt"
            prompt_file.write_text(veo_prompt, encoding="utf-8")
            r = api_post("/api/scenes", {
                "video_id": vid,
                "display_order": k,
                "prompt": f"Transition stage {k} to stage {k+1} of {analysis.get('subject','object')} build.",
                "video_prompt": veo_prompt,
                "transition_prompt": veo_prompt,
                "character_names": [],
                "chain_type": "ROOT",
                "parent_scene_id": None,
            })
            sid = r["id"]
            scene_ids.append(sid)
            # Wire start + end frame images — native HTTP PATCH per skills/fk-gen-chain-videos.md
            import urllib.request as _ur
            patch_payload = json.dumps({
                "vertical_image_media_id": upload_cache[f"stage_{k:02d}"],
                "vertical_end_scene_media_id": upload_cache[f"stage_{k+1:02d}"],
                "vertical_image_status": "COMPLETED",
            }).encode("utf-8")
            patch_req = _ur.Request(
                f"{API}/api/scenes/{sid}",
                data=patch_payload,
                headers={"Content-Type": "application/json"},
                method="PATCH",
            )
            with _ur.urlopen(patch_req, timeout=30) as _resp:
                if _resp.status >= 400:
                    raise RuntimeError(f"PATCH /api/scenes/{sid} failed: HTTP {_resp.status}")
            print(f"    scene {k}: id={sid[:8]}... wired stage_{k:02d}→stage_{k+1:02d}")

        # Save project meta for resume
        flow_meta_path.write_text(json.dumps({"pid": pid, "vid": vid, "scene_ids": scene_ids}, indent=2))

    # Probe clip_00 first
    print("  Probing clip_00...")
    clip_00 = clips_dir / "clip_00.mp4"
    if not (resume and image_file_ok(clip_00, 50_000)):
        api_post("/api/requests/batch", {"requests": [{
            "type": "GENERATE_VIDEO",
            "scene_id": scene_ids[0],
            "project_id": pid,
            "video_id": vid,
            "orientation": "VERTICAL",
        }]})
        ok = poll_batch_until_done(vid)
        if not ok:
            die("Probe clip failed. Run /fk-doctor for details.")
        if not download_clip(scene_ids[0], clip_00):
            die("Failed to download clip_00 after probe.")
        print(f"  clip_00: downloaded ({clip_00.stat().st_size // 1024}KB)")

    # Submit remaining N-1 clips
    if n_stages > 1:
        remaining = [
            {"type": "GENERATE_VIDEO", "scene_id": scene_ids[k], "project_id": pid, "video_id": vid, "orientation": "VERTICAL"}
            for k in range(1, n_stages)
            if not (resume and image_file_ok(clips_dir / f"clip_{k:02d}.mp4", 50_000))
        ]
        if remaining:
            print(f"  Submitting {len(remaining)} remaining Veo requests...")
            api_post("/api/requests/batch", {"requests": remaining})
            poll_batch_until_done(vid)

    # Download all clips
    print("  Downloading clips...")
    for k in range(n_stages):
        clip_path = clips_dir / f"clip_{k:02d}.mp4"
        if resume and image_file_ok(clip_path, 50_000):
            print(f"  clip_{k:02d}: skipped (--resume)")
            continue
        if download_clip(scene_ids[k], clip_path):
            print(f"  clip_{k:02d}: downloaded ({clip_path.stat().st_size // 1024}KB)")
        else:
            print(f"  clip_{k:02d}: WARNING — download failed or file too small")

    print(f"  Flow project: {pid}  video: {vid}")


# ---------- Stage D: Concat + music + brand ----------

def phase_d_concat(slug_dir: Path, n_stages: int, dry_run: bool, speed: float = 0.8) -> Path:
    """Concat N clips with 0.5s tail trim, then slow by `speed` factor.

    Veo clips are fast-forward by nature. Slowing to 0.8x adds ~25% duration and
    a calmer pace while keeping the timelapse feel. speed=1.0 skips slowdown.
    """
    print(f"\n[Phase D-1] Concatenating clips (speed={speed}x)...")
    clips_dir = slug_dir / "clips"
    concat_txt = clips_dir / "concat.txt"
    raw_mp4 = slug_dir / "concat_raw.mp4"  # intermediate before slowdown
    final_mp4 = slug_dir / "final.mp4"

    if dry_run:
        print("  [DRY RUN] Would concat clips → final.mp4")
        return final_mp4

    # Build concat list with 0.5s tail trim on all-but-last
    with open(concat_txt, "w") as f:
        for k in range(n_stages):
            clip = clips_dir / f"clip_{k:02d}.mp4"
            if not clip.exists():
                die(f"clip_{k:02d}.mp4 missing — Phase C incomplete.")
            if k < n_stages - 1:
                dur = ffprobe_dur(clip)
                trim_dur = max(round(dur - 0.5, 2), 1.0)
                trim_clip = clips_dir / f"clip_{k:02d}_trim.mp4"
                run(["ffmpeg", "-y", "-i", str(clip), "-t", str(trim_dur), "-c", "copy", str(trim_clip)])
                f.write(f"file '{trim_clip.name}'\n")
            else:
                f.write(f"file '{clip.name}'\n")

    # 1) Fast concat (stream copy)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-c", "copy", "-movflags", "+faststart", str(raw_mp4)],
        cwd=clips_dir)

    # 2) Slow down if speed != 1.0 (re-encode required for setpts)
    if abs(speed - 1.0) > 0.01:
        run(["ffmpeg", "-y", "-i", str(raw_mp4),
             "-vf", f"setpts=PTS/{speed}",
             "-an",  # silent — BGM mixed later in D3
             "-c:v", "libx264", "-crf", "18", "-r", "24", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(final_mp4)])
        raw_mp4.unlink(missing_ok=True)  # remove intermediate
    else:
        raw_mp4.rename(final_mp4)

    dur = ffprobe_dur(final_mp4)
    print(f"  final.mp4: {dur:.1f}s @ speed={speed}x ({final_mp4.stat().st_size // 1024}KB)")
    return final_mp4


def phase_d_music(slug_dir: Path, analysis: dict, subject_key: str, dry_run: bool) -> Path | None:
    """Generate Lyria music, transcode to MP3. Returns path or None."""
    print("\n[Phase D-2] Generating music (Lyria)...")
    music_dir = slug_dir / "music"
    music_dir.mkdir(exist_ok=True)
    track_mp3 = music_dir / "track.mp3"

    if dry_run:
        print("  [DRY RUN] Would generate Lyria music → track.mp3")
        return None

    if track_mp3.exists() and track_mp3.stat().st_size > 10_000:
        print(f"  track.mp3: already exists — skipped")
        return track_mp3

    color = MUSIC_COLORS.get(subject_key, "warm, satisfying, transformational")
    music_prompt = (
        f"Slow cinematic instrumental, gentle warm strings + soft piano, building swell over 30 seconds, "
        f"satisfying transformation mood, organic and uplifting. NO drums, NO vocals, NO lyrics, NO percussion. "
        f"Mood: {color}."
    )
    try:
        r = api_post("/api/gemini/browser/generate-music", {
            "prompt": music_prompt,
            "model": "Nhanh",
            "timeout": 120,
            "headless": True,
        }, timeout=150)
        lyria_mp4 = r.get("path")
        if not lyria_mp4:
            raise RuntimeError(f"Lyria returned no path: {r}")
        run(["ffmpeg", "-y", "-i", str(ROOT / lyria_mp4),
             "-vn", "-c:a", "libmp3lame", "-q:a", "4", str(track_mp3)])
        print(f"  track.mp3: {track_mp3.stat().st_size // 1024}KB")
        return track_mp3
    except Exception as e:
        # Per skills/fk-gen-music.md, the canonical path is /api/gemini/browser/generate-music (Lyria).
        # No Suno fallback — if Lyria is down, final video is silent. User can run /fk-gen-music
        # manually later and re-mux, or invoke `--resume` after Lyria recovers.
        print(f"  Lyria failed ({e}). Skipping music — final video will be silent.")
        print(f"  → Fix: check skills/fk-gen-music.md (Path A) + retry, OR run /fk-doctor.")
        return None


def phase_d_mix(slug_dir: Path, final_mp4: Path, track_mp3: Path | None, dry_run: bool) -> Path:
    """Mix BGM into final.mp4 → final_with_music.mp4."""
    print("\n[Phase D-3] Mixing BGM...")
    out = slug_dir / "final_with_music.mp4"

    if dry_run:
        print("  [DRY RUN] Would mix BGM → final_with_music.mp4")
        return out

    if track_mp3 is None or not track_mp3.exists():
        import shutil
        shutil.copy2(final_mp4, out)
        print("  No music — copied final.mp4 → final_with_music.mp4")
        return out

    dur = ffprobe_dur(final_mp4)
    run([
        "ffmpeg", "-y", "-i", str(final_mp4), "-i", str(track_mp3),
        "-filter_complex",
        f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{dur},volume=0.18[bg];"
        "[0:a]volume=1.0[sfx];"
        "[sfx][bg]amix=inputs=2:duration=first:dropout_transition=0[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(out),
    ])
    print(f"  final_with_music.mp4: {out.stat().st_size // 1024 // 1024}MB")
    return out


def phase_d_brand(slug_dir: Path, with_music_mp4: Path, channel: str | None, dry_run: bool) -> Path:
    """Apply brand logo overlay → final_branded.mp4."""
    out = slug_dir / "final_branded.mp4"

    if dry_run:
        print("\n[Phase D-4] [DRY RUN] Would apply brand logo → final_branded.mp4")
        return out

    if not channel:
        import shutil
        shutil.copy2(with_music_mp4, out)
        print("\n[Phase D-4] No --channel given — brand skipped. Output: final_with_music.mp4")
        return out

    icon = ROOT / "youtube" / "channels" / channel / f"{channel}_icon.png"
    if not icon.exists():
        import shutil
        shutil.copy2(with_music_mp4, out)
        print(f"\n[Phase D-4] WARNING: icon not found at {icon} — brand skipped.")
        return out

    print(f"\n[Phase D-4] Applying brand logo ({channel})...")
    size, pad = 140, 28  # for 1080×1920 vertical
    run([
        "ffmpeg", "-y",
        "-i", str(with_music_mp4), "-i", str(icon),
        "-filter_complex",
        f"[1:v]scale={size}:{size},format=rgba[icon];[0:v][icon]overlay=W-w-{pad}:H-h-{pad}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "24", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart",
        str(out),
    ])
    print(f"  final_branded.mp4: {out.stat().st_size // 1024 // 1024}MB")
    return out


def write_readme(slug_dir: Path, analysis: dict, n_stages: int, channel: str | None,
                 final_path: Path, args_str: str) -> None:
    from datetime import datetime, timezone
    subject = analysis.get("subject", "?")
    subtype = analysis.get("subtype", "")
    dur = ffprobe_dur(final_path) if final_path.exists() else 0
    music_info = "track.mp3" if (slug_dir / "music" / "track.mp3").exists() else "none"
    brand_info = channel if channel else "none"
    flow_meta_path = slug_dir / "clips" / "flow_project.json"
    flow_info = ""
    if flow_meta_path.exists():
        m = json.loads(flow_meta_path.read_text())
        flow_info = f"project {m.get('pid','')} / video {m.get('vid','')}"

    readme = f"""# fk-build · {slug_dir.name}

- **Subject:** {subject}{' / ' + subtype if subtype else ''}
- **Stages:** {n_stages}
- **Source image:** source.jpg
- **Final:** {final_path.name} ({dur:.0f}s, 1080x1920, vertical)
- **Music:** {music_info}
- **Brand:** {brand_info}
- **Flow project:** {flow_info}
- **Created:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
- **Args used:** {args_str}

## How to re-render
```
/fk-build source.jpg --slug {slug_dir.name} --stages {n_stages} [--resume]
```
"""
    (slug_dir / "README.md").write_text(readme, encoding="utf-8")


# ---------- Entry point ----------

def main():
    parser = argparse.ArgumentParser(
        description="fk-build render pipeline — Flow image gen + Veo transitions + concat + music + brand",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--image", help="Path to source image (required for first run)")
    parser.add_argument("--slug", required=True, help="Output slug (e.g. house_modern_villa_001)")
    parser.add_argument("--stages", type=int, default=1, choices=range(1, 9), metavar="N",
                        help="Number of build stages (1-8, default 1 = single one-shot Veo clip with workers visible, full build compressed in ~16s @ speed 0.5). Bump N for richer multi-stage timelapse.")
    parser.add_argument("--speed", type=float, default=0.5, metavar="X",
                        help="Final concat playback speed (default 0.5 = half-speed, twice as long; "
                             "0.8 = ~25%% longer than raw Veo; 1.0 = original Veo speed)")
    parser.add_argument("--subject", default="house",
                        choices=["house", "garden", "room", "building",
                                 "object/food", "object/furniture", "object/electronics",
                                 "object/sculpture", "object/painting", "object/model",
                                 "object/instrument", "object/other"],
                        help="Subject type (use compound key for objects, e.g. object/food)")
    parser.add_argument("--channel", default=None,
                        help="Brand channel slug (e.g. lamplit-library). Omit for no branding.")
    parser.add_argument("--no-music", action="store_true", help="Skip BGM generation")
    parser.add_argument("--no-brand", action="store_true", help="Skip brand logo overlay")
    parser.add_argument("--resume", action="store_true", help="Skip stages where output already exists")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts only; do not call Flow image gen or Veo")
    parser.add_argument("--no-caption", action="store_true", help="Skip Phase E caption generation")
    args = parser.parse_args()

    slug_dir = OUTPUT_BASE / args.slug
    slug_dir.mkdir(parents=True, exist_ok=True)

    # Handle source image
    if args.image:
        src = Path(args.image)
        if not src.exists():
            die(f"Image not found: {src}")
        import shutil
        source_jpg = slug_dir / "source.jpg"
        if not source_jpg.exists():
            shutil.copy2(src, source_jpg)
            print(f"Copied source → {source_jpg}")

    # Load analysis.json (written by /fk-build Phase A)
    analysis_path = slug_dir / "analysis.json"
    if not analysis_path.exists():
        die(f"analysis.json not found at {analysis_path}.\nRun /fk-build via the Claude skill first to complete Phase A (vision analysis).")
    analysis = json.loads(analysis_path.read_text())

    subject_key = args.subject  # already compound for objects
    milestones = get_milestones(subject_key, args.stages)

    if not args.dry_run:
        health_check()

    # Phase B — Stage images
    phase_b_generate_stages(slug_dir, analysis, args.stages, subject_key, milestones,
                             args.dry_run, args.resume)

    # Phase C — Veo transitions
    phase_c_veo_transitions(slug_dir, analysis, args.stages, subject_key, milestones,
                             args.dry_run, args.resume)

    # Phase D — Concat + music + brand
    final_mp4 = phase_d_concat(slug_dir, args.stages, args.dry_run, speed=args.speed)

    track_mp3 = None
    if not args.no_music:
        track_mp3 = phase_d_music(slug_dir, analysis, subject_key, args.dry_run)

    with_music = phase_d_mix(slug_dir, final_mp4, track_mp3, args.dry_run)

    effective_channel = None if args.no_brand else args.channel
    final_branded = phase_d_brand(slug_dir, with_music, effective_channel, args.dry_run)

    # Write README
    args_str = " ".join(sys.argv[1:])
    if not args.dry_run:
        write_readme(slug_dir, analysis, args.stages, effective_channel, final_branded, args_str)

    # Phase E — Caption (optional)
    if args.no_caption or args.dry_run:
        if args.no_caption:
            print("\n[Phase E] Caption skipped (--no-caption).")
    else:
        print("\n[Phase E] Caption: run `/fk-gen-caption` against final_branded.mp4 in Flow UI.")
        print("  Subject context for caption: "
              f"{analysis.get('subject','')} / {analysis.get('style_descriptor','')} / "
              f"{analysis.get('scene_context',{}).get('era','')} / "
              f"{analysis.get('stage_0_archetype','')[:80]}")

    print(f"\nDone: {final_branded}")
    print(f"Output dir: {slug_dir}")


if __name__ == "__main__":
    main()
