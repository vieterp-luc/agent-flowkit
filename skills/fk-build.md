# fk-build — 1 image → vertical timelapse Short (auto-classify house/garden/room/building/object → reverse-engineer N build stages → Flow chained images + Veo transitions + instrumental BGM)

Universal orchestrator: turn 1 finished-subject photo into a 9:16 "before → built" timelapse Short (~32-45s). Auto-classifies subject (house, garden, room, building, object), reverse-engineers N stages with LOCK BLOCKS for continuity, generates Flow chained stage images (GENERATE_IMAGE + EDIT_IMAGE waves) + Veo first+last-frame transition videos, mixes instrumental BGM, optionally brands. **Silent timelapse — no narrator/TTS.**

Usage:
```
/fk-build <image_path_or_url> [flags]
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--stages N` | 3 | Number of build stages (2–8). Produces N Veo clips. |
| `--speed X` | 0.8 | Final concat playback speed (1.0 = raw Veo, 0.8 = ~25% longer, calmer pacing; 0.5 = half-speed). |
| `--subject {auto,house,garden,room,building,object}` | auto | Override auto-classify |
| `--object-subtype {auto,food,furniture,electronics,sculpture,model,instrument,painting}` | auto | Force when subject=object |
| `--start-state NAME` | auto | Override Stage 0 archetype (e.g. "abandoned fish pond") |
| `--slug SLUG` | auto-derived | Override auto-slug |
| `--output DIR` | `output/fk_build/` | Override output root |
| `--channel NAME` | _(none)_ | Brand channel slug (e.g. `lamplit-library`). **Default = no branding.** |
| `--no-music` | false | Skip BGM generation |
| `--no-brand` | false | Skip logo overlay (auto-true when `--channel` not given) |
| `--dry-run` | false | Analyze + print prompts only; do NOT call Flow image gen or Veo |
| `--resume` | false | Skip stages where output already exists |

## Identity

| Item | Value |
|------|-------|
| Skill ID | `fk-build` |
| Skill file | `skills/fk-build.md` |
| Orientation | VERTICAL 1080×1920 |
| Default N | **3** stages → 3 Veo clips × ~8s ≈ 24s raw, ≈ **29s** sau slowdown 0.8× |
| Output root | `output/fk_build/<slug>/` |
| Image generator | Flow `/fk-gen-images` (GENERATE_IMAGE + chained EDIT_IMAGE waves) — modeled on `fk-video-vetranh` |
| Video generator | Flow + Veo (start+end frame, via `/fk-gen-chain-videos` pattern) |
| Music | Gemini Lyria "Nhanh" 30s instrumental — `/fk-gen-music` Path A only (no Suno) |
| Slug format | `<subject>_<style_descriptor>_<NNN>` |

---

## Pre-flight

```bash
curl -s http://127.0.0.1:8100/health   # must return {"extension_connected": true}
```
If health fails → invoke the doctor command (`/fk-doctor` on Claude Code, `/fk:doctor` on Gemini CLI) before anything else.
Check Flow credits before the run: if low → warn user and suggest waiting for quota reset.

---

## Phase A — Analyze Image + Build LOCK BLOCKS

### A0 — Input validation
- Accept local path or HTTPS URL. URL → download to `/tmp/fk_build_in_<hash>.jpg`.
- Abort if file missing, > 10 MB, or MIME not image/jpeg/png/webp.
- Copy input → `output/fk_build/<slug>/source.jpg`.

### A1 — Subject classification (skip if `--subject` given)

Run a single agent vision call (Claude vision / Gemini vision / any multimodal model in use). Decision tree:

```
Q1: Dominated by a single building structure (facade + roofline visible, exterior shot)?
    → single residence (1-4 floors, yard) → house
    → multi-story tower / commercial / institutional → building
Q2: Interior space (floor + walls + ceiling visible)? → room
Q3: Outdoor landscaped area (plants/hardscape/sky, no dominant single building)? → garden
Q4: Single discrete crafted thing dominating frame? → object → run Q5
Q5 (object sub-type):
    - Edible / on plate/bowl         → food
    - Chair/table/cabinet/sofa shape → furniture
    - Device with screen/buttons     → electronics
    - Statue/bust/abstract carved    → sculpture
    - Canvas/framed 2D art           → painting
    - Lego/gunpla/model/figurine     → model
    - Guitar/violin/drum/synth       → instrument
    - None of above                  → other
```

Print classification + 1-line reasoning. **No confirmation prompt — proceed immediately.**

### A2 — Subject-specific analysis (always run)

**HOUSE / BUILDING:** architectural style, scale (floors), primary materials, facade color palette (3-5 colors), distinctive features, surroundings (street/lawn/skyline), lighting, camera angle, era/mood.
- LAYOUT MAP zones: roof / facade / entrance / surrounding ground / neighboring buildings-trees / sky.
- INVENTORY name: **MATERIAL INVENTORY** — every visible material with location + finish.

**ROOM:** room type, design style, color palette, materials/textures, key furniture, decor/lighting, architectural features (window/door/ceiling), camera angle.
- LAYOUT MAP zones: floor / each visible wall / ceiling / window / door / each furniture piece.
- INVENTORY name: **FURNITURE INVENTORY** — every furniture piece + decor with position, material, color.

**GARDEN:** garden type, plant species, hardscape, water features, lighting fixtures, furniture/decor, surroundings, sky, camera angle, mood.
- LAYOUT MAP zones: ground areas (lawn/path/pond/beds) / perimeter (fence/wall) / overhead (trees/sky) / decor clusters.
- INVENTORY name: **PLANT INVENTORY** — every plant species + position + mature size + container (verbatim per build-garden rules).

**OBJECT:** sub-type, material composition, dominant color palette (2-4), surface finish, distinctive features, scale (cm), camera framing, surface object rests on, background, lighting.
- LAYOUT MAP zones: principal sub-regions of the object in frame (e.g. cake: tiers; lego castle: keep/walls/towers/gates).
- INVENTORY name: **OBJECT/COMPONENT INVENTORY** — schema per component:
  ```
  - Component <X>: <name> — <position in frame %>, <size %frame>,
    <material>, <color/finish>, <surface treatment>.
    At Stage 0 = <raw-material form>.
    At Stage N = <final form visible in input>.
  ```
  Sub-type examples: food → raw ingredients; furniture → raw lumber + tools; electronics → scattered components on antistatic mat; sculpture → uncarved stone block; painting → blank canvas + paints; model → sealed box / loose sprues; instrument → wood blanks + luthier tools.

### A3 — Defensive guardrails (append to every LOCK BLOCK preamble)
```
VERTICAL PORTRAIT 9:16 (1080×1920) framing.
STRICTLY NO TEXT, NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS in the image.
```

### A4 — Stage 0 archetype selection

| Subject | Default Stage 0 |
|---------|----------------|
| house | Decayed/dilapidated shell — peeling paint, broken windows, overgrown lawn |
| garden | Auto-pick from build-garden start-states library (match existing features) |
| room | Bare empty shell — stripped plaster walls, bare subfloor, single bulb hanging |
| building | Empty bare plot of graded earth + temp fencing + materials staged |
| object / food | Raw ingredients in bowls / mise-en-place on same surface as input |
| object / furniture | Pile of raw lumber + tools (saw, clamps, sandpaper) on workshop floor |
| object / electronics | Scattered components (PCB, chips, screen, battery) on antistatic mat |
| object / sculpture | Raw uncarved stone block / clay lump + chisels on pedestal |
| object / painting | Blank stretched canvas on easel + paint tubes + brushes + palette |
| object / model | Sealed box / loose sprues + manual scattered on building mat |
| object / instrument | Raw wood blanks + strings + tuning pegs + luthier tools |
| object / other | Raw materials + tools on neutral surface |

Override via `--start-state`. Stage 0 MUST look RADICALLY DIFFERENT from input (the "same property?" rule). Wasteland character dominates 80-90% visual weight; future layout hints ≤ 10%.

### A5 — Write analysis.json
```json
{
  "subject": "house",
  "subtype": null,
  "style_descriptor": "modern_villa",
  "slug": "house_modern_villa_001",
  "stage_0_archetype": "Decayed shell — peeling paint, broken windows, overgrown lot",
  "scene_context": {
    "era": "contemporary",
    "palette": ["#ffffff", "#3a3a3a", "#8b7355"],
    "camera_angle": "wide-angle eye-level 3/4 view",
    "lighting": "soft overcast daylight",
    "surroundings_locked": "mature oak tree at right frame, neighboring house partially visible at left"
  },
  "lock_blocks": {
    "layout_map": "<<LAYOUT MAP prose — paste verbatim in every prompt>>",
    "inventory": "<<MATERIAL/PLANT/FURNITURE/OBJECT INVENTORY prose — paste verbatim>>"
  }
}
```

Also write `analysis.md` as human-readable mirror for debugging.

### A6 — Slug derivation
```python
slug = f"{subject}_{style_descriptor}_{counter:03d}"
# counter = next integer not already present in output/fk_build/<subject>_*/
```

---

## Phase B — Stage Image Generation (Flow chained — modeled on `fk-video-vetranh`)

**Generator: Flow `/fk-gen-images`** — GENERATE_IMAGE (Stage 0) + chained EDIT_IMAGE (Stages 1..N-1). Stage N = `source.jpg` — the original input image, already final, NOT regenerated.

### B0 — Upload input image + create Flow project

```bash
# 1. Upload source.jpg to get a media_id for the visual_asset entity
curl -X POST http://127.0.0.1:8100/api/flow/upload-image \
  -H "Content-Type: application/json" \
  -d '{"file_path": "output/fk_build/<slug>/source.jpg", "file_name": "<slug>_source.jpg"}'
# → {"media_id": "<UUID>"}  — save as SOURCE_MEDIA_ID

# 2. Create ephemeral Flow project (shared for image gen; Phase C creates its own)
curl -X POST http://127.0.0.1:8100/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fk-build-imggen-<slug>",
    "description": "Phase B image gen workspace",
    "story": "<subject> build — reverse-engineered stage images",
    "material": "realistic",
    "orientation": "VERTICAL",
    "characters": []
  }'
# → save project_id → IMG_PID

curl -X POST http://127.0.0.1:8100/api/videos \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<IMG_PID>",
    "title": "<slug>-stages",
    "video_story": "Build stage images",
    "display_order": 0,
    "orientation": "VERTICAL"
  }'
# → save video_id → IMG_VID

# 3. Create visual_asset entity (the finished subject as style reference)
curl -X POST http://127.0.0.1:8100/api/characters \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<IMG_PID>",
    "name": "<Slug Subject>",
    "entity_type": "visual_asset",
    "description": "<description from analysis.json scene_context — subject, style, colors, composition>"
  }'
# → save entity_id → ENTITY_ID

# 4. Patch media_id onto entity (API may not auto-link)
curl -X PATCH http://127.0.0.1:8100/api/characters/<ENTITY_ID> \
  -H "Content-Type: application/json" \
  -d '{"media_id": "<SOURCE_MEDIA_ID>"}'
```

Save `IMG_PID`, `IMG_VID`, `ENTITY_ID`, `SOURCE_MEDIA_ID` to `stages/flow_imggen.json`.

### B1 — Create N scenes for stage image generation

For k = 0..N-1 (N scenes, one per generated stage):

```bash
curl -X POST http://127.0.0.1:8100/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "<IMG_VID>",
    "display_order": <k>,
    "prompt": "<STAGE_K_IMAGE_PROMPT>",
    "character_names": ["<Slug Subject>"],
    "chain_type": "<ROOT if k==0, else CONTINUATION>",
    "parent_scene_id": <null if k==0, else SID_{k-1}>
  }'
# → save scene_id → IMG_SID_k
```

Scene k=0 → `chain_type: "ROOT"`, `parent_scene_id: null` → will use GENERATE_IMAGE.
Scenes k=1..N-1 → `chain_type: "CONTINUATION"`, `parent_scene_id: IMG_SID_{k-1}` → will use EDIT_IMAGE (auto-chains from parent's completed image).

Save all `IMG_SID_*` to `stages/flow_imggen.json`.

**If ghost scene with duplicate `display_order` appears:** DELETE before submitting gen requests (per vetranh "Lỗi thường gặp").

### B2 — Generate images: 4 waves sequential

| Wave | Scene | Request type | Condition |
|------|-------|-------------|-----------|
| 0 | _(preflight)_ | _(upload only — B0 above)_ | Stage N already exists as source.jpg |
| 1 | Stage 0 (ROOT) | `GENERATE_IMAGE` | Wasteland / raw-materials state |
| 2..N | Stages 1..N-1 | `EDIT_IMAGE` | Chained from previous scene's completed image |

Submit Wave 1 first, poll until `done: true`, then submit each subsequent wave:

```bash
# Wave 1 — Stage 0 (GENERATE_IMAGE)
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{"requests":[{
    "type": "GENERATE_IMAGE",
    "scene_id": "<IMG_SID_0>",
    "project_id": "<IMG_PID>",
    "video_id": "<IMG_VID>",
    "orientation": "VERTICAL"
  }]}'

# Poll until done (10-15s interval):
curl -s "http://127.0.0.1:8100/api/requests/batch-status?video_id=<IMG_VID>&type=GENERATE_IMAGE"
# Wait for: "done": true
# On QUOTA error → HALT: "Quota hit at Stage 0. Run the doctor command (/fk-doctor on Claude Code, /fk:doctor on Gemini CLI); resume with --resume after quota reset."

# Wave 2 — Stage 1 (EDIT_IMAGE, auto-chains from Stage 0's image)
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{"requests":[{
    "type": "EDIT_IMAGE",
    "scene_id": "<IMG_SID_1>",
    "project_id": "<IMG_PID>",
    "video_id": "<IMG_VID>",
    "orientation": "VERTICAL"
  }]}'

# Poll EDIT_IMAGE status:
curl -s "http://127.0.0.1:8100/api/requests/batch-status?video_id=<IMG_VID>&type=EDIT_IMAGE"
# Repeat for Wave 3 (Stage 2), Wave 4 (Stage 3), ...
```

Each EDIT_IMAGE wave: the Flow worker auto-resolves `source_media_id` from the parent scene's `vertical_image_media_id`. No manual chaining needed.

**Stage N** (the "100% final" state) = `source.jpg` — already on disk. Copy to `stages/stage_<N>.jpg`:
```bash
cp output/fk_build/<slug>/source.jpg output/fk_build/<slug>/stages/stage_$(printf "%02d" $N).jpg
```

### B3 — Download generated stage images

After all waves complete, for each scene k = 0..N-1:
```bash
# Get scene to find image URL
curl -s "http://127.0.0.1:8100/api/scenes/<IMG_SID_k>"
# → vertical_image_url

# Download to stages/stage_NN.jpg
curl -sL "<vertical_image_url>" -o output/fk_build/<slug>/stages/stage_<NN>.jpg
```

### B4 — Per-stage verification

```bash
SIZE=$(stat -f%z "stages/stage_NN.jpg")
[ "$SIZE" -lt 30000 ] && echo "WARNING: stage_NN too small (<30KB) — likely blank or failed"
```
Check aspect ratio; if not 9:16, center-crop in-place:
```bash
ffmpeg -y -i stages/stage_NN.jpg -vf "crop=ih*9/16:ih" stages/stage_NN.jpg
```

### N=4 stage milestone table (default — interpolate proportionally for other N)

| Subject | Stage 0 | Stage 1 (25%) | Stage 2 (50%) | Stage 3 (75%) | Stage 4 (100%) |
|---------|---------|---------------|---------------|---------------|----------------|
| house | Decayed shell | Demolished + scaffolding | Walls/roof rebuilt + primed | Windows, doors, paint, landscaping | Final = input |
| garden | Wasteland | Cleared + graded | Hardscape installed | Softscape mid-growth | Final = input |
| room | Bare shell | Walls painted + flooring laid | Major furniture in place | Decor + soft furnishings + lighting | Final = input |
| building | Empty plot | Foundation + ground floor frame | Mid-rise frame + partial skin | Curtain wall + facade complete | Final = input |
| object/food | Raw ingredients | Cake baked (unfrosted layers) | Crumb-coated + base frosting | Decorated + piping | Final = input |
| object/furniture | Raw lumber + tools | Pieces cut + dry-fit | Joinery glued + clamped | Sanded + first stain coat | Final = input |
| object/electronics | Components scattered | PCB + frame assembled | Screen + battery installed | Closed body, screen on | Final = input |
| object/sculpture | Raw block + chisels | Rough form blocked out | Mid-detail carving | Fine detail + initial polish | Final = input |
| object/painting | Blank canvas | Underpainting / sketch | Mid-layer color blocking | Detail pass + highlights | Final = input |
| object/model | Sealed box / sprues | Base + lower walls | Mid-structure + sub-assemblies | Towers + roof + flags partial | Final = input |
| object/instrument | Wood blanks + tools | Body shaped + top glued | Neck attached + fretboard | Hardware + finish coat | Final = input |

### Stage 0 image prompt template

```
[VERTICAL PORTRAIT 9:16, 1080×1920]
Transform this image so the {{subject_display}} is COMPLETELY removed and
replaced with {{stage_0_archetype_description}}.

LOCKED — keep IDENTICAL to original:
- Camera angle, focal length, framing
- Sky / weather / time-of-day / ambient lighting
- {{locked_surroundings}}:
    house/building → fence/wall boundary, neighboring buildings, external trees, sidewalk
    garden         → fence/wall, neighboring overhanging trees, building edges at frame border
    room           → walls, ceiling, floor subfloor, window/door openings, architectural shell
    object         → surface the object rests on, background, table/easel/board, lighting setup

{{LAYOUT_MAP}}

Stage 0 must look RADICALLY DIFFERENT from input — wasteland / raw-materials
character dominates 80-90% visual weight; future layout hints ≤ 10%.
{{SUBJECT_SPECIFIC_STAGE_0_RULE}}
DO NOT introduce components/plants/materials not listed in INVENTORY.
STRICTLY NO TEXT, NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS.
Photorealistic, ultra-detailed, cinematic. IDENTICAL camera angle to input.
```

Subject-specific Stage 0 rules:
- **house:** "Show DECAYED state — peeling paint, broken windows, overgrown yard. Lot dimensions + house footprint preserved."
- **garden:** "Apply build-garden Stage 0 rule: pond pit visible if final has pond; wasteland surface dominates."
- **room:** "Show bare empty shell — stripped walls, bare subfloor, single bulb hanging, NO furniture."
- **building:** "Show empty bare plot of graded earth with temp construction fencing, materials staged on side."
- **object:** "Show ONLY the raw materials + tools needed to make this object, on the same surface as input. Finished object MUST be absent."

### Stage k image prompt template (k = 1..N-1, chained EDIT_IMAGE from Stage k-1)

```
[VERTICAL PORTRAIT 9:16, 1080×1920]
Starting from this image (Stage {{k-1}} of {{subject_display}} build —
showing {{brief_recap_stage_k_minus_1}}), advance it to Stage {{k}} —
approximately {{percent}}% complete at the "{{milestone_name}}" milestone.

LOCKED — keep IDENTICAL to Stage {{k-1}}:
- Camera angle, focal length, framing
- Sky / lighting / surroundings
- {{locked_surroundings_per_subject}}
- Everything already built / installed in Stage {{k-1}}

INHERITED from Stage {{k-1}} (must look IDENTICAL at these elements):
- {{list_inherited}}

NEW IN Stage {{k}} (added/changed in this step):
- {{list_new}}

STILL MISSING in Stage {{k}} (appears in later stages — DO NOT add yet):
- {{list_missing}}

{{LAYOUT_MAP}}

{{INVENTORY}}
(PLANT INVENTORY / FURNITURE INVENTORY / MATERIAL INVENTORY / OBJECT/COMPONENT INVENTORY)

CONTINUITY RULES:
- Position/orientation LOCK: every zone at EXACT position from LAYOUT MAP.
- Identity LOCK: every plant/component/material matches INVENTORY — only completion/maturity/finish changes.
- Camera LOCK: never move.
DO NOT introduce components/plants/materials not listed in INVENTORY.
STRICTLY NO TEXT, NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS.
Photorealistic, ultra-detailed.
```

Save each prompt to `prompts/stage_<NN>_image_prompt.txt`.

### Resume support

`--resume`: skip any stage where `stages/stage_<NN>.jpg` already exists + size > 30KB. Reuse `stages/flow_imggen.json` (IMG_PID + IMG_VID + IMG_SID_*) if present.

---

## Phase C — Veo Transition Videos

### C1 — Create ephemeral Flow project

```bash
# Create project (internal render workspace)
curl -X POST http://127.0.0.1:8100/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fk-build-<slug>",
    "description": "Internal render workspace for fk-build",
    "story": "<subject> build timelapse — <N> stages",
    "material": "realistic",
    "characters": []
  }'
# Save: project_id → PID

curl -X POST http://127.0.0.1:8100/api/videos \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<PID>",
    "title": "<slug>",
    "video_story": "Timelapse build",
    "display_order": 0,
    "orientation": "VERTICAL"
  }'
# Save: video_id → VID
```

Save PID + VID to `clips/flow_project.json`.

### C2 — Upload stage images

For each `stages/stage_<NN>.jpg` (k = 0..N):
```bash
curl -X POST http://127.0.0.1:8100/api/upload-image \
  -F "file=@stages/stage_NN.jpg"
# → {"media_id": "<uuid>", ...}
```
Cache `stage_NN → media_id` in `clips/.upload_cache.json`.

### C3 — Create N scenes + wire chain

For k = 0..N-1 (N scenes, one per transition k → k+1):
```bash
curl -X POST http://127.0.0.1:8100/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "<VID>",
    "display_order": <k>,
    "prompt": "Transition stage <k> to stage <k+1> of <subject> build.",
    "video_prompt": "<VEO_TRANSITION_PROMPT>",
    "transition_prompt": "<VEO_TRANSITION_PROMPT>",
    "character_names": [],
    "chain_type": "ROOT",
    "parent_scene_id": null
  }'
# Save: scene_id → SID_k
```

Then PATCH each scene to wire start + end frame images:
```bash
curl -X PATCH http://127.0.0.1:8100/api/scenes/<SID_k> \
  -H "Content-Type: application/json" \
  -d '{
    "vertical_image_media_id": "<media_id_of_stage_k>",
    "vertical_end_scene_media_id": "<media_id_of_stage_k+1>",
    "vertical_image_status": "COMPLETED"
  }'
```
`vertical_image_status: COMPLETED` short-circuits image gen — we supply the image directly.

Save all scene IDs to `clips/flow_project.json`.

### C4 — Probe first, then batch

```bash
# Probe clip_00 alone
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{"requests":[{
    "type":"GENERATE_VIDEO","scene_id":"<SID_0>",
    "project_id":"<PID>","video_id":"<VID>","orientation":"VERTICAL"
  }]}'

# Poll until done:
curl -s "http://127.0.0.1:8100/api/requests/batch-status?video_id=<VID>&type=GENERATE_VIDEO"
# Wait for "done": true
# On QUOTA error → HALT + emit: "Run the doctor command (/fk-doctor on Claude Code, /fk:doctor on Gemini CLI); resume with --resume after quota reset."

# If probe OK → submit remaining N-1 in one batch
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{"requests":[<SID_1..SID_N-1 batch>]}'
# Poll every 30s until "done": true
```

### C5 — Download clips

For each scene k: download `vertical_video_url` → `clips/clip_<NN>.mp4`.

### Veo transition video prompt template (per k → k+1)

```
8-second hyper-fast timelapse of {{subject_display}} build, phase {{k+1}} of {{N}} —
progressing from {{milestone_from}} ({{pct_from}}%) to {{milestone_to}} ({{pct_to}}%).
Camera locked-off, IDENTICAL framing throughout.

{{LAYOUT_MAP}}
{{INVENTORY}}

CRITICAL during this 8s timelapse:
- Camera does NOT move (locked tripod, identical to first-frame & last-frame images).
- All zones stay at EXACT positions from LAYOUT MAP.
- All components/plants/materials stay SAME identity per INVENTORY — only build-progress changes.
- Final frame matches the provided end-frame image EXACTLY.

Action progression ({{milestone_name}} phase):
{{PHASE_SPECIFIC_ACTIONS}}
  house/building → workers hauling materials, scaffolding rising, walls forming, windows snapping in
  garden         → clearing → soil → hardscape → planting → blooming (per phase)
  room           → stripping → painting → flooring → furniture → decor (per phase)
  object/food    → mixing, pouring, baking flash, layering, frosting sweeps, piping in fast strokes
  object/furniture → cutting flash, dry-fit, glue + clamp, sanding, staining
  object/electronics → components snapping together, screen lighting up
  object/sculpture → chisel chips flying, form emerging, polishing pass
  object/painting → brush strokes appearing, layers building, details added
  object/model   → pieces clicking together, walls rising, minifigs placed
  object/instrument → glue + clamp, strings winding on, polish

Time-passing cue: subtle sun-arc / shadow shift (outdoor) OR window light shift (interior)
OR slight ambient shift (object close-up).

Style: realistic high-end timelapse, fast-motion stable LOCKED camera, cinematic color grade,
sharp focus, saturation increasing toward final phase.
Vertical 9:16 portrait. STRICTLY NO TEXT, NO TYPOGRAPHY, NO LOGOS.

Negative: subtitles, watermark, text overlay, camera movement, multiple shots, dialogue.
```

Save each Veo prompt to `prompts/transition_<NN>_video_prompt.txt`.

After all clips downloaded: print PID + VID so user can run `/fk-status` if needed. Do NOT delete the ephemeral project (keep for resume).

---

## Phase D — Music + Concat + Brand

### D1 — Concat clips with tail trim + slow-down

Veo clips are fast-forward by nature. Default `--speed 0.8` slows the final concat by 25% (calmer pacing, video lasts ~25% longer — better fits 30-60s Short range). Pass `--speed 1.0` to keep raw Veo speed.

```bash
SRC=output/fk_build/<slug>
N=<num_clips>
SPEED=<--speed value, default 0.8>

# 1) Tail-trim 0.5s on all-but-last to mitigate chain-boundary static
> $SRC/clips/concat.txt
for k in $(seq 0 $((N-1))); do
  CLIP=$SRC/clips/clip_$(printf "%02d" $k).mp4
  if [ $k -lt $((N-1)) ]; then
    DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$CLIP")
    TRIM=$(python3 -c "print(round(float('$DUR') - 0.5, 2))")
    ffmpeg -y -i "$CLIP" -t $TRIM -c copy "$SRC/clips/clip_${k}_trim.mp4"
    echo "file 'clip_${k}_trim.mp4'" >> $SRC/clips/concat.txt
  else
    echo "file 'clip_$(printf "%02d" $k).mp4'" >> $SRC/clips/concat.txt
  fi
done

# 2) Fast concat (stream copy) → concat_raw.mp4
cd $SRC/clips
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy -movflags +faststart ../concat_raw.mp4

# 3) Slow-down with setpts (skip if SPEED=1.0)
cd $SRC
if [ "$SPEED" != "1.0" ]; then
  ffmpeg -y -i concat_raw.mp4 -vf "setpts=PTS/${SPEED}" -an \
    -c:v libx264 -crf 18 -r 24 -pix_fmt yuv420p -movflags +faststart final.mp4
  rm concat_raw.mp4
else
  mv concat_raw.mp4 final.mp4
fi
```

**Duration math** (default N=3, raw clip 8s, trim 0.5s, speed 0.8):  
post-trim concat ≈ 2×7.5 + 1×8.0 = 23s → after 0.8× slowdown ≈ **29s**. With raw 1.0× = 23s.  
Tăng N=4 → 38s @ 0.8×; N=5 → 47s @ 0.8×.

### D2 — Music generation (skip if `--no-music`)

Music prompt (per subject):
```
Slow cinematic instrumental, gentle warm strings + soft piano, building swell over 30 seconds,
satisfying transformation mood, organic and uplifting. NO drums, NO vocals, NO lyrics.
{{SUBJECT_COLOR}}:
  house/building → industrious + hopeful + accomplished
  garden         → organic + earthy + peaceful → blooming joyful
  room           → cozy + warm + cinematic reveal
  object/food    → playful + appetizing + warm
  object/furniture → artisanal + woody + warm craft
  object/electronics → clean + modern + minimal (no drums)
  object/sculpture → contemplative + classical
  object/painting → dreamy + romantic + impressionistic
  object/model   → nostalgic + playful
  object/instrument → warm + craft + melodic
```

```bash
# Gemini Lyria (Path A — default)
curl -X POST http://127.0.0.1:8100/api/gemini/browser/generate-music \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"<MUSIC_PROMPT>","model":"Nhanh","timeout":120,"headless":true}'
# → {"ok":true,"path":"output/_shared/gemini_music/<file>.mp4"}

# Transcode MP4 → MP3 (per feedback-music-as-mp3 — smaller, audio-only)
LYRIA_MP4=<path from response>
ffmpeg -y -i "$LYRIA_MP4" -vn -c:a libmp3lame -q:a 4 \
  output/fk_build/<slug>/music/track.mp3
```

On Lyria failure (LOGIN_EXPIRED, QUOTA_REACHED, timeout): **skip music** — final video is silent. No Suno fallback (per project decision: `/fk-gen-music` Path A is the only sanctioned music source for this skill). User can later run `/fk-gen-music` manually and re-mux, or invoke `--resume` after Lyria recovers.

### D3 — Mix BGM into final

```bash
SRC=output/fk_build/<slug>
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 $SRC/final.mp4)
ffmpeg -y -i $SRC/final.mp4 -i $SRC/music/track.mp3 \
  -filter_complex "[1:a]aloop=loop=-1:size=2e9,atrim=0:$DUR,volume=0.18[bg]; \
                   [0:a]volume=1.0[sfx]; \
                   [sfx][bg]amix=inputs=2:duration=first:dropout_transition=0[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -movflags +faststart \
  $SRC/final_with_music.mp4
```

If `--no-music`: `cp $SRC/final.mp4 $SRC/final_with_music.mp4`.

### D4 — Brand logo (skip if no `--channel` given, or `--no-brand`)

```bash
CHANNEL=<channel_slug>
ICON=youtube/channels/${CHANNEL}/${CHANNEL}_icon.png
[ ! -f "$ICON" ] && echo "ERROR: icon missing at $ICON — skipping brand" && exit 0

SIZE=140; PAD=28   # for 1080×1920 vertical
ffmpeg -y -i $SRC/final_with_music.mp4 -i $ICON \
  -filter_complex "[1:v]scale=${SIZE}:${SIZE},format=rgba[icon]; \
                   [0:v][icon]overlay=W-w-${PAD}:H-h-${PAD}" \
  -c:v libx264 -preset fast -crf 18 -r 24 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart \
  $SRC/final_branded.mp4
echo "Branded output: $SRC/final_branded.mp4"
```

If `--no-brand` or no `--channel`: `cp $SRC/final_with_music.mp4 $SRC/final_branded.mp4`. Print "Brand skipped — final output: final_with_music.mp4".

### D5 — Write README.md recap

Write `output/fk_build/<slug>/README.md`:
```
# fk-build · <slug>

- Subject: <subject> / <subtype>
- Stages: <N>
- Source image: source.jpg
- Final: final_branded.mp4 (<DUR>s, 1080×1920, vertical)
- Music: <track.mp3 | none>
- Brand: <channel | none>
- Flow project: <PID> / video <VID>
- Created: <iso8601>
- Args used: <full CLI flags>

## How to re-render
/fk-build source.jpg --slug <slug> --stages <N> [--resume]
```

### D6 — Final verification

```bash
ffprobe -v quiet -show_entries format=duration,stream=width,height $SRC/final_branded.mp4
# Expect: duration ≈ N×8 − (N−1)×0.5, width=1080, height=1920
ffmpeg -y -i $SRC/final_branded.mp4 -af "volumedetect" -f null /dev/null 2>&1 | grep mean_volume
# Expect: mean_volume ~ −22 to −16 dB
```

---

## Phase E — Caption (optional, default: enabled)

Run `/fk-gen-caption` against the final branded video after Phase D completes. Since fk-build has no TTS/narrator text, caption is derived from `analysis.json` subject description (subject, style_descriptor, stage_0_archetype).

```bash
/fk-gen-caption <final_branded_mp4_video_id>
# OR skip with --no-caption flag
```

On `--no-caption`: skip silently. No caption file written.

Caption content source: use the `style_descriptor` + `scene_context.era` + `scene_context.lighting` fields from `analysis.json` as the subject description passed to `/fk-gen-caption`.

---

## Output Folder Structure

```
output/fk_build/<slug>/
  meta.json                  subject, subtype, N, source_image_hash, args used
  analysis.json              LAYOUT MAP + INVENTORY + scene_context (LOCK BLOCKS source-of-truth)
  analysis.md                human-readable mirror for debugging
  source.jpg                 copy of input image (= Stage N)
  README.md                  auto-written recap at end
  prompts/
    stage_00_image_prompt.txt
    stage_01_image_prompt.txt
    ...
    transition_00_video_prompt.txt
    ...
  stages/
    stage_00.jpg             Stage 0 — wasteland / raw materials
    stage_01.jpg
    ...
    stage_<N-1>.jpg
    stage_<N>.jpg            = source.jpg (final)
    flow_imggen.json         IMG_PID, IMG_VID, ENTITY_ID, IMG_SID_* (for resume)
  clips/
    clip_00.mp4              8s: stage_00 → stage_01
    clip_01.mp4
    ...
    clip_<N-1>.mp4           8s: stage_<N-1> → stage_<N>
    clip_<k>_trim.mp4        trimmed (0.5s tail removed) for concat
    concat.txt               ffmpeg concat list
    .upload_cache.json       stage_NN → media_id mapping
    flow_project.json        PID, VID, scene IDs (for resume)
  music/
    track.mp3                30s instrumental
  final.mp4                  concat of N trimmed clips
  final_with_music.mp4       final.mp4 + BGM at 0.18× volume
  final_branded.mp4          + brand logo overlay (primary deliverable)
```

---

## Quick Reference

| Param | Value |
|-------|-------|
| Resolution | 1080×1920 (9:16 vertical) |
| Video codec | h264, yuv420p, crf 18 |
| Audio codec | aac, 192k |
| Stage image model | Flow GENERATE_IMAGE + EDIT_IMAGE (chained waves, per `/fk-gen-images`) |
| Clip duration | ~8s per Veo clip |
| Total duration | `(N×8 − (N−1)×0.5) / speed` — default N=3 + speed 0.8 ≈ **29s**; N=4 ≈ 38s; N=5 ≈ 47s |
| BGM volume | 0.18× |
| Clip SFX volume | 1.0× |
| Brand logo size | 140px, PAD 28px, bottom-right |
| Image gen | Sequential wave-by-wave (Wave 1 then Wave 2..N) — poll between waves |
| Probe-first | Clip 00 probed alone before submitting N-1 batch |

---

## Per-Video Checklist

```
[ ] Pre-flight: /health ok + Flow credits ok
[ ] Phase A: analysis.json written, LOCK BLOCKS non-empty
[ ] Phase B0: source.jpg uploaded → SOURCE_MEDIA_ID; Flow imggen project created; visual_asset entity patched with media_id
[ ] Phase B1: N scenes created (ROOT + CONTINUATION chain); flow_imggen.json saved
[ ] Phase B Wave 1: stage_00.jpg — GENERATE_IMAGE done, >30KB, 9:16 ratio
[ ] Phase B Waves 2..N: stages 01..N-1 — EDIT_IMAGE chained, each >30KB
[ ] Phase B Stage N: source.jpg copied → stage_<N>.jpg
[ ] Phase C: all N clips downloaded to clips/clip_NN.mp4
[ ] Phase D concat: final.mp4 exists, duration ≈ N×8−(N-1)×0.5
[ ] Phase D music: music/track.mp3 exists (or --no-music confirmed)
[ ] Phase D mix: final_with_music.mp4 has audio, mean_volume −22…−16 dB
[ ] Phase D brand: final_branded.mp4 exists (or no-brand confirmed)
[ ] Phase E: caption generated (or --no-caption confirmed)
[ ] README.md written
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| GENERATE_IMAGE / EDIT_IMAGE `FAILED` | Flow quota or prompt issue | Check batch-status `failed` count → `/fk-doctor`; resume with `--resume` after quota reset |
| Ghost scene duplicate `display_order` | Flow API created duplicate on retry | DELETE duplicate scene before resubmitting wave |
| Entity `media_id=none` after create | API did not auto-link | PATCH `/api/characters/<ENTITY_ID>` with `media_id` |
| Stage image < 30KB / blank | Flow image gen failed silently | Check scene `vertical_image_url`; resubmit with `REGENERATE_IMAGE` |
| Camera drifts between stages | LAYOUT MAP not pasted verbatim | Confirm LAYOUT MAP block in every stage prompt |
| Species / component drifts | INVENTORY not pasted verbatim | Confirm INVENTORY block in every stage + video prompt |
| Veo QUOTA / NO_FLOW_KEY | Flow credits exhausted | HALT → `/fk-doctor` → resume after reset |
| Concat gap > 0.5s at cut | Static end-frames from chaining | Phase D tail-trim 0.5s from clip ends (already in D1) |
| Brand icon missing | `--channel` slug has no icon file | Check `youtube/channels/<channel>/<channel>_icon.png`; run without `--channel` if absent |
| Text in stage image | Gemini ignored NO TEXT guard | Add stronger "ABSOLUTELY NO text, numbers, labels, watermarks" line; regen |
| Image is horizontal | Gemini ignored 9:16 instruction | Check prompt preamble `[VERTICAL PORTRAIT 9:16, 1080×1920]`; re-run |
| Lyria music failure | LOGIN_EXPIRED or quota | Skip music (silent final), or use `--no-music` from the start; manual re-mux after Lyria recovers |

---

## When to Call the Doctor (`/fk-doctor` on Claude / `/fk:doctor` on Gemini)

```
[ ] /health → extension_connected: false
[ ] Flow project/video/scene API returns 4xx/5xx
[ ] Veo batch returns FAILED with QUOTA / NO_FLOW_KEY / UNSAFE_GENERATION
[ ] Lyria persistent failure (LOGIN_EXPIRED, repeated QUOTA_REACHED)
[ ] Any stuck PROCESSING request > 20 min
```

---

## How to Resume

Re-run with same slug + `--resume`:
```
/fk-build source.jpg --slug house_modern_villa_001 --resume
```
- Phase B: skips stage_NN.jpg files that already exist + size > 30KB. Reuses `stages/flow_imggen.json` for IMG_PID/VID/SID if present — skips project/scene creation.
- Phase C: reads `clips/flow_project.json` to reuse existing PID/VID/scene IDs; downloads any still-missing clips.
- Phase D: skips final.mp4, final_with_music.mp4, final_branded.mp4 if they already exist.

---

## Examples

```bash
# House (defaults: N=3, no brand, with music, slow 0.8×)
/fk-build photos/villa.jpg

# Garden, 5 stages
/fk-build photos/zen_garden.jpg --stages 5

# Object (cake), force subtype
/fk-build photos/cake.jpg --subject object --object-subtype food

# Room, with brand logo for lamplit-library channel
/fk-build photos/living_room.jpg --channel lamplit-library

# Dry run: see prompts without generating anything
/fk-build photos/lego_castle.jpg --subject object --object-subtype model --dry-run

# Resume interrupted run
/fk-build photos/villa.jpg --slug house_modern_villa_001 --resume

# No music, URL input
/fk-build https://example.com/guitar.jpg --no-music
```

---

## Helper Script

For automated / batch runs, use the Python helper:
```bash
python3 scripts/fk-build-render-stages.py \
  --image output/fk_build/<slug>/source.jpg \
  --slug <slug> --stages 4 [--resume] [--dry-run]
```
The script handles Phase B (Flow image gen — GENERATE_IMAGE + EDIT_IMAGE waves) + Phase C (Veo uploads + batch) + Phase D (concat + music + brand) with full resume support and quota-halt logic. See `scripts/fk-build-render-stages.py` for full argparse documentation.

---

## Files Created / Edited

- WRITE: `output/fk_build/<slug>/` — all artifacts per output structure above
- INVOKES: FlowKit `:8100` API (image gen + Veo videos + music), `ffmpeg` (concat + mix + brand)
- REFERENCES: `/fk-gen-images` pattern (GENERATE_IMAGE + EDIT_IMAGE waves), `/fk-gen-chain-videos` pattern (Veo first+last-frame), `/fk-upload-image` (source image upload), `/fk-brand-logo` (logo overlay), `/fk-gen-music` Path A only (Lyria — no Suno), `/fk-gen-caption` (Phase E), `/fk-doctor` (error escalation)
