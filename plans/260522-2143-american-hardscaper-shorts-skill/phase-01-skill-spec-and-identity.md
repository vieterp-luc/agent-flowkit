# Phase 01 — Skill Spec, Command & Identity

## Context Links

- Overview: [plan.md](plan.md)
- Structural template: `skills/fk-video-khkd.md` (niche vertical-Short skill)
- Pipeline reference: `skills/fk-video-bible-explainer.md` (MODE B producer)

## Overview

- **Priority:** P1 (blocks all later phases — defines the contract)
- **Status:** pending
- **Description:** Define the public surface of `fk-video-hardscaper` — command
  signature, arguments, the "American Hardscaper" identity table, defaults, and
  the output folder structure. No production logic here; this is the spec other
  phases fill in.

## Key Insights

- `fk-video-khkd` is a pure producer (one command → one video, no dashboard) —
  exactly the KISS shape wanted. Copy that structure, NOT bible-explainer's
  MODE A/B/C/D channel-operator complexity.
- Skill must be self-contained: setup.py auto-generates the `.claude/commands/`
  stub from the file's first line, so line 1 = the one-line description.
- VERTICAL orientation must never be hardcoded downstream — but for THIS skill
  it is always VERTICAL, so the project is created VERTICAL once and reused.

## Requirements

### Functional

- One positional arg = the hardscape topic/angle.
- One command runs end-to-end autonomously (per memory
  `feedback-no-confirmation-prompts` — no yes/no prompts mid-run).
- Optional flags: `--no-music`, `--no-brand`, `--length <sec>`, `--scenes <n>`,
  `--area <paver-cutting|retaining-wall|polymeric-sand>`.
- If no topic given → pick a default angle from the 3 KB areas in rotation.

### Non-functional

- Skill file < ~330 lines (matches khkd/bible-explainer size band).
- All prompts in English; output language n/a (no narration).
- Reuse existing skills — zero new API endpoints.

## Architecture

### Command signature

```
/fk-video-hardscaper "<topic>"                       # produce one Short
/fk-video-hardscaper --area paver-cutting            # pick area, auto-topic
/fk-video-hardscaper "<topic>" --length 60           # pin duration
/fk-video-hardscaper "<topic>" --scenes 8            # override scene count
/fk-video-hardscaper "<topic>" --no-music            # skip instrumental bed
/fk-video-hardscaper "<topic>" --no-brand            # skip /fk-brand-logo
```

### Identity table (goes in the skill file)

| Item | Value |
|------|-------|
| Skill name | `fk-video-hardscaper` |
| Style | American Hardscaper — Strong / Real / Brutal-Intense, action over explanation |
| Output | Vertical 9:16 Short, 720×1280, 24fps |
| Duration | 30-60s (default ~45s) |
| Scenes | 6-9 (default 7) |
| Material | `realistic` |
| Narration | NONE — music + SFX driven; 2-4 short bold text overlays only |
| Music | instrumental ONLY (Gemini Lyria), aggressive/driving/bass-heavy, no vocals |
| SFX | jobsite layer — saw, hammer, plate compactor, ambient |
| Local output | `output/hardscaper/<slug>/` |
| KB areas | Paver Cutting · Retaining Wall · Polymeric Sand |

### Output folder structure

```
output/hardscaper/<slug>/
├── scene_breakdown.json      Hook/Body/CTA scene plan + durations + overlays
├── images/                   scene_000.png … scene_00N.png
├── 4k/ , norm/               downloaded + normalized clips (from /fk-concat)
├── music/                    driving_bed.mp3
├── sfx/                      per-scene SFX cues built from shared library
├── overlays/                 text_overlays.json
├── <slug>_final.mp4          finished Short (music + SFX + overlays)
└── <slug>_final_branded.mp4  after /fk-brand-logo (CTA logo frame)
```

## Related Code Files

- CREATE: `skills/fk-video-hardscaper.md` (full file written in Phase 05)
- READ: `skills/fk-video-khkd.md`, `setup.py`, `CLAUDE.md`
- This phase = SPEC ONLY; no code yet.

## Implementation Steps

1. Lock the command signature + flag list above.
2. Write the identity table.
3. Write the output folder structure.
4. Define defaults: length 45s, 7 scenes, music on, brand on (if channel exists).
5. Define the `--area` rotation default and topic auto-pick rule.
6. Hand the spec to Phase 02 (scene logic) and Phase 05 (file authoring).

## Todo List

- [ ] Command signature + flags finalized
- [ ] Identity table drafted
- [ ] Output folder structure drafted
- [ ] Defaults documented
- [ ] `--area` auto-topic rule defined

## Success Criteria

- A reader can tell exactly what `fk-video-hardscaper` does and how to call it
  from the spec alone, without reading later phases.
- Spec contradicts nothing in CLAUDE.md or project memory.

## Risk Assessment

- **Risk:** scope creep toward a channel-operator. **Mitigation:** spec explicitly
  states "producer only, no MODE A dashboard" — lock it in line 1 of the skill.

## Security Considerations

- None — local-only video production, no credentials, no uploads in this skill.

## Next Steps

- Phase 02 consumes the scene count + duration defaults.
- Phase 05 consumes the whole spec to author the file.
