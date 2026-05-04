Create a new Video (episode) inside an existing Project (channel universe).

Usage: `/fk-add-video <project_id>`

## Step 1: Fetch Project Entities

```bash
curl -s http://127.0.0.1:8100/api/projects/<PID>/characters
```

Show the user the current entities available in the channel (Characters, Locations, Visual Assets).

## Step 2: Ask for Video Details
Ask the user for:
1. **Title** of the new video.
2. **Story** (brief plot summary for this specific episode).
3. **Number of scenes** and **orientation** (VERTICAL or HORIZONTAL).
4. **New Entities**: Does this episode introduce any new characters or locations that aren't in the project yet? 
   - If YES, ask for their name + visual description (appearance only, no scene context).

## Step 3: Add New Entities (if any)
For each new entity required:
```bash
curl -X POST http://127.0.0.1:8100/api/projects/<PID>/characters \
  -H "Content-Type: application/json" \
  -d '{"name": "...", "entity_type": "character|location|visual_asset", "description": "..."}'
```

## Step 4: Create Video

```bash
curl -X POST http://127.0.0.1:8100/api/videos \
  -H "Content-Type: application/json" \
  -d '{"project_id": "<PID>", "title": "...", "video_story": "...", "orientation": "VERTICAL|HORIZONTAL"}'
```

Save the returned `video_id`.

## Step 5: Create Scenes
Follow the exact same prompt-writing rules and chain structure (ROOT vs CONTINUATION) as detailed in `/fk-create-project`.
Reference the project's entities (both existing and newly added) in the `character_names` array.

```bash
curl -X POST http://127.0.0.1:8100/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "<VID>", 
    "display_order": N,
    "prompt": "...", 
    "video_prompt": "...", 
    "character_names": ["Entity1", "Entity2"], 
    "chain_type": "ROOT|CONTINUATION",
    "parent_scene_id": "..."
  }'
```

## Output
Print a summary table:
- Project ID, Video ID
- All scenes with prompts (truncated) and chain type
- Next step: 
  - If new entities were added: "Run `/fk-gen-refs <PID>` first, then `/fk-gen-images <PID> <VID>`"
  - If no new entities: "Run `/fk-gen-images <PID> <VID>`"
