# Flow Kit Skills - Stages Summary


This document explains the stages/steps inside each Flow Kit skill.


## fk-add-material
**Title**: fk-add-material — Image Material System

*No explicit stages/steps defined in the document.*

---

## fk-add-entity
**Title**: fk-add-entity — Add new entity to an existing channel universe

**Stages:**
- Step 1: Ask for Entity Details
- Step 2: Create Entity
- Output

---

## fk-add-video
**Title**: fk-add-video — Create a new episode inside an existing channel

**Stages:**
- Step 1: Fetch Project Entities
- Step 2: Ask for Video Details
- Step 3: Add New Entities (if any)
- Step 4: Create Video
- Step 5: Create Scenes
- Output

---

## fk-brand-logo
**Title**: fk-brand-logo — Apply Channel Branding (Intro + Outro + Logo + 4K Badge)

**Stages:**
- Step 1: Locate channel assets
- Step 2: Auto-detect resolution and select assets
- Step 3: Normalize intro/outro to match main video
- Step 4: Normalize main video audio
- Step 5: Concat intro + main + outro
- Step 6: Apply brand logo overlay
- Step 7: Apply 4K badge (if applicable)
- Step 8: Apply to thumbnails (if --thumbnails)
- Step 9: Cleanup and verify

---

## fk-camera-guide
**Title**: Camera Guide — Cinematic Video Prompts (Veo 3)

*No explicit stages/steps defined in the document.*

---

## fk-change-model
**Title**: fk-change-model — View & Change Video/Image Model Keys

**Stages:**
- Step 1: Show Current Models
- Step 2: Quick Select (Interactive)
- Step 3: Change a Model (Manual)
- Step 4: Verify

---

## fk-concat-fit-narrator
**Title**: fk-concat-fit-narrator

**Stages:**
- Step 1: Get project, video, and scenes
- Step 2: Locate video + TTS for each scene
- Step 3: Get TTS duration for each scene
- Step 4: Setup output directory
- Step 5: Determine output resolution
- Step 6: Trim + normalize + mix audio (per scene)
- Step 6b: Burn text overlays (per scene)
- Step 7: Create concat list and merge (with chain crossfade)
- Step 8: Verify and output

---

## fk-concat
**Title**: fk-concat

**Stages:**
- Step 1: Get project, video, and scenes
- Step 2: Determine video source for each scene
- Step 3: Setup output directory
- Step 4: Download videos (skip if local file exists)
- Step 5: Determine output resolution
- Step 6: Normalize + mix audio
- Step 7: Create concat list and merge
- Step 8: Verify and output

---

## fk-create-project
**Title**: fk-create-project

**Stages:**
- Step 1: Create project with all entities
- Step 2: Create video
- Step 3: Create scenes
- Step 4: Review and Update Scenes

---

## fk-creative-mix
**Title**: fk-creative-mix

**Stages:**
- Step 0: Cleanup previous creative-mix scenes
- Step 1: Analyze current video
- Step 2: Suggest a creative plan
- Step 3: Execute with user approval
- Step 4: Output

---

## fk-dashboard
**Title**: fk-dashboard

*No explicit stages/steps defined in the document.*

---

## fk-doctor
**Title**: fk-doctor

*No explicit stages/steps defined in the document.*

---

## fk-fix-uuids
**Title**: fk-fix-uuids

**Stages:**
- Step 1: Check entities
- Step 2: Check scenes
- Step 3: Output

---

## fk-gen-chain-videos
**Title**: fk-gen-chain-videos

**Stages:**
- Step 1: Pre-check
- Step 2: Set up end_scene_media_ids for chaining
- Step 3: Submit ALL video requests at once
- Step 4: Output

---

## fk-gen-images
**Title**: fk-gen-images

**Stages:**
- Step 0: Detect orientation
- Step 1: Pre-check — all references must be ready
- Step 2: Get scenes and classify by chain_type
- Step 3: Submit wave by wave
- Step 4: Verify media_ids are UUID
- Step 5: Output

---

## fk-gen-music
**Title**: fk-gen-music — Generate Music via Suno

**Stages:**
- Step 1: Choose a Template (Optional)
- Step 2: Generate Music
- Step 3: Check Results
- Step 4: Download
- Step 5: Use in Video (Optional)

---

## fk-gen-narrator
**Title**: fk-gen-narrator — Generate Narrator Text + TTS for All Scenes

**Stages:**
- Step 1: Load project, video, scenes
- Step 2: Check voice template
- Step 3: Generate narrator text for each scene
- Step 4: Save narrator_text to each scene
- Step 5: Show all narrator texts for review
- Step 6: Generate TTS for all scenes
- Step 7: Setup output directory
- Step 8: Verify and output

---

## fk-gen-refs
**Title**: fk-gen-refs

**Stages:**
- Step 1: Check health
- Step 2: Get entities
- Step 3: Submit ALL requests at once
- Step 4: Verify
- Step 5: Troubleshoot UNSAFE_GENERATION failures

---

## fk-gen-text-overlays
**Title**: fk-gen-text-overlays — Generate Text Overlays from Narrator Text

**Stages:**
- Step 1: Load project, video, scenes
- Step 2: Detect target language
- Step 3: Analyze each scene's narrator text
- Step 4: Generate text_overlays.json
- Step 5: Validate and save
- Step 6: Report

---

## fk-gen-tts-template
**Title**: fk-gen-tts-template — Generate Voice Template

**Stages:**
- Step 1: Create Voice Template
- Step 2: Listen & Verify
- Step 3: Link to Project

---

## fk-gen-videos
**Title**: fk-gen-videos

**Stages:**
- Step 0: Detect orientation
- Step 1: Pre-check — all scene images must be ready
- Step 2: Filter scenes needing video
- Step 3: Submit ALL requests at once
- Step 4: Verify
- Step 5: Output

---

## fk-import-voice
**Title**: fk-import-voice — Import Existing Voice as Template

**Stages:**
- Step 1: Locate the WAV file
- Step 2: Transcribe with faster-whisper
- Step 3: Register template in templates.json
- Step 4: Verify via API
- Step 5: Test voice clone

---

## fk-insert-scene
**Title**: fk-insert-scene

**Stages:**
- Step 1: Get current scenes
- Step 2: Create INSERT scene
- Step 3: Shift subsequent scenes
- Step 4: Output

---

## fk-monitor
**Title**: fk-monitor — Full Pipeline Monitor

**Stages:**
- Step 1: Resolve project and slug
- Step 2: Resolve video_id and scene count
- Step 3: Get Telegram chat_id
- Step 4: Send start notification
- Step 5: Poll loop
- Step 6: Stop conditions

---

## fk-pipeline
**Title**: fk-pipeline — Smart Full-Pipeline Orchestrator

**Stages:**
- Step 1: Resolve Project and State
- Step 2: Stage Routing
- Step 3: Run Each Stage
- Stage 0 — Ref Images
- Stage 1 — Scene Images
- Stage 2 — Scene Videos
- Stage 2.5 — Review Videos
- Stage 3 — Upscale (4K)
- Stage 4 — TTS Narration (parallel)
- Stage 5 — Rolling Downloads (parallel with upscale)
- Stage 6 — Concat
- Step 4: Poll Loop
- Step 5: Failure Handling
- Step 6: Final Summary

---

## fk-refresh-urls
**Title**: fk-refresh-urls

**Stages:**
- Step 1: Get project_id from video
- Step 2: Bulk refresh via TRPC
- Step 3: Verify refresh worked
- Step 4: Per-media fallback (if TRPC fails)

---

## fk-research
**Title**: fk-research — Fact-Check & Research Before Scripting

**Stages:**
- Step 1: Define Research Questions
- Step 2: Web Search — Gather Facts
- Step 3: Build Fact Sheet
- Step 4: Validate Against Content Policy
- Step 5: Save Research
- Step 6: Handoff to Project Creation

---

## fk-review-board
**Title**: fk-review-board

**Stages:**
- Steps

---

## fk-review-video
**Title**: fk-review-video

**Stages:**
- Step 1: Pre-check
- Step 2: Check scenes have completed videos
- Step 3: Run review via API
- Step 4: Interpret results
- Step 5: Act on results

---

## fk-status
**Title**: fk-status

*No explicit stages/steps defined in the document.*

---

## fk-switch-project
**Title**: fk-switch-project — Switch Active Project

**Stages:**
- Step 1: List Available Projects
- Step 2: Show Current Active Project
- Step 3: Switch Project
- Step 4: Verify
- Step 5: Clear (optional)

---

## fk-thumbnail-guide
**Title**: YouTube Thumbnail Guide — Hook-Worthy Design Rules

*No explicit stages/steps defined in the document.*

---

## fk-thumbnail
**Title**: fk-thumbnail

**Stages:**
- Step 1: Load project context
- Step 2: Create 2-LINE TEXT
- Step 3: Build 4 thumbnail prompts
- Step 4: Collect character refs
- Step 5: Generate 4 thumbnails
- Step 6: Resize to YouTube (1280x720)
- Step 7: Show all 4 and evaluate
- Step 8: Output

---

## fk-upload-image
**Title**: fk-upload-image

**Stages:**
- Step 1: Check health
- Step 2: Upload image
- Step 3: Apply the media_id
- Step 4: Verify

---

## fk-youtube-seo
**Title**: fk-youtube-seo — Generate YouTube Metadata (SEO-Optimized)

**Stages:**
- Step 1: Load project context + channel rules
- Step 2: Identify the NICHE
- Step 3: Generate HOOK TITLE
- Step 4: Generate DESCRIPTION
- Step 5: Generate HASHTAGS
- Step 6: Generate KEYWORDS (Tags)
- Step 7: Generate TIMESTAMPS
- Step 8: Output all metadata
- Step 9: Save backup (optional)

---

## fk-youtube-upload
**Title**: fk-youtube-upload — Upload Video to YouTube (Shorts + Long-form)

**Stages:**
- Step 1: Parse input and detect video type
- Step 2: Load channel rules
- Step 3: Validate against rules
- Step 4: Schedule (single or batch)
- Step 5: Generate or load SEO metadata
- Step 6: Upload
- Step 7: Verify and report
- Step 8: `--dry-run` mode

---
