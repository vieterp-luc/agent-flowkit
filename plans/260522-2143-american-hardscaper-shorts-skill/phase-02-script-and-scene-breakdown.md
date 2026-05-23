# Phase 02 — Script & Scene-Breakdown Logic

## Context Links

- Overview: [plan.md](plan.md)
- Depends on: [phase-01](phase-01-skill-spec-and-identity.md) (scene count, duration)
- Pattern reference: `fk-video-khkd` Bước 0-1 (research + scene arc design)

## Overview

- **Priority:** P1
- **Status:** pending
- **Description:** Define how the skill turns a topic into a `scene_breakdown.json`
  — the Hook/Body/CTA framework, per-scene roles, durations, KB-grounded content,
  and which scenes get text overlays. There is NO narrator script; the "script"
  here is the visual + SFX + overlay plan.

## Key Insights

- The video has NO voiceover. The "script" is therefore a **shot list**, not prose.
- The Hardscaper framework is fixed: Hook 5s → Body 20-40s → CTA 10s. Map this
  onto 6-9 scenes; each scene is one Veo clip (~5-8s native).
- KB grounding matters for AI realism — technically-correct technique in the
  prompt makes the clip read as "real pro work" not "AI vibes" (see Phase 03).
- Beat-sync (Phase 04) needs scene durations chosen on a BPM grid, so durations
  are decided HERE as multiples of a bar, not arbitrary.

## Requirements

### Functional

- Produce `scene_breakdown.json` with one object per scene:
  `{idx, role, area, duration_s, shot, action, overlay, chain_type}`.
- `role` ∈ `hook | body | cta`. Exactly: 1 hook scene, 4-6 body scenes, 1 cta scene.
- Durations sum to the target length (default ~45s).
- Mark 2-4 scenes (max) with a short overlay string; rest = `overlay: null`.

### Non-functional

- All `action`/`shot` text in English.
- Content must be technically accurate to the 3 KB areas.

## Architecture

### Framework → scene mapping (default 7 scenes, ~45s)

| Scene | Role | Dur | Shot intent | KB anchor |
|-------|------|-----|-------------|-----------|
| 0 | HOOK | 5s | Head-on saw blade / plate compactor in low "dying light", music slams in | any area — most visceral tool |
| 1 | BODY | 6s | Close-up paver scoring + cut, sparks, fast | Paver Cutting — speed = mastery |
| 2 | BODY | 6s | Low-angle stone laid into course, hands seating it | Retaining Wall — foundation/elevation |
| 3 | BODY | 6s | Plate compactor passing over base, dust kicked up | Retaining Wall — base compaction |
| 4 | BODY | 6s | Polymeric sand swept into joints, broom strokes | Polymeric Sand — locking step |
| 5 | BODY | 6s | "Self-reliance" — worker adjusting heavy equipment alone | Hardscaper identity |
| 6 | CTA | 10s | Finished tiered patio glowing in sunlight, slow reveal + logo | "Level Up" payoff |

- `--scenes 9` → split Body into more cuts (faster montage). `--scenes 6` → drop
  scene 5. CTA stays 10s; Hook stays 5s; Body absorbs the change.
- `--area X` → bias Body scenes toward that area's KB technique.

### chain_type policy

- **All scenes ROOT.** The Hardscaper style is fast hard cuts beat-synced — NOT
  smooth morph transitions. Chaining (CONTINUATION/EDIT_IMAGE) would soften the
  cuts and risk visual drift. Hard cuts ARE the aesthetic. (Per `fk-gen-chain-videos`
  guidance: location/action change → ROOT hard cut.)
- This also keeps image gen single-wave (all GENERATE_IMAGE) — simpler, quota-lighter.

### Knowledge base → content rules

The skill embeds a compact KB table so generated `action` text is accurate:

| Area | Correct technique cues to put in prompts | Avoid |
|------|------------------------------------------|-------|
| Paver Cutting | score line then full cut, masonry blade, steady feed, minimal wasted motion, measure-to-cut flow | wobbling blade, cutting toward body |
| Retaining Wall | compacted gravel base, level first course, backfill + drainage, tiered batter/setback | wall on bare soil, no base |
| Polymeric Sand | sweep into joints, dry pavers, fine mist activation, joints fully filled | wet pavers before sweeping, sand on paver faces |

### Overlay plan (2-4 scenes max)

- Punchy, ALL-CAPS, ≤ 22 chars: e.g. `CUT FAST. CUT CLEAN.`, `BASE IS EVERYTHING`,
  `LOCK IT FOREVER`, `LEVEL UP YOUR YARD`.
- Hook scene + CTA scene almost always get one; 0-2 body scenes optional.
- Stored into `text_overlays.json` via `/fk-gen-text-overlays` consumption format
  in Phase 04 (keyed by display_order).

## Related Code Files

- CREATE (at runtime, per video): `output/hardscaper/<slug>/scene_breakdown.json`
- The breakdown LOGIC is documented in `skills/fk-video-hardscaper.md` (Phase 05).
- No standalone code module — the skill instructs the agent to build the JSON.

## Implementation Steps

1. Write the framework→scene mapping table into the skill.
2. Write the KB technique table into the skill.
3. Define the `scene_breakdown.json` schema.
4. Define duration math: durations are bar-multiples (see Phase 04) summing to
   target length; document the default 5/6×5/10 layout.
5. Define overlay-selection rule (Hook + CTA always; ≤2 body optional).
6. Define `--scenes` / `--area` adjustment rules.

## Todo List

- [ ] Framework→scene table written
- [ ] KB technique table written
- [ ] `scene_breakdown.json` schema defined
- [ ] Duration/bar math documented
- [ ] Overlay-selection rule documented
- [ ] `--scenes` / `--area` adjustment rules documented

## Success Criteria

- Given any topic, the rules deterministically yield a valid breakdown:
  1 hook + 4-6 body + 1 cta, durations summing to target ±1s.
- Every Body scene cites a KB-correct technique.

## Risk Assessment

- **Risk:** generic/inaccurate hardscaping content → looks fake.
  **Mitigation:** mandatory KB table; every scene `action` must map to a KB cue.
- **Risk:** durations don't fit the music grid. **Mitigation:** durations chosen
  as bar-multiples in coordination with Phase 04.

## Security Considerations

- None.

## Next Steps

- Phase 03 turns each scene's `shot`/`action` into a defensive Veo prompt.
- Phase 04 consumes durations for beat-sync.
