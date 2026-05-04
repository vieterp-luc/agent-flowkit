Add a new entity (character, location, or visual asset) to an existing project (channel universe).

Usage: `/fk-add-entity <project_id>`

## Step 1: Ask for Entity Details
Ask the user for:
1. **Name** of the entity.
2. **Type**: `character`, `location`, or `visual_asset`.
3. **Description**: Visual appearance only (outfit, hair, architecture, style). No actions or story context. 
4. **Voice Description**: (Only for characters if TTS is needed).

*Note: For famous real people, follow the bypass rules (use alias, back/side view description) from `/fk-create-project`.*

## Step 2: Create Entity

```bash
curl -X POST http://127.0.0.1:8100/api/projects/<PID>/characters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "...", 
    "entity_type": "...", 
    "description": "...",
    "voice_description": "..."
  }'
```

## Output
Print success and remind the user:
"Entity added. Run `/fk-gen-refs <PID>` to generate its reference image before using it in any scenes."
