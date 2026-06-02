# Meta AI Video Generation: Build-vs-Buy Evaluation

**Date:** 2026-06-02  
**Status:** NO PUBLIC API / RESEARCH-ONLY for Movie Gen  
**Recommendation:** Movie Gen not viable for integration. Vibes app has limited automation potential.

---

## 1. Products & Capabilities

### Movie Gen (Text-to-Video Model)
- **Status:** Research model only. NOT released to public or developers.
- **What it does:** Text → 16-second video at 16 fps. Text → audio (45s). Image → video. Video editing/transformation.
- **Model size:** 30B parameter transformer (video) + 13B (audio).
- **Output:** Up to 16 seconds at 720p. Audio generation (Foley, ambient, instrumental music, dialogue synth at 48kHz).
- **Access:** Limited to select academic researchers + Blumhouse filmmakers via invitation. No API, no SDK, no public release date announced.

### Vibes App (AI Video Feed + Remix)
- **Launch:** September 2025 (Meta AI app feature). February 2026: spun out as standalone mobile app (testing Brazil/Mexico).
- **What it does:** Text-to-video generation + remix existing videos (change style, add music, alter details).
- **Features:** Create from scratch, modify existing, remix from Vibes feed. Cross-post to Instagram/Facebook Stories.
- **Monetization:** Freemium model planned (free tier + paid subscription for extra generations/month).
- **Access:** Mobile app only (web "coming soon" as of Feb 2026). No official API.
- **Note:** Relies on Movie Gen models internally; no public programmatic access documented.

### Edits App (AI Video Editor)
- **Launch:** April 2025 (standalone mobile app).
- **What it does:** AI-powered video editing (50+ preset prompts). NOT generation — transforms existing video clips (≤10s).
  - Change outfit/location/lighting/mood
  - Graphic novel style, vintage comics, video game aesthetic
  - AI object segmentation + style restyle (SAM model)
  - Personalized sound effects suggestions
- **Future:** Planned custom text-prompt editing (as of May 2026, still pending).
- **Access:** Mobile app. No API.

### Instagram/Facebook Reels AI Tools
- **Native to platform:** Animated backgrounds, visual effects, transitions for Stories/Reels.
- **Labeling:** "AI Creator" label (May 2026 test) + C2PA SynthID invisible watermark.
- **Quality:** Adequate for social backgrounds/quick effects. NOT standalone video generation.
- **Access:** In-app only. No API.

---

## 2. Official Public API / SDK Availability

**CRITICAL FINDING: NO OFFICIAL API EXISTS FOR ANY META VIDEO GENERATION PRODUCT.**

| Product | API? | SDK? | Developer Access? |
|---------|------|------|-------------------|
| **Movie Gen** | ❌ NO | ❌ NO | ❌ Research-only (invite). No dev program. |
| **Vibes** | ❌ NO | ❌ NO | Mobile/web app only. No automation. |
| **Edits** | ❌ NO | ❌ NO | Mobile app only. No automation. |
| **Instagram/FB Reels AI** | ❌ NO | ❌ NO | In-app presets only. No programmatic control. |

**Movie Gen Status:** CPO stated publicly that Movie Gen is "not ready anytime soon" — model is "still expensive and generation time too long." Safety concerns blocking release. No timeline announced.

**Llama API:** Meta's Llama API provides access to LLMs, not video generation.

**Veo 3.1 (Google, for comparison):** API available via Gemini API or Vertex AI. Pricing: $0.40/sec (Standard) or $0.15/sec (Fast). Native vertical (9:16) + 4K support. This is the competitive baseline your pipeline currently uses.

---

## 3. Pricing & Commercial Terms

### Movie Gen
- Free for academic researchers (select invitees only).
- No commercial product planned yet.

### Vibes App
- Freemium model: free tier + paid subscription (exact tier pricing not yet disclosed as of June 2026).
- Free tier: Limited generations/month.
- Paid tier: More monthly quota.

### Edits App
- Pricing: Not clearly documented. Appears bundled with Meta accounts (free or subscription).

### Commercial Usage Rights & Watermarking
- **NO commercial licensing** for Meta-generated video content.
- Meta's Terms of Service: Outputs NOT approved for commercial use (e.g., YouTube monetization, client work).
- **Watermarking:** SynthID (invisible) embedded in all output, + "AI Creator" label required on Instagram. Watermarks resistant to editing.
- **IP:** You retain rights to your input prompts. Meta retains broad reuse rights over outputs within Meta ecosystem.
- **YouTube specifically:** Meta AI generated videos are NOT licensed for commercial YouTube upload (violates ToS).

**Contrast with Veo 3.1:** Google grants commercial license for paid API access. Watermark optional. Suitable for YouTube monetization.

---

## 4. Quality & Limits vs. Veo 3 (Your Current Baseline)

### Video Output Specs

| Metric | Movie Gen | Veo 3.1 | Winner |
|--------|-----------|--------|--------|
| Max length | 16 sec | 8 sec | Movie Gen |
| Resolution | 720p (inferred) | 720p / 1080p / 4K | Veo 3.1 |
| Vertical (9:16) | Not confirmed | ✅ Native (Jan 2026) | Veo 3.1 |
| Audio generation | 45s synth (Foley, dialogue) | Dialogue only | Movie Gen (richer) |
| Quality (benchmark) | Competitive in research | Best in class (MovieGenBench) | Veo 3.1 |
| Physics realism | Not tested publicly | Superior per MovieGenBench | Veo 3.1 |

### Strengths/Weaknesses

**Movie Gen strengths:**
- Built-in audio synthesis (dialogue, Foley, music) — useful for podcast/narration workflows.
- 16s vs 8s gives more scene duration.
- Research-grade quality metrics competitive with Veo.

**Movie Gen weaknesses:**
- NO public access (research-only).
- NO vertical support (not mentioned).
- NO API for automation.
- Longer generation time (CPO stated this as blocker).
- NOT licensed for commercial use.
- Safety/content policies still being finalized.

**Veo 3.1 strengths:**
- Publicly available via API (Vertex AI, Gemini API).
- Native 9:16 vertical (critical for your YouTube Shorts).
- 4K upscaling.
- Commercial licensing on paid plans.
- Proven reliability in your pipeline.
- $0.15–$0.40/sec transparent pricing.

**Veo 3.1 weaknesses:**
- 8 sec max (vs 16 sec for Movie Gen).
- No native audio synthesis (you handle via TTS separately).

---

## 5. Terms of Service & Automation

### Meta's Stance on Automation
- **Explicit prohibition:** Unauthorized scraping, bots, automated data collection from Meta products violates ToS.
- **Bot detection:** Meta maintains anti-scraping team that detects patterns.
- **Enforcement:** Account suspension, legal action.

### Web App Scraping Risk
- Scraping `meta.ai` or Instagram/Facebook web UI to automate video generation = **VIOLATION**.
- Legal caveat (Jan 2024 ruling): Logged-off, public-data scraping of Meta's *websites* (not APIs) technically outside ToS scope. **But:** Reverse-engineering mobile app or automating logged-in access remains illegal.
- **Practical risk:** Meta will detect automation patterns → account ban.

### Verdict
- **No path to automated integration** via Vibes web app.
- Movie Gen: Not even available; future release likely gated by approved partners only (e.g., Blumhouse, studios).
- **Automation is explicitly against Meta's ToS.**

---

## Summary: Integration Viability

| Dimension | Verdict |
|-----------|---------|
| **Official API?** | ❌ NO (Movie Gen research-only; Vibes/Edits app-only) |
| **Programmatic access?** | ❌ NO |
| **Commercial licensing?** | ❌ NO |
| **Automation allowed?** | ❌ PROHIBITED (violates ToS) |
| **Timeline to public release?** | ⏳ "Not anytime soon" (CPO quote) |
| **Risk of scraping/bots?** | 🚫 HIGH (account ban likely) |

---

## Recommendation: STAY WITH VEO 3

### Why Meta is NOT viable for this pipeline:

1. **Movie Gen:** Trapped in research. No API, no timeline, no commercial licensing. Not a build option.
2. **Vibes:** Mobile/web UI only. Automation violates ToS. Manual labor only.
3. **No commercial rights:** Your YouTube Shorts business requires commercial licensing — Meta ToS forbids this.
4. **Watermarking mandatory:** SynthID + "AI Creator" label on all output. Impacts perceived quality/authenticity.

### Veo 3 remains optimal:

- ✅ **Public API** (Gemini API, Vertex AI).
- ✅ **Commercial licensing** on paid plans.
- ✅ **Vertical video native** (9:16, your Shorts format).
- ✅ **Proven in your pipeline** (lamplit, van-vo workflows).
- ✅ **Transparent pricing** ($0.15–$0.40/sec).
- ✅ **Quality competitive** (best on MovieGenBench).

---

## Unresolved Questions

1. **Movie Gen public release date?** Meta has not announced a timeline. CPO said "not anytime soon." Check `ai.meta.com` quarterly for updates.
2. **Vibes future API?** No indication that Meta plans to open an API for Vibes. May remain app-only long-term.
3. **Watermark optionality?** SynthID appears mandatory on all Meta AI outputs. No way to disable for commercial use.
4. **Academic researcher access to Movie Gen?** Unclear if available in your region (Vietnam). Would require Meta partnership application.

---

## Sources

- [Meta Movie Gen Research](https://ai.meta.com/research/movie-gen/)
- [Meta Movie Gen Blog](https://ai.meta.com/blog/movie-gen-media-foundation-models-generative-ai-video/)
- [Meta Movie Gen Paper](https://ai.meta.com/research/publications/movie-gen-a-cast-of-media-foundation-models/)
- [DataCamp Movie Gen Guide](https://www.datacamp.com/blog/movie-gen-meta)
- [TechCrunch: Vibes Standalone App (Feb 2026)](https://techcrunch.com/2026/02/05/meta-tests-a-standalone-app-for-its-ai-generated-vibes-videos/)
- [Android Central: Vibes Feed](https://www.androidcentral.com/apps-software/meta/meta-ai-app-new-vibes-feed-full-ai-generated-videos-you-can-remix)
- [TechCrunch: Meta Edits AI Video Editing (June 2025)](https://techcrunch.com/2025/06/11/meta-ai-gains-video-editing-capabilities/)
- [Meta Edits Help Center](https://www.meta.com/help/artificial-intelligence/996454095987249/)
- [Meta AI Terms of Service](https://www.facebook.com/legal/ai-terms)
- [Meta Automated Data Collection Terms](https://www.facebook.com/legal/automated_data_collection_terms)
- [Medium: Meta AI Commercial Use Restrictions](https://medium.com/@business.adrianmatuguina/you-can-now-make-videos-with-meta-ai-but-heres-why-you-shouldn-t-use-them-for-commercial-purposes-37238999c966)
- [Google Veo 3.1 Official](https://deepmind.google/models/veo/)
- [Google Veo 3.1 Gemini API Docs](https://ai.google.dev/gemini-api/docs/video)
- [TechCrunch: Veo 3.1 Vertical Video (Jan 2026)](https://techcrunch.com/2026/01/13/googles-update-for-veo-3-1-lets-users-create-vertical-videos-through-reference-images/)
- [Google Cloud: Veo 3.1 Lite & Upscaling](https://cloud.google.com/blog/products/ai-machine-learning/veo-3-1-lite-and-a-new-veo-upscaling-capability-on-vertex-ai)
- [LicenseOrg: AI Commercial Use Guide 2026](https://www.licenseorg.com/blog/ai-commercial-use-guide-2026)
- [Court Ruling on Meta Scraping (Jan 2024)](https://www.courthousenews.com/federal-judge-rules-against-meta-in-data-scraping-case/)
