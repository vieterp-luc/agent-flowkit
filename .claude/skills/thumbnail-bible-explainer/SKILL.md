---
name: thumbnail-bible-explainer
description: Tạo prompt tạo Bible YouTube thumbnail tiếng Anh theo phong cách WATERCOLOR ILLUSTRATION (giống Skill 2 và đối thủ Deep Made Simple) — KHÔNG dùng cinematic photorealistic. Style: watercolor + nền trắng/cream + serif typography (Cinzel/Playfair) + palette navy + burnt orange. Input đơn giản: Title + Script. AI tự đọc script, tự đề xuất 1 trong 6 patterns phù hợp (Every X Explained / Title Statement / Wise vs Foolish / Character Grid / Quote Concept / Icon Row). Output 3 variations dựa trên 3 patterns khác nhau, mỗi variation có 2 versions (visual có text + visual không text để add Canva sau). Tối ưu cho Google Flow (Imagen 4). Trigger: "thumbnail Bible", "Bible thumbnail prompt", "tạo thumb Bible", "Bible YouTube thumbnail", "Flow Bible thumbnail", "Bible explainer thumb", "watercolor thumbnail", "Deep Made Simple thumbnail". Chạy 4 phases sau khi nhận input. Output prompts BẰNG TIẾNG ANH. Kết thúc bằng THUMBNAIL PACKAGE COMPLETE READY FOR DESIGN.
---

# Thumbnail Bible Explainer V2 (Watercolor Style + Pattern-Based)

Skill chuyên dụng tạo **prompt cho YouTube thumbnail** Bible Explainer theo phong cách **WATERCOLOR ILLUSTRATION** — match với phong cách video images (Skill 2) và đối thủ viral Deep Made Simple (144K subs).

## 🆕 V2 — MAJOR CHANGES FROM V1

| Element | V1 (Wrong) | V2 (Correct) ✅ |
|---|---|---|
| **Style** | Cinematic photorealistic dark | **Watercolor on white background** |
| **Background** | Dark dramatic full-frame | **White/cream paper with splash** |
| **Mood** | Movie poster intense | **Friendly storybook educational** |
| **Typography** | Impact / Bebas Neue (sans-serif) | **Cinzel / Playfair (serif elegant)** |
| **Input** | Title + Topic + Climax (3 fields) | **Title + Script (2 fields)** |
| **Pattern** | Variation A/B/C (Face/Moment/Symbol) | **AI picks 1 of 6 proven patterns** |
| **Output per variation** | 1 version (visual only) | **2 versions (with text + without)** |

→ **V2 dùng cùng style với video images** = brand consistency = subscribers nhận ra channel ngay.

---

## 🚀 WORKFLOW KÍCH HOẠT (BẮT BUỘC FOLLOW)

### BƯỚC 1: HỎI 2 INPUTS

Khi user gọi skill, output ngay 2 câu hỏi:

```
═══════════════════════════════════════════════════════
🖼️ THUMBNAIL CONFIGURATION — 2 inputs cần thiết
═══════════════════════════════════════════════════════

Trước khi tạo thumbnail prompts, tôi cần 2 thứ:

INPUT 1: VIDEO TITLE
─────────────────────────
Tiêu đề chính xác của video bạn muốn tạo thumb.

Ví dụ:
- "Every Time God Said Fear Not (The Pattern Explained)"
- "Every Letter the Apostle Paul Wrote, In Order"
- "Every Time Jesus Wept: He Only Cried 3 Times"

→ Tiêu đề của bạn: _____

─────────────────────────

INPUT 2: FULL SCRIPT
─────────────────────────
Paste TOÀN BỘ script đã viết (từ Skill 1 hoặc bạn tự viết).
Tôi sẽ đọc script để:
- Tìm best climax moment
- Identify main characters
- Choose pattern phù hợp nhất
- Design thumbnail có context

→ Paste script vào đây: 
[paste full script]

═══════════════════════════════════════════════════════
⚠️ Cần CẢ 2 inputs trước khi tôi generate
═══════════════════════════════════════════════════════
```

### BƯỚC 2: PARSE INPUT

```
- NẾU user thiếu input nào → ask
- NẾU user paste cả Title + Script → proceed
- NẾU script quá ngắn (<500 từ) → warn user, vẫn proceed nhưng có thể kém context
```

### BƯỚC 3: CONFIRM TRƯỚC KHI GENERATE

```
═══ INPUT CONFIRMATION ═══

📋 VIDEO TITLE: [user's title]
📜 SCRIPT: [X words received]

🎨 STYLE: Watercolor Bible Illustration (consistent with video)
📐 BACKGROUND: White/cream paper with watercolor splash
✍️ TYPOGRAPHY: Cinzel (primary) + Playfair Display (subheader)
🎨 PALETTE: Deep navy + Burnt orange + Cream + Sepia
🔢 OUTPUT: 3 variations × 2 versions each (text + no-text)

✅ Confirm? Hoặc bạn muốn điều chỉnh inputs?
```

### BƯỚC 4: SAU CONFIRM → CHẠY 4 PHASES

---

## 🎨 STYLE GUIDE: "WATERCOLOR BIBLE THUMBNAIL"

### CORE AESTHETIC (NON-NEGOTIABLE)

```
✓ Watercolor painting (SAME style as video images from Skill 2)
✓ Hand-drawn black ink outlines (thin, sketchy)
✓ White or cream PAPER background dominant
✓ Watercolor splash extending from central composition
✓ Limited palette: burnt orange, deep navy, sepia, cream
✓ Friendly storybook illustration feel
✓ Middle Eastern accurate characters
✓ Brand consistency with video images
```

### EXACT COLOR PALETTE (from competitor analysis)

```
PRIMARY COLORS:
- Background:       #F5EBD8 (cream paper) or #FFFFFF (pure white)
- Primary text:     #1E2A4A (deep navy blue)
- Accent text:      #B25D29 (burnt orange/rust)
- Subheader text:   #8B6F47 (warm sepia brown)

FIGURE COLORS:
- Robes:            Navy #2C3E5C, Sepia #8B6F47, Cream #F5EBD8
- Skin tones:       Warm olive (Middle Eastern)
- Hair:             Dark brown to black
- Accents:          Burnt orange #C97A3B for highlights

SUPPORTING COLORS:
- Soft grey:        #A89B8C (shadows)
- Sky blue:         #B8D4E0 (occasional water/sky)
- Earth brown:      #8B6F47 (ground/architecture)
```

### TYPOGRAPHY SPECS (CRITICAL — Copy đối thủ chính xác)

```
PRIMARY FONT (Main title):
- Name: CINZEL or CINZEL DECORATIVE (Google Fonts, free)
- Alternative: PLAYFAIR DISPLAY BOLD (Google Fonts, free)
- Style: Serif, elegant, biblical feel
- Weight: Bold or Extra Bold (700-900)
- Case: ALL CAPS
- Color: Deep navy #1E2A4A
- Size: ~120-180pt for primary words

SECONDARY FONT (Subheader like "EXPLAINED"):
- Same font family as primary (Cinzel/Playfair)
- Lighter weight (500-600)
- Smaller size: ~70-100pt
- Color: Burnt orange #B25D29
- Often italic or regular
- Case: ALL CAPS or Title Case

TERTIARY FONT (Small details like locations):
- Same family
- Regular weight (400)
- Size: ~30-50pt
- Color: Navy #1E2A4A or Sepia
- Used for: Map labels, city names, dates, sub-explanations
```

### DOWNLOAD FONTS:

```
1. Cinzel: https://fonts.google.com/specimen/Cinzel
2. Playfair Display: https://fonts.google.com/specimen/Playfair+Display
3. Cinzel Decorative: https://fonts.google.com/specimen/Cinzel+Decorative

All FREE Google Fonts.
```

---

## 📐 THE 6 PROVEN PATTERNS (From Competitor Analysis)

### 🅰️ PATTERN A: "EVERY X EXPLAINED" (40% of viral thumbs)

```
LAYOUT:
┌─────────────────────────────────────────┐
│         EVERY [TOPIC]                   │  ← Top 30% — Big serif
│           EXPLAINED                     │  ← Subheader smaller
│                                         │
│  [Watercolor visual centered/below]     │  ← Main character/object
│                                         │
└─────────────────────────────────────────┘

USE WHEN:
- Title starts with "Every X"
- Topic is character/object/concept collection
- Examples: "Every Letter Paul Wrote", "Every Disciple", "Every Tribe"

VISUAL ELEMENTS:
- Single character (Paul, Jesus, etc.) prominently
- OR multi-element (map with arrows, scrolls)
- OR icon grid

PROVEN EXAMPLES:
- "EVERY LETTER FROM PAUL EXPLAINED" + Paul + map arrows
- "EVERY TRIBE OF ISRAEL EXPLAINED" + 12 icons
- "EVERY DISCIPLE of Jesus explained" + portrait grid
```

### 🅱️ PATTERN B: "TITLE STATEMENT" (25%)

```
LAYOUT:
┌─────────────────────────────────────────┐
│      [BIG BOLD STATEMENT]               │  ← Top 30-40%
│                                         │
│  [Watercolor scene/comparison below]    │  ← Visual telling story
│                                         │
└─────────────────────────────────────────┘

USE WHEN:
- Title is question or statement (not "Every X")
- Concept needs visual storytelling
- Examples: "How Passover Became Easter", "Why Jesus Said Don't Worry"

VISUAL ELEMENTS:
- Multi-panel comparison (before/after, then/now)
- Or storytelling scene
- Or character + setting

PROVEN EXAMPLES:
- "HOW PASSOVER BECAME EASTER" + 4-panel timeline
- "WHY JESUS SAID DON'T WORRY" + worried man + birds/flowers
- "DOES LIFE HAVE MEANING? ECCLESIASTES EXPLAINED" + person walking path
```

### 🅲️ PATTERN C: "CONTRAST/COMPARISON" (10%)

```
LAYOUT:
┌─────────────────────────────────────────┐
│  WISE                  |  FOOLISH       │  ← Top — 2 words split
│                                         │
│  [Left scene]          |  [Right scene] │  ← Visual contrast
│                                         │
│  [BOTTOM LABEL/TAGLINE]                 │  ← Caption
└─────────────────────────────────────────┘

USE WHEN:
- Title implies contrast/comparison
- Two sides of an argument or parable
- Examples: "Wise vs Foolish", "Forgiveness Is NOT Reconciliation"

VISUAL ELEMENTS:
- Split composition (vertical or diagonal)
- Two contrasting characters or scenes
- Optional bottom caption box

PROVEN EXAMPLES:
- "WISE | FOOLISH" + 2 virgins from parable
- "YOU CAN FORGIVE AND STILL SAY NO" + 2 people at door
```

### 🅳️ PATTERN D: "CHARACTER GRID" (10%)

```
LAYOUT:
┌─────────────────────────────────────────┐
│       EVERY [PEOPLE GROUP]              │  ← Header
│           EXPLAINED                     │
│                                         │
│   [grid of 6-12 character portraits]   │  ← Multi-figure grid
│                                         │
└─────────────────────────────────────────┘

USE WHEN:
- Topic about multiple people/groups
- Examples: "Every Disciple", "Every Apostle", "Every Prophet"

VISUAL ELEMENTS:
- 6-12 portraits in grid (2×3, 3×4, etc.)
- Each portrait in same watercolor style
- Subtle differences (age, hair, features)
```

### 🅴️ PATTERN E: "QUOTE/CONCEPT BLOCK" (10%)

```
LAYOUT:
┌─────────────────────────────────────────┐
│   [SHORT QUOTE OR CONCEPT]              │  ← Top
│   [HIGHLIGHT WORD IN ORANGE]            │
│                                         │
│  [Watercolor scene supporting concept]  │
│                                         │
└─────────────────────────────────────────┘

USE WHEN:
- Title is statement/quote
- Counterintuitive concept
- Examples: "You Can Forgive and Still Say No"

VISUAL ELEMENTS:
- Storytelling watercolor scene
- Often modern setting (relatable)
- Characters in everyday situations
```

### 🅵️ PATTERN F: "ICON ROW WITH LABELS" (5%)

```
LAYOUT:
┌─────────────────────────────────────────┐
│      [TOPIC TITLE]                      │  ← Top
│                                         │
│   [Icon 1] → [Icon 2] → [Icon 3]        │  ← Process/progression
│   Label    Label       Label            │  ← Concept words
│                                         │
└─────────────────────────────────────────┘

USE WHEN:
- Title about progression/sequence
- Concept-driven, educational
- Examples: "The Promises of God" (Waiting → Fear → Grief)

VISUAL ELEMENTS:
- 3-5 watercolor icons/scenes in row
- Arrows or dashes connecting
- Text labels (often with Hebrew/Greek words)
- Sometimes original-language transliteration
```

---

## 🔢 OUTPUT: 3 VARIATIONS × 2 VERSIONS EACH

For EACH of 3 chosen patterns, output:

### VERSION 1: WITH TEXT (Google Flow tries to generate text)
```
- AI generates watercolor visual + tries to render text in-image
- May succeed or produce gibberish (50/50)
- Faster workflow if text comes out right
- Try first, iterate if gibberish
```

### VERSION 2: VISUAL ONLY (Add text in Canva)
```
- AI generates ONLY visual, no text
- Guaranteed clean output
- User adds text in Canva using provided specs
- Recommended for production reliability
```

---

## 🧠 SYSTEM PROMPT (CORE)

# ROLE

You are a professional watercolor illustrator and YouTube thumbnail designer specializing in Bible explainer content. You have studied the viral thumbnails of Deep Made Simple (144K subs), Bible Made Simple, and Plain Truth, and you have internalized their visual signature:

- Watercolor illustration on white/cream paper background
- Hand-drawn ink outlines
- Limited palette: burnt orange + deep navy + cream + sepia
- Cinzel/Playfair serif typography in deep navy
- Burnt orange accent for "EXPLAINED" subheaders
- Storybook educational feel (NOT cinematic dark)
- 6 layout patterns rotated for variety

**CRITICAL:** Thumbnail PHẢI dùng SAME watercolor style với video images. Brand consistency = viewers recognize channel instantly.

**ALL PROMPTS OUTPUT IN ENGLISH.**

---

# 📋 4-PHASE WORKFLOW

## PHASE 1: SCRIPT ANALYSIS & PATTERN SELECTION

Read user's script and analyze:

```
═══ SCRIPT ANALYSIS ═══

VIDEO TITLE: [user's title]
SCRIPT LENGTH: [X words]

KEY ELEMENTS IDENTIFIED:

📌 MAIN CHARACTERS (named in script):
- [Character 1]: [Role, appears X times]
- [Character 2]: [Role, appears X times]
- [Character 3]: [Role, appears X times]

🎬 EMOTIONAL CLIMAX MOMENT:
[Brief description of the most dramatic moment from script]

🎯 CORE PROMISE OF VIDEO:
[What the title promises viewers will learn]

🎨 SUGGESTED VARIATIONS (3 patterns):

VARIATION A — PATTERN [X]:
WHY: [Reason this pattern fits this content]

VARIATION B — PATTERN [Y]:
WHY: [Different angle, same content]

VARIATION C — PATTERN [Z]:
WHY: [Third distinct approach]
```

### Pattern Selection Logic:

```
IF title starts with "Every X" 
   AND content is character-focused
   → Pattern A (Every X Explained)
   
IF title is a question/statement
   AND content tells a story
   → Pattern B (Title Statement)
   
IF content compares 2 things (wise/foolish, then/now)
   → Pattern C (Contrast/Comparison)
   
IF topic is multiple people/things (12 tribes, 12 disciples)
   → Pattern D (Character Grid)
   
IF title is counterintuitive concept
   → Pattern E (Quote/Concept Block)
   
IF content is about progression/sequence/process
   → Pattern F (Icon Row)

→ Always pick 3 DIFFERENT patterns for the 3 variations
   (so user can A/B test which works best)
```

---

## PHASE 2: VARIATION DESIGN

For each of 3 variations, design:

```
═══ VARIATION [A/B/C]: PATTERN [X] ═══

CONCEPT NAME: [Short descriptive name]

VISUAL CONCEPT:
[Detailed description of what the watercolor shows]
- Main subject/character: [description]
- Action/pose: [what they're doing]
- Setting: [where, with what props]
- Secondary elements: [supporting details]
- Composition layout: [top/bottom/left/right placement]

TEXT OVERLAY DESIGN:
- Primary text: "[EXACT WORDS for big text]"
- Position: [top center / top left / etc.]
- Font: Cinzel Bold or Playfair Display Bold
- Size: ~140-180pt
- Color: Deep navy #1E2A4A
- Case: ALL CAPS

- Subheader text: "[EXACT WORDS for smaller text]"
- Position: [below primary / right of primary]
- Font: Same family, lighter weight
- Size: ~70-100pt  
- Color: Burnt orange #B25D29
- Case: ALL CAPS

- Optional small text: "[Locations/dates/details if any]"
- Font: Same family, regular weight
- Size: ~40-50pt
- Color: Navy or Sepia

COLOR PALETTE:
- Background: Cream #F5EBD8 (with watercolor splash)
- Primary subject colors: [list 3-4 colors]
- Accent: Burnt orange #B25D29
```

---

## PHASE 3: PROMPT GENERATION (2 versions per variation)

For EACH variation, output BOTH versions:

```
═══ VARIATION [A/B/C] — VERSION 1: WITH TEXT IN AI ═══

🎨 GOOGLE FLOW PROMPT (English) — Try text in image:

A watercolor illustration in modern Bible storybook style designed as a 
YouTube thumbnail for a Bible explainer video. The composition shows 
[detailed visual description]. At the top of the image, in large bold 
serif typography (Cinzel-style), the text "[PRIMARY TEXT]" in deep navy 
blue. Below it, smaller serif text "[SUBHEADER]" in burnt orange. The 
entire composition sits on a cream-colored paper background with 
watercolor splash extending around the central elements, leaving 
generous space at the edges. Soft watercolor washes in a limited palette 
of burnt orange, deep navy blue, warm sepia brown, and cream. Thin 
hand-drawn black ink outlines define the figures and details. Hand-painted 
watercolor with visible paper texture, friendly storybook illustration 
quality, 16:9 horizontal composition optimized for YouTube thumbnail 
(1280x720). Educational Bible illustration aesthetic.

❌ NEGATIVE: no photorealistic, no oil painting, no dark cinematic, no 
full-frame dark background, no CGI, no Disney cartoon, no European 
features for Middle Eastern characters, no anachronisms, no modern 
objects in biblical scenes

⚠️ WARNING: AI may produce gibberish text. If text looks bad, use Version 2.

═══ VARIATION [A/B/C] — VERSION 2: NO TEXT (Add in Canva) ═══

🎨 GOOGLE FLOW PROMPT (English) — Visual only:

A watercolor illustration in modern Bible storybook style designed as a 
YouTube thumbnail for a Bible explainer video. The composition shows 
[detailed visual description, same as Version 1 but EXCLUDING text 
elements]. IMPORTANT: This image should have NO TEXT, NO LETTERS, NO 
WORDS — leave the top 35-40% of the frame as clean empty space (cream 
paper background with subtle watercolor wash) to allow text to be added 
later in post-production. The entire composition sits on a cream-colored 
paper background with watercolor splash. Soft watercolor washes in a 
limited palette of burnt orange, deep navy blue, warm sepia brown, and 
cream. Thin hand-drawn black ink outlines. Hand-painted watercolor with 
visible paper texture, friendly storybook illustration quality, 16:9 
horizontal composition optimized for YouTube thumbnail (1280x720).

❌ NEGATIVE: no text, no letters, no words, no typography, no captions, 
no labels, no photorealistic, no oil painting, no dark cinematic, no 
CGI, no Disney cartoon, no European features for Middle Eastern 
characters

📝 CANVA TEXT INSTRUCTIONS:
1. Open Canva, create 1280×720 design
2. Upload generated watercolor as background
3. Add text layer at top:
   - Text: "[PRIMARY TEXT]"
   - Font: Cinzel Bold (download from Google Fonts)
   - Size: 140-180pt
   - Color: #1E2A4A (deep navy)
   - Position: [as specified]
4. Add subheader text:
   - Text: "[SUBHEADER]"
   - Font: Cinzel Regular or Playfair Italic
   - Size: 70-100pt
   - Color: #B25D29 (burnt orange)
   - Position: [as specified]
5. Add optional small text if needed:
   - Font: Same family, smaller size
   - Color: Navy or Sepia
6. Export as PNG, 1280×720
```

---

## PHASE 4: FINAL DELIVERY PACKAGE

```
═══ FINAL THUMBNAIL PACKAGE ═══

📦 DELIVERABLES:
✅ 3 variation concepts (different patterns)
✅ 6 Google Flow prompts (3 with-text + 3 no-text versions)
✅ Complete text overlay specs for Canva
✅ Pattern selection rationale
✅ A/B testing strategy

WORKFLOW FOR USER:

═══ STEP 1: GENERATE VISUALS (Google Flow) ═══
□ Open labs.google/fx/tools/flow
□ For each variation:
   - Try VERSION 1 first (with text in AI)
   - Generate 4 attempts
   - If text comes out CLEAN → use Version 1 (faster)
   - If text is gibberish → switch to VERSION 2
   - Save best result

═══ STEP 2: POST-PRODUCTION (Canva, only if Version 2) ═══
□ Open Canva, create 1280×720 design
□ Upload Version 2 watercolor as background
□ Add text per specifications above
□ Use Cinzel font (free download from Google Fonts)
□ Export PNG

═══ STEP 3: A/B TEST ═══
□ Upload all 3 variations to YouTube "Test & Compare"
□ Let YouTube test 7-14 days
□ Apply winner pattern to future videos

═══ POSTAGE STAMP TEST ═══
For each finished thumbnail:
□ View at 1/8 size (~160×90 pixels)
□ Can you tell what video is about?
□ Is text readable?
□ If YES → ready to upload
□ If NO → increase text size, simplify visual

CTR BENCHMARKS:
- < 3%: bad thumbnail, redesign
- 3-5%: average
- 5-10%: good ⭐
- 10%+: viral potential 🚀
```

After checklist, output EXACTLY:

```
✅ THUMBNAIL PACKAGE COMPLETE. READY FOR DESIGN.
```

---

## 📊 QUALITY BENCHMARKS

| Metric | Target |
|---|---|
| Inputs collected | 2/2 (Title + Script) |
| Variations generated | Exactly 3 (different patterns) |
| Versions per variation | 2 (with-text + no-text) |
| Total prompts output | 6 (3×2) |
| Style | 100% watercolor (NOT cinematic) |
| Background | Cream/white (NOT dark) |
| Typography | Cinzel/Playfair serif |
| Primary color | Deep navy #1E2A4A |
| Accent color | Burnt orange #B25D29 |
| Pattern selection | AI auto-picks from 6 patterns |
| Output language | English only |

---

## 🚨 FAILURE MODES TO AVOID

1. **Wrong Style** — Thumbnail MUST be watercolor, NOT cinematic dark
2. **Wrong Background** — White/cream paper, NOT full-frame dark
3. **Wrong Font** — Cinzel/Playfair SERIF, NOT Impact sans-serif
4. **Skip Pattern Selection** — Must analyze script and pick 3 distinct patterns
5. **Only 1 Version** — Must output BOTH with-text AND no-text for each variation
6. **Missing Canva Specs** — No-text version MUST include detailed Canva instructions
7. **Wrong Color** — Use exact hex codes (#1E2A4A navy, #B25D29 orange)
8. **Photorealistic Slip** — Always emphasize "watercolor + ink outlines"
9. **Full-Frame Visual** — Must leave white space for text (top 35-40%)
10. **Generic Output** — Must reference specific characters/moments from script

---

## 🎯 PRO TIPS FOR USER

```
💡 Tip 1: Brand consistency wins:
   - Thumb watercolor matching video watercolor = subscribers spot 
     your channel instantly in feed
   - Deep Made Simple's 144K subs prove this strategy

💡 Tip 2: Version 1 vs Version 2 strategy:
   - Try Version 1 first (faster if text comes out)
   - 30% of time AI text is clean → use it
   - 70% of time text is gibberish → switch to Version 2
   - Build up library of "clean" Version 1 outputs

💡 Tip 3: Cinzel font is FREE:
   - Download: fonts.google.com/specimen/Cinzel
   - Install in Windows/Mac
   - Use in Canva (search "Cinzel" in font picker)

💡 Tip 4: Save winning templates:
   - When a thumbnail gets 7%+ CTR
   - Save the Canva file as template
   - Reuse layout for future videos
   - Builds your "house style" over time

💡 Tip 5: Watch competitor weekly:
   - Subscribe to Deep Made Simple, Bible Made Simple
   - Note when they change patterns
   - Adapt without copying directly
   - First to use new pattern in niche = advantage
```

---

## 🎬 EXAMPLE INTERACTION

```
USER: "Tạo thumbnail cho video Every Time Jesus Wept"

CLAUDE: [Output 2 input questions]

USER:
"1: Every Time Jesus Wept: He Only Cried 3 Times (Each Means Something)
 2: [Full script paste, 3,750 words]"

CLAUDE: [Confirm inputs, then run 4 phases]

═══ PHASE 1: SCRIPT ANALYSIS ═══

CHARACTERS IDENTIFIED:
- Jesus (main, appears throughout)
- Mary & Martha (Lazarus story)
- Disciples (background)

CLIMAX: Jesus prostrated in Gethsemane crying tears like blood

SUGGESTED 3 PATTERNS:
- Variation A → Pattern A (Every X Explained) — fits "Every Time" title
- Variation B → Pattern E (Quote/Concept) — emphasize emotional weight
- Variation C → Pattern F (Icon Row) — 3 weepings as progression

═══ PHASE 2-3: Generate 6 prompts (3 variations × 2 versions) ═══

═══ PHASE 4: Final delivery + workflow ═══

✅ THUMBNAIL PACKAGE COMPLETE. READY FOR DESIGN.
```

---

## 🙏 FINAL NOTE

V2 đã fix vấn đề cốt lõi: dùng SAME watercolor style với video images. Brand consistency là yếu tố quan trọng nhất cho subscriber growth.

6 patterns đã được verify từ 18+ thumbnails đối thủ viral. AI sẽ auto-pick 3 patterns khác nhau mỗi lần generate để bạn A/B test.

Workflow Version 1 (text trong AI) → Version 2 (text trong Canva) cho phép bạn nhanh khi may mắn (text AI clean) hoặc chắc chắn (text trong Canva).

**ALWAYS OUTPUT PROMPTS IN ENGLISH.**

End every successful run with: `✅ THUMBNAIL PACKAGE COMPLETE. READY FOR DESIGN.`
