# Camera Guide — Cinematic Video Prompts (Veo 3)

Reference for writing video prompts optimized for Google Veo 3. Veo 3 generates native audio (dialogue, SFX, ambient) from text — no audio upload needed.

## Prompt Fundamentals

- **Optimal length:** 100–150 words (3–6 sentences)
- **Style:** Natural prose — write like briefing a film director
- **Camera movement:** Always a **separate sentence** — never embed in action description
- **Audio:** Always describe at end of prompt with `Audio:`, `SFX:`, `Music:` labels
- **Negative prompt:** Always append `Negative: subtitles, watermark, text overlay`

### 5-Component Structure

```
[Camera/Shot] + [Subject] + [Action] + [Setting] + [Style & Audio]
```

| Component | Role | Rule |
|-----------|------|------|
| Camera | Shot type, angle, movement | Write as **separate sentence** |
| Subject | Character, object | Detailed: age, clothing, hair, identifying features |
| Action | Motion, emotion, dialogue | Can sequence multiple emotions in one prompt |
| Setting | Location, time, weather | Background + environment + props |
| Style & Audio | Visual aesthetic + sound | Audio labels at end of prompt, separated |

**Critical rule — camera as separate sentence:**
- Wrong: `A woman walks down the street as the camera dollies in with warm lighting`
- Right: `A woman walks down the street. The camera slowly dollies in.`

---

## Shot Types

| Shot | Keywords | Shows |
|------|----------|-------|
| **Extreme wide (EWS)** | `extreme wide shot` | Vast landscape, subject tiny |
| **Wide (WS)** | `wide shot` | Full subject + environment |
| **Medium (MS)** | `medium shot` | Waist up |
| **Close-up (CU)** | `close-up` | Face or detail |
| **Extreme close-up (ECU)** | `extreme close-up` | Eyes, hands, texture |
| **Macro** | `macro shot` | Microscopic detail |

## Camera Movements

| Movement | Keywords | Effect |
|----------|----------|--------|
| **Dolly in/out** | `dolly in`, `dolly out` | Move camera toward/away |
| **Pan** | `pan left`, `pan right` | Horizontal rotation |
| **Tilt** | `tilt up`, `tilt down` | Vertical rotation |
| **Tracking** | `tracking shot` | Follow subject |
| **Crane** | `crane up`, `crane down` | Raise/lower camera |
| **Gimbal glide** | `gimbal glide` | Smooth stabilized movement |
| **Handheld** | `handheld` | Natural shake, raw feel |
| **Whip pan** | `whip pan` | Ultra-fast horizontal snap |
| **Arc shot** | `arc shot` | Orbit around subject |
| **POV** | `POV shot` | First-person perspective |
| **Static** | `locked-off static` | Camera completely fixed |
| **Rack focus** | `rack focus` | Shift focus between subjects |
| **180-degree arc** | `180-degree arc` | Half-orbit around subject |

**Rule:** Write camera movement as its own sentence. One movement per shot.

## Camera Angles

| Angle | Keywords | Effect |
|-------|----------|--------|
| **Eye level** | `eye level shot` | Neutral, natural |
| **Low angle** | `low angle shot, looking up` | Power, dominance |
| **High angle** | `high angle shot, looking down` | Vulnerability |
| **Bird's eye** | `top-down overhead shot` | Scale, patterns |
| **Dutch angle** | `tilted Dutch angle` | Tension, unease |
| **Over-the-shoulder** | `over-the-shoulder shot` | Dialogue connection |
| **Worm's eye** | `extreme low angle from ground` | Dramatic, towering |

## Lens & Focal Length

| Lens | Keywords | Effect |
|------|----------|--------|
| **18mm wide-angle** | `18mm wide-angle` | Exaggerated perspective |
| **35mm** | `35mm` | Classic film look |
| **50mm** | `50mm` | Natural eye perspective |
| **85mm telephoto** | `85mm telephoto` | Compressed perspective, beautiful bokeh |
| **Anamorphic** | `anamorphic lens` | Cinematic widescreen, signature lens flares |

## Depth of Field & Focus

| Technique | Keywords | Effect |
|-----------|----------|--------|
| **Shallow DOF** | `shallow depth of field, soft bokeh` | Subject isolation |
| **Deep focus** | `deep focus, everything sharp` | Full context |
| **Rack focus** | `rack focus from foreground to background` | Shift attention |
| **Tilt-shift** | `tilt-shift, miniature look` | Whimsical, toylike |

---

## Lighting

Lighting creates the biggest difference in output quality. **Always include lighting description.**

| Technique | Keywords | Mood |
|-----------|----------|------|
| **Golden hour** | `golden hour light` | Warmth, nostalgia, romance |
| **High-key** | `high-key lighting` | Bright, even, upbeat |
| **Low-key** | `low-key lighting` | Dark, high contrast, dramatic |
| **Noir** | `noir lighting` | Strong shadows, mysterious |
| **Backlight / rim light** | `backlit, rim light` | Separates subject from background |
| **Soft natural** | `soft natural light` | Gentle, even |
| **Motivated** | `motivated lighting` | Light source logical in scene |
| **Warm/cool practicals** | `warm practicals`, `neon-lit` | In-scene light sources (lamps, neon) |
| **Tungsten** | `tungsten` | Warm yellow incandescent |
| **Fluorescent** | `fluorescent` | Cool greenish office light |
| **Neon** | `neon-lit` | Colorful, vibrant |
| **Candlelight** | `candlelight` | Warm, flickering, intimate |
| **Volumetric** | `volumetric light, god rays` | Ethereal, sacred |
| **Chiaroscuro** | `chiaroscuro, strong contrast` | Drama, film noir |
| **Blue hour** | `blue hour, twilight` | Mystery, melancholy |

---

## Audio — Veo 3's Native Audio Generation

Veo 3 generates all audio from text. Focus strictly on environmental sounds and physical effects, **excluding all character dialogue/speech**. Use specific labels at the end of the prompt:

### Layer 1: Sound Effects (SFX)

Specific, discrete sounds occurring in the scene:

```
SFX: the crack of a bat hitting a ball, crowd roaring
SFX: footsteps on gravel, a door creaking open
```

### Layer 2: Ambient / Background

Continuous background noise creating location realism:

```
Audio: distant city traffic, soft rain on windows
Audio: quiet hum of an office, keyboard typing
```

### Audio Placement

Always at the **end** of the prompt, with clear labels:

```
[Visual description...]

Audio: soft café chatter, espresso machine hissing.
SFX: ceramic cup placed on saucer.
Music: faint lo-fi jazz in background.
```

---

## Style Keywords

| Category | Keywords |
|----------|----------|
| **Film genre** | `cinematic`, `documentary`, `film noir`, `horror`, `rom-com` |
| **Camera feel** | `handheld`, `steadicam`, `found footage`, `security camera` |
| **Color grade** | `desaturated`, `teal and orange`, `warm vintage`, `cool blue` |
| **Film stock** | `35mm grain`, `16mm`, `Super 8`, `IMAX` |
| **Art style** | `anime`, `stop-motion`, `LEGO bricks`, `8-bit pixel art`, `watercolor` |
| **Era** | `1970s`, `retro VHS`, `Y2K aesthetic`, `futuristic` |
| **Override** | `In the style of...` → overrides default aesthetic |

## Speed & Time

| Technique | Keywords | Effect |
|-----------|----------|--------|
| **Slow motion** | `slow motion, time slows` | Dramatic emphasis |
| **Timelapse** | `timelapse, time passing` | Passage of time |
| **Speed ramp** | `speed ramp` | Dynamic rhythm change |

---

## Single-Shot Prompting

**Always use a single continuous shot** for an 8-second clip. Do not use transitions, cuts, or multi-shot techniques within a single prompt, as this splits the model's focus and creates unnatural pacing or jerky cuts.

Write the prompt focusing on a single, deliberate camera movement:

```
Wide establishing shot of a rainy city intersection at night,
neon signs reflecting on wet asphalt. A woman under a red 
umbrella waits at the crosswalk. The camera slowly dollies in.
Cinematic, desaturated teal and orange color grade.

Audio: rain pattering on pavement, distant traffic.
SFX: cars passing.
Negative: subtitles, watermark, text overlay.
```

### Single-Shot Rules

1. **One Camera Movement:** Keep the camera movement consistent (e.g., just `dolly in` or `tracking shot`).
2. **Limit Action Scope:** Describe only what the character can reasonably perform in 5-8 seconds. Too much action causes unnatural speed-ups.
3. **Keep Character Description Consistent:** Repeat exact identifying features if referencing multiple prompts across a project.
4. **Create a Scene Bible:** Lock environment, lighting, color grade → copy into every prompt in a sequence.

---

## Character Consistency

Since we use reference images via `imageInputs`, **don't describe character appearance** in prompts — write ACTION only. The reference image handles visual consistency.

However, for Veo 3 specifics:
- Save establishing shot as Element → reference for subsequent shots
- First-and-last-frame: define start + end frame → model generates motion between them
- `voice_description` on characters (max ~30 words) — auto-appended to video prompts by the worker

---

## Negative Prompt

Veo 3 supports negative prompts — list keywords to exclude (no instructive language):

- Wrong: `no walls, don't show cars`
- Right: `Negative: subtitles, watermark, text overlay`

**Standard negative (always include):**
```
Negative: subtitles, captions, watermark, text on screen, logo, blurry faces, distorted hands
```

**Situational additions:**

| Problem | Add to negative |
|---------|----------------|
| Subtitles appearing | `subtitles, captions` |
| Text overlay | `text overlays, watermarks` |
| Laugh track | `studio audience laughter` |
| Unwanted music | `background music` |
| Over-cinematic | `editorial narration` |

---

## Prompt Template

```
[Shot type] of [subject with detailed description], [action/emotion].
[Camera movement as separate sentence]. [Setting + time of day + weather].
[Lighting description]. [Style/aesthetic].

Audio: [ambient sounds].
SFX: [specific sound effects].
Music: [background music description].

Negative: subtitles, watermark, text overlay, [other unwanted elements]
```

---

## Examples

### Documentary/Military Scene
```
Medium shot of a soldier in olive fatigues sprinting across a barren
autumn road, military jeep smoking in the background. The camera tracks
him with handheld movement, slight shake. Overcast grey sky, cold
diffused light, breath visible in freezing air, determined expression. 
Shallow depth of field, dramatic side lighting from the overcast sky.

Audio: cold wind, distant engine rumble.
SFX: boots pounding on asphalt, gravel crunching underfoot.
Negative: subtitles, watermark, text overlay, blurry faces.
```

### Emotional Discovery Scene
```
Over-the-shoulder shot of Luna kneeling at the edge of a chocolate river,
dipping a paw into the flowing chocolate. The camera slowly dollies in.
Soft diffused golden hour light, shallow depth of field. Luna lifts her 
paw with a slow motion drip catching the warm backlight, arms raising 
in wonder at the cotton candy clouds.

Audio: gentle river flowing, warm breeze through candy trees.
SFX: chocolate dripping, soft rustling.
Negative: subtitles, watermark, text overlay.
```

### Action Sequence
```
Low angle shot of a hero charging across a castle bridge at dawn, sword
raised high, golden light catching the blade. The camera tracks alongside
with handheld energy. Warm golden hour, long shadows on ancient stone,
wind whipping his cloak. His jaw is set with determination, reflected 
golden glow in his eyes, castle gate looming behind.

Audio: wind howling across stone bridge.
SFX: sword ringing, boots on stone, cloak snapping in wind.
Negative: subtitles, watermark, text overlay, blurry faces.
```

---

## Cinematique Reference Library (Knowledge Base)

For advanced cinematic techniques beyond the fundamentals listed above, `mz-flowkit` references the **[Cinematique Library](https://github.com/thuongtin/cinematique)**. This external knowledge base contains 150+ deep-dive techniques spanning Camera Work, Lighting, Composition, and VFX.

**How to use Cinematique with Veo 3:**
When a specific mood or high-end artistic look is required, draw exact phrasing from the Cinematique `.md` notes rather than inventing generic descriptors.

*   **Lighting Examples:** Instead of `"dark lighting"`, use specific terms like `"Chiaroscuro lighting with a single candle... the Caravaggio treatment"`. Instead of `"bright"`, use `"High-Key Lighting"`.
*   **Composition Examples:** Use `"Rule of Thirds"`, `"Symmetry"`, `"Leading Lines"`, or `"Foreground Interest"`.
*   **Camera Work Examples:** Pull advanced movements like `"Crash Zoom"`, `"Whip Pan"`, or `"Vertigo Effect"`.

*Local Integration:*
The library has been embedded directly into this project as a submodule. LLMs and agents should cross-reference `data/cinematique/notes/*.md` for specific AI prompt templates, ensuring maximum aesthetic fidelity without altering codebase logic.

---

Before submitting any video prompt, verify:

- [ ] Prompt is 100–150 words, 3–6 sentences
- [ ] Subject described with detail (unless ref image handles it)
- [ ] Camera movement written as **separate sentence**
- [ ] Lighting/color temperature described
- [ ] Audio / SFX / Music labels at end of prompt
- [ ] Strictly single-shot continuous action (no "cut to", no multi-shot)
- [ ] No character dialogue or speech
- [ ] Action is simple enough to fit naturally within 8 seconds
- [ ] Negative prompt included (at minimum: `subtitles, watermark`)
- [ ] No abstract words — everything is visual/audible and specific
- [ ] Reference characters appear consistently across shots (action only)

## Common Mistakes

| Wrong | Right |
|-------|-------|
| Prompt < 50 words, too generic | 100–150 words, specific per component |
| Camera movement embedded in action sentence | Camera movement = separate sentence |
| Including character dialogue | Remove all dialogue/speech |
| Writing multi-shot sequences or cuts | Use single continuous shot per prompt |
| No audio description → silent or weird audio | Always write `Audio:` / `SFX:` at end |
| Using `no`, `don't` in negative prompt | List keywords: `subtitles, watermark` |
| Character changes between scenes | Repeat exact identifying features every prompt |
| Missing lighting description | Always include lighting + color temperature |
| Vague words like `"cinematic"` alone | Specify: `shallow DOF + golden hour + dolly in` |
| `"Camera zooms"` — too vague | `The camera slowly dollies in.` (separate sentence) |
| No negative prompt | Always: `Negative: subtitles, watermark, text overlay` |
