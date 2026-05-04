# YouTube Channel Workflow Plan (mz-flowkit)

**Objective**: Evolve the FlowKit architecture to treat `Projects` as YouTube Channels (reusable entity universes) and `Videos` as independent episodes that utilize the channel's assets.

## Phase 1: New Skills for Expansion
1. **Create `skills/fk-add-video.md`**: 
   - A new workflow that takes a `project_id`, fetches existing entities, asks the user for a new story, creates a new Video (`POST /api/videos`), and generates Scenes that link back to the channel's existing `character_names`.
2. **Create `skills/fk-add-entity.md`**:
   - A lightweight workflow to add new characters/locations to an existing project (`POST /api/projects/<PID>/characters`) as the channel universe expands.

## Phase 2: Refactoring Existing Skills
3. **Update `skills/fk-pipeline.md`**:
   - Modify the usage syntax to `/fk-pipeline [project_id] [video_id] [options]`.
   - Update the state detection logic to target a specific `video_id` instead of blindly taking `[0]`.
   - Add logic to select the most recent video or ask the user if multiple videos exist.
4. **Update `skills/fk-status.md`**:
   - Add support for `/fk-status <PID> <VID>`.
   - If no `<VID>` is provided, summarize the list of videos (Title, Status) without dumping every scene. If `<VID>` is provided, print the detailed scene table.

## Phase 3: Documentation Updates
5. **Update `skills/fk-create-project.md`**:
   - Conceptual shift: Define the project creation as "Creating a Channel Universe & Episode 1".
6. **Update `skills/README.md` and `skills/SKILLS_STAGES.md`**:
   - Register the new `fk-add-video` and `fk-add-entity` skills into the pipeline documentation.
