# Phase 2 — Vision Analysis, Subject Classification, LOCK BLOCK Builder

## Context Links
- Parent: `plan.md`
- Direct pattern source: `/Users/vieterp/code/Research/.claude/skills/build-garden/SKILL.md` (step 3, LAYOUT MAP + PLANT INVENTORY)
- Memory: `feedback-flow-image-orientation-text` (defensive vertical + no-text prompting)
- Sibling: `skills/fk-create-project.md` ("Real-People Characters" section's safe prompt language)

## Overview
The brain of `fk-build`. Reads input image with Claude's built-in vision, decides which of the 5 subject buckets it belongs to (with object sub-typing), then builds the canonical **LOCK BLOCKS** that will be pasted verbatim into every downstream Gemini stage prompt + every Veo transition prompt.

## Key Insights
- LOCK BLOCKS are the ONLY thing that prevents Gemini from mutating layout / species / materials between stages. They are 80% of the quality difference between this skill and a naive prompt-the-image loop.
- LOCK BLOCKS must be SUBJECT-AWARE — a garden's inventory is plant species, an object's inventory is component parts. Generic schema won't work.
- Classification + analysis happen in a SINGLE vision pass to save context tokens — emit one structured JSON.

## Requirements

### Functional
- Single Claude vision call against the input image producing structured `analysis.json` with:
  - `subject`: one of `{house, garden, room, building, object}` (auto unless `--subject` override)
  - `subtype` (object only): one of `{food, furniture, electronics, sculpture, model, instrument, painting, other}`
  - `style_descriptor`: short kebab-case for slug (e.g. `modern_villa`, `scandi_living`, `lego_castle`, `decorated_cake`)
  - `scene_context`: dict with subject-specific fields (era, palette, materials, lighting, camera-angle, mood, surroundings-locked)
  - `layout_map`: free-form prose block (used verbatim as `{{LAYOUT_MAP}}`)
  - `inventory_lock`: free-form prose block (used verbatim as `{{INVENTORY_LOCK}}` — name varies by subject)
  - `stage_0_archetype`: chosen wasteland / raw-materials archetype + 2-3 line description
- Output language: prompts in English; analysis prose may be bilingual if helpful but LOCK BLOCKS stay English (Gemini/Veo perform best with English).
- Subject overrides via `--subject` and `--object-subtype` skip the classifier (use user choice but still run the analysis pass).

### Non-functional
- Single vision call (≤ 1 image attached, ≤ 3000 output tokens).
- Deterministic outputs across runs (within Claude's normal variance) — re-running same image gives the same subject classification.

## Architecture

### Step 2.1 — Classify (only if `--subject auto`)
Use Claude built-in vision. Decision tree (encoded in skill prose):

```
Q1: Is the image dominated by a single building structure occupying most of the frame?
  → if photographed from outside, ground-level/elevated, showing facade & roofline:
      - if it's a single residence (1-4 floors, lawn/yard around it) → house
      - if it's a multi-story commercial/residential tower or large institutional structure → building
Q2: Is the image an interior space (floor + walls + ceiling visible)?
  → room
Q3: Is the image an outdoor landscaped area (plants, hardscape, sky, no dominant single building)?
  → garden
Q4: Otherwise — single discrete crafted thing dominating frame (food, furniture piece,
    gadget, statue, painting, model/toy build, instrument):
  → object → run sub-type classifier (Q5)
Q5 (object sub-type): match dominant material/category
  - edible / on plate / in bowl → food
  - chair/table/cabinet/sofa shape → furniture
  - device with screen/buttons/ports → electronics
  - statue/bust/abstract carved form → sculpture
  - canvas/framed flat 2D art → painting
  - lego/gunpla/wooden-model/figurine → model
  - guitar/violin/drum/synth → instrument
  - none of above → other
```

Print the reasoning + classification to user, then proceed (no confirmation prompt per `feedback-no-confirmation-prompts`).

### Step 2.2 — Analyze (always run)
Run a subject-specific vision pass. Each subject has its own analysis schema:

#### HOUSE / BUILDING (outdoor structure)
- Architectural style, scale (floors/meters), primary materials, facade color palette (3-5), distinctive features (balcony, columns, signage, podium), surroundings (street/lawn/skyline), lighting & camera angle, era/mood
- LAYOUT MAP zones: roof, facade, entrance, surrounding ground (yard/plaza), neighboring buildings/trees, sky
- INVENTORY name: **MATERIAL INVENTORY** — every visible material with location + finish (e.g. "white stucco walls on body, dark grey slate gable roof, oak front door center, large fixed-pane windows in 2 horizontal rows")

#### ROOM
- Room type (living/kitchen/bedroom/office/bathroom), design style, color palette, materials & textures, key furniture pieces, decor & lighting, architectural features (window/door/ceiling), camera angle
- LAYOUT MAP zones: floor, walls (each visible wall), ceiling, window, door, each furniture piece's footprint
- INVENTORY name: **FURNITURE INVENTORY** — every furniture piece + decor object with position, material, color (e.g. "Sofa: rear wall center, 3-seat linen sectional, oatmeal beige; Coffee table: center floor, round walnut 80cm; Pendant lamp: ceiling above table, brass bowl shade")

#### GARDEN
- Garden type, plant species, hardscape elements, water features, lighting fixtures, furniture & decor, surroundings, sky, camera angle, mood
- LAYOUT MAP zones: ground areas (lawn/path/pond/beds), perimeter (fence/wall), overhead (trees/sky), each decor cluster
- INVENTORY name: **PLANT INVENTORY** (verbatim from build-garden — plant species + position + mature size + container)

#### OBJECT (NEW)
- Object subtype (food/furniture/electronics/sculpture/model/instrument/painting/other)
- Material composition, dominant color palette (2-4), surface finish (matte/glossy/textured), distinctive features (carvings/screens/strings/icing pattern), scale (real-world cm), camera framing (top-down/3⁄4/eye-level macro), surface it sits on, background, lighting
- LAYOUT MAP zones: the object's principal sub-regions in the frame (e.g. cake: tiers; chair: seat/legs/back; phone: screen/body/buttons/ports; lego castle: keep/walls/towers/gates; guitar: body/neck/headstock/strings; painting: foreground/midground/background regions inside the canvas)
- INVENTORY name: **OBJECT/COMPONENT INVENTORY** (NEW SCHEMA, see below)

#### OBJECT/COMPONENT INVENTORY schema
Each entry:
```
- Component <X>: <name> — <position in frame %>, <approx size %frame>,
  <material>, <color/finish>, <surface treatment>.
  At Stage 0 = <raw-material form>. At intermediate = <half-formed form>.
  At Stage N = <final form as visible in input>.
```
Examples per subtype:

```
[food: 3-tier chocolate cake]
- Component A: bottom tier — center-bottom, 60% frame width, sponge cake covered
  in dark chocolate ganache, glossy finish, piped white-cream rosettes along base.
  At Stage 0 = bowl of cake batter + bowl of melted chocolate on counter.
  At intermediate = baked unfrosted bottom round on cake board.
  At Stage N = fully frosted with rosettes.
- Component B: middle tier — ...
- Component C: top tier — ...
- Component D: piping decorations — ...
- Component E: cherry garnishes — ...

[furniture: oak Windsor chair]
- Component A: seat plank — center, 35% frame area, solid oak, golden honey stain, satin finish.
- Component B: 4 turned legs — bottom 30% frame, oak, golden honey stain.
- Component C: backrest spindles — ...
- Component D: top crest rail — ...

[electronics: smartphone — black slab]
- Component A: aluminum frame — perimeter, anodized matte black.
- Component B: front glass + OLED screen — center, 90% front face.
- Component C: rear glass — ...
- Component D: camera lens cluster + sensors — top-left rear.
- Component E: side buttons — ...

[model: lego castle]
- Component A: keep — center, 50% frame height, grey 2×4 bricks stacked, crenellated top.
- Component B: 2 corner towers — left/right back, cylindrical, grey + tan windows.
- Component C: gatehouse — front-center, brown drawbridge piece, portcullis.
- Component D: green base plate — bottom 100%, 32×32 stud green.
- Component E: minifigure knights — 2 figures on battlements.
```

### Step 2.3 — Pick Stage 0 archetype
Map subject + subtype → raw-state archetype (default; overridable via `--start-state`):

| Subject | Default Stage 0 | Notes |
|---------|----------------|-------|
| house | Decayed/dilapidated shell (peeling paint, broken windows, overgrown lawn) | Mirrors build-house |
| garden | Auto from build-garden start-states.md (load that file's library by reference) | Honor build-garden rule "Stage 0 must be DRAMATIC" |
| room | Bare empty shell (stripped to plaster walls + bare subfloor, no furniture, single bulb) | Mirrors build-room |
| building | Empty plot of bare graded earth + temp fencing + materials staged | Mirrors build-building |
| object → food | Raw ingredients in bowls / cutting board / mise-en-place on counter | NEW |
| object → furniture | Pile of raw lumber + tools (saw, clamps, sandpaper, screws) on workshop floor | NEW |
| object → electronics | Scattered components (PCB, chips, battery, frame, screen) on antistatic mat | NEW |
| object → sculpture | Raw uncarved stone block / clay lump on pedestal with chisels nearby | NEW |
| object → painting | Blank stretched canvas on easel + paint tubes + brushes + palette | NEW |
| object → model | Sealed box / sprues + manual / loose pieces scattered on building mat | NEW (lego/gunpla) |
| object → instrument | Raw wood blanks + strings + tuning pegs + luthier tools | NEW |
| object → other | Generic "raw materials and tools laid out on neutral surface" | NEW |

### Step 2.4 — Persist
Write `analysis.json` with all fields above + `lock_blocks.layout_map` and `lock_blocks.inventory` (full prose blocks, ready to interpolate).

### Step 2.5 — Defensive vertical + no-text guardrails (per memory)
Append the following invariant to every LOCK BLOCK preamble:
```
VERTICAL PORTRAIT 9:16 (1080×1920) framing. STRICTLY NO TEXT,
NO TYPOGRAPHY, NO WATERMARKS, NO LOGOS in the image.
```

## Related Code Files
- **Inside skill:** vision prompts written as templated prose in `skills/fk-build.md`
- **Output:** `output/fk_build/<slug>/analysis.json` + `analysis.md` (human-readable mirror for debugging)

## Implementation Steps
1. Write classifier prose Q1-Q5 inside SKILL.md (5-bucket + sub-type tree above).
2. Write 5 analysis schemas (one per subject) as templated prompt sections.
3. Write OBJECT/COMPONENT INVENTORY schema + 7 sub-type examples (food / furniture / electronics / sculpture / painting / model / instrument) in SKILL.md.
4. Write Stage 0 archetype mapping table.
5. Write `analysis.json` JSON-schema + minimal example for one subject per bucket.
6. Add defensive vertical + no-text invariant block.

## Todo List
- [ ] Vision classifier Q1-Q5 tree
- [ ] 5 subject-specific analysis schemas
- [ ] OBJECT/COMPONENT INVENTORY schema (NEW)
- [ ] Stage 0 archetype mapping
- [ ] analysis.json shape + sample
- [ ] Defensive prompting boilerplate

## Success Criteria
- 5 sample images (one per subject; for object run all 7 subtypes) classified correctly ≥ 4/5.
- For each, the produced LAYOUT MAP + INVENTORY block is concrete enough that a fresh agent reading only the JSON could re-imagine the original image's layout without seeing it.
- Stage 0 archetype feels DRAMATICALLY different from input (the "this is the same property?" rule).

## Risk Assessment
- Classifier miss on edge cases (e.g. a model building of a real building → likely object/model, not building). Mitigation: `--subject` override is loud + documented.
- Object subtype "other" risks weak LOCK BLOCK. Mitigation: fall back to generic "primary components + surface + lighting" template + warn.
- Vision call might produce non-strict JSON. Mitigation: prompt the model with "respond with JSON only, no prose, no fences"; on parse failure, retry once.

## Security Considerations
- Don't include PII visible in the image in analysis.json (e.g. address numbers, faces). Strip faces from LAYOUT MAP wording (use "person silhouette" rather than describing face).

## Next Steps
- Phase 3 consumes `analysis.json` and the LOCK BLOCKS to generate Stage 0 + chained Stage 1..N-1.
