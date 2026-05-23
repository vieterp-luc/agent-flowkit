# Phase 6 — Write `skills/fk-build.md` + Register

## Context Links
- Parent: `plan.md`, Phases 1-5
- Sibling examples: `skills/fk-van-vo.md`, `skills/fk-podcast-book.md`, `skills/fk-video-bible-explainer.md`
- Reference: setup.py auto-discovers `skills/fk-*.md` (no manual registration)

## Overview
Write the actual `skills/fk-build.md` file. Single source of truth. Once written, run `python3 setup.py --tool claude` (and the other tool flags as appropriate) to regenerate `.claude/commands/fk-build.md` stub. Then add one row to `CLAUDE.md` skills table.

## Requirements

### Functional
- Single file: `skills/fk-build.md`.
- Self-contained — embeds all CLI dispatch, vision schemas, LOCK BLOCK templates, milestone tables, Veo prompt template, music prompt builder, ffmpeg snippets.
- Target ≤ 600 lines (will be the longest skill — comparable to `fk-van-vo.md` and `fk-podcast-book.md`).
- Honors KISS: prose dispatch, no Python helper unless needed; if Phase 3 helper script gets created, this skill calls it.

### Non-functional
- Pass `setup.py` discovery (correct front-matter, first line description).
- `.claude/commands/fk-build.md` regenerates cleanly.
- One line in `CLAUDE.md` skills table.

## Architecture / File Layout (proposed sections of `skills/fk-build.md`)

```
# fk-build — Universal 1-image → vertical timelapse Short

[1-line description for setup.py discovery]

Usage: /fk-build <image_path> [flags]

## Flags
| Flag | Default | Description |
...

## Pre-flight
curl :8100/health; gemini status; brand icon exists

## Phase A — Analyze
[vision classifier Q1-Q5 + 5 subject-specific analysis schemas + OBJECT/COMPONENT INVENTORY schema + Stage 0 archetype mapping]

## Phase B — Stage image gen
[Stage 0 prompt template + Stage k prompt template + per-subject N=4 milestones table + gemini CLI snippet + verify + halt-on-quota]

## Phase C — Veo transitions
[ephemeral Flow project bootstrap + upload + scene wire-up + probe + batch + poll + download + Veo transition prompt template + per-subject phase-action snippets]

## Phase D — Music + concat + brand
[Lyria prompt builder + Suno fallback + concat-with-trim + BGM mix + logo overlay + README recap]

## Output structure
output/fk_build/<slug>/...

## Common errors
quota, captcha, Lyria login expired, icon missing, dimensions wrong, drift

## How to resume
/fk-build <image> --slug <existing> --resume

## Examples
- House: /fk-build photos/villa.jpg
- Garden N=5: /fk-build photos/zen.jpg --stages 5
- Object cake: /fk-build photos/cake.jpg --subject object --object-subtype food
```

### CLAUDE.md table row (to add)
```
| `/fk-build` | 1 image → vertical timelapse Short (auto-classify house/garden/room/building/object) |
```
Insert alphabetically — between `/fk-brand-logo` and `/fk-camera-guide`.

## Related Code Files
- **Create:** `skills/fk-build.md`
- **Modify:** `CLAUDE.md` (1 table row insertion)
- **Auto-regen:** `.claude/commands/fk-build.md` (via `python3 setup.py --tool claude`)
- **Optional create:** `scripts/fk-build-render-stages.py` (if Phase 3 needs the helper — kebab-case per env naming convention; converted to snake_case import via `import importlib.util` if ever imported)

## Implementation Steps
1. Draft `skills/fk-build.md` skeleton with all section headers from architecture above.
2. Fill Phase A section from `phase-02-vision-classify-locks.md`.
3. Fill Phase B from `phase-03-stage-image-gen.md`.
4. Fill Phase C from `phase-04-veo-transitions.md`.
5. Fill Phase D from `phase-05-music-concat-brand.md`.
6. Add Output structure + Common errors + Resume + Examples.
7. Run `python3 setup.py --tool claude` to regenerate command stub.
8. Add CLAUDE.md row alphabetically.
9. Smoke-check: `cat skills/fk-build.md | wc -l` (target ≤ 600), `cat .claude/commands/fk-build.md` (should reference `skills/fk-build.md`).

## Todo List
- [ ] Skill file skeleton
- [ ] Phase A content
- [ ] Phase B content
- [ ] Phase C content
- [ ] Phase D content
- [ ] Output/errors/resume/examples sections
- [ ] Run setup.py --tool claude
- [ ] CLAUDE.md row insertion (alphabetical)
- [ ] Line-count sanity check (≤ 600)

## Success Criteria
- `cat skills/fk-build.md` is self-sufficient — a fresh agent reading only that file can dispatch the full pipeline.
- `python3 setup.py --tool claude` runs without errors and prints `fk-build` in the discovered list.
- `/fk-build` slash-command stub exists in `.claude/commands/`.
- `CLAUDE.md` shows the new row.

## Risk Assessment
- Risk: skill file balloons past 800 lines, hard to navigate. Mitigation: keep prose dense; split per-subject phase-action snippets into a single compact table; if still too long, factor the per-subject milestone table into `skills/fk-build-references/milestones.md` (only if needed; KISS prefers inline).
- Risk: setup.py front-matter mismatch breaks auto-discovery. Mitigation: match the `# fk-build —` first-line description format used by other fk-* skills (verify by grepping `head -1 skills/fk-*.md`).

## Security Considerations
- None new.

## Next Steps
- Phase 7: validation + smoke test against a real input image.
