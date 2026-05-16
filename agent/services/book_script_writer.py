"""Gemini-powered script writer: book text/outline → structured JSON script.

Uses the multi-key rotation pool from agent.services.gemini_key_pool.
"""
import json
import logging

logger = logging.getLogger(__name__)

_NARRATOR_RULE = (
    "NARRATOR RULE: Each narrator_text MUST be exactly 20-22 Vietnamese words "
    "(count by splitting on spaces; allow up to 23 tokens if punctuation is attached). "
    "Do NOT write longer or shorter sentences."
)

_SCENE_RULE = (
    "SCENE PROMPT RULE: All scene_prompts MUST be in English, "
    "cinematic style, suitable for AI image generation (Imagen). "
    "Each prompt: 1 sentence, describe setting + mood + lighting.\n\n"
    "CULTURAL CONTEXT (CRITICAL): Match the book's cultural origin in visuals.\n"
    "- For Vietnamese books (author with Vietnamese name): scenes MUST depict Vietnamese settings — "
    "rural villages with tiled roofs, rice paddies, banyan trees, riverside markets, old wooden schools; "
    "Vietnamese people (Asian appearance), traditional clothing (áo dài, áo bà ba, white school uniforms, conical hats nón lá); "
    "vintage 1960s-1990s Vietnam aesthetic; warm tropical light, monsoon greens, dusty earth tones.\n"
    "- AVOID generic Western/American settings (modern offices, coffee shops, English signage, Caucasian faces) "
    "unless the story explicitly takes place there.\n"
    "- Specify cultural markers explicitly in the prompt (e.g. 'Vietnamese countryside', 'áo dài', 'rural Vietnam')."
)

_SUMMARY_SYSTEM = f"""You are a Vietnamese podcast scriptwriter for YouTube book summary videos (5-8 minutes).
Your job: transform book content into engaging Vietnamese narration scripts.

{_NARRATOR_RULE}
{_SCENE_RULE}

CRITICAL: Narration must NEVER mention the book title or author name. Deliver the WISDOM and IDEAS only — pure content, no attribution speech. Listeners want insights, not citations.

Output ONLY valid JSON matching this exact schema — no markdown, no code fences:
{{
  "book": {{"title": "...", "author": "..."}},
  "hook": {{"narrator_text": "...", "scene_prompts": ["..."]}},
  "sections": [
    {{"title": "...", "narrator_text": "...", "scene_prompts": ["...", "..."]}}
  ],
  "outro": {{"narrator_text": "...", "scene_prompts": ["..."]}},
  "estimated_duration_seconds": 420
}}

Guidelines:
- Hook: 1 powerful opening sentence (NO book/author mention) — pure idea/question hooking viewer
- Sections: 5-8 sections covering key lessons/principles; each has 1 narrator sentence + 2-3 scene prompts
- Outro: 1 closing reflection sentence — NO "subscribe / follow / read the book" CTA, just a wrap-up insight
- estimated_duration_seconds: target_minutes * 60
- "book" field is metadata ONLY (used in caption/description, never spoken)
"""

_CHAPTERS_SYSTEM = f"""You are a Vietnamese book analyst. Your job: identify the main chapters / principles / themes of a book.

Output ONLY a valid JSON object — no markdown, no code fences:
{{
  "chapters": [
    {{
      "id": 1,
      "title": "Tiêu đề chương ngắn (Vietnamese, 4-8 từ)",
      "key_idea": "Ý chính cốt lõi của chương (Vietnamese, 20-30 từ)",
      "summary": "Tóm tắt 30-60 từ Vietnamese, đủ context để làm video về chương này"
    }}
  ]
}}

Guidelines:
- Cap output at max_chapters provided in user prompt
- For self-help books with N principles → 1 principle = 1 chapter
- For narrative books → break into thematic sections (not literal chapters)
- Title should be DISTINCT and SEARCHABLE (avoid generic titles like "Chương 1")
- key_idea should let user immediately know if they want a video on this topic
- summary gives enough context so a downstream extract-script call can use it as outline
"""


_CHAPTER_PODCAST_SYSTEM = """You are an English podcast scriptwriter for an international YouTube channel that covers classic literature chapter-by-chapter.
Your job: turn one book chapter (or grouped chapters) into a 10-15 minute English narration in the 4-act podcast structure.

NARRATOR RULE: All narrator_text is ENGLISH, written for spoken delivery at podcast pace (~135 wpm at TTS speed 0.9). Use natural sentence rhythm with em-dashes, contractions, and rhetorical pauses. NO Vietnamese.

WORD-COUNT TARGETS per section (count by splitting on spaces):
- Hook: 110-130 words (~55-65 seconds spoken)
- Each Summary section: 100-130 words (~50-60 seconds)
- Each Analysis section: 100-160 words (~55-70 seconds)
- Outro: 110-130 words (~55-65 seconds)

SCENE PROMPT RULE: All scene_prompts in ENGLISH, cinematic oil-painting style suitable for AI image generation (Imagen).
- 1-2 sentences each, describing setting + composition + mood + lighting
- For Frankenstein and other gothic classics: late 1700s/1800s European setting, candlelit, painterly, Caspar David Friedrich / Goya / Fuseli influence
- Period-strict: NO modern objects, electricity, cars, contemporary clothing
- Use entity aliases from project entities (e.g. "The Scientist", "The Creature") rather than character real names

4-ACT STRUCTURE (REQUIRED):

1. HOOK (1 section) — 110-130 words:
   - Open with greeting + book title + author + chapter name
   - State a quote or question from the chapter that hooks viewers
   - Tease what they'll learn
   - Example open: "Welcome back, fellow readers. Today we open Frankenstein by Mary Shelley — and the very first chapter holds a line that defines the entire novel..."

2. SUMMARY (5-7 sections) — 100-130 words each:
   - Retell plot in own words
   - Each section MUST start with a time connector: First / Next / Then / Suddenly / Meanwhile / Later / Finally / In the end
   - Use vivid sensory language but stay faithful to the source

3. ANALYSIS (3-5 sections) — 100-160 words each:
   - Explain character motivations, metaphors, symbols, themes
   - Address the WHY, not the WHAT
   - Connect to real-world insight or modern relevance
   - Each section has a clear topic label

4. OUTRO (1 section) — 110-130 words:
   - MUST include a subscribe CTA ("Hit subscribe / don't miss / follow for")
   - MUST include a comment-engagement question
   - MUST tease the next chapter by name or theme
   - Warm sign-off ("See you next chapter")

Output ONLY valid JSON matching this exact schema — no markdown, no code fences:
{
  "book": {"title": "...", "author": "..."},
  "chapter": "Chapter 1: ... (or Letters 1-4, etc.)",
  "hook": {
    "narrator_text": "...",
    "scene_prompt": "english cinematic scene description",
    "duration_target_sec": 60
  },
  "summary": [
    {
      "section": 1,
      "title": "Short label",
      "time_connector": "First",
      "narrator_text": "First, ... (100-130 words)",
      "scene_prompt": "english scene",
      "duration_target_sec": 55
    }
  ],
  "analysis": [
    {
      "section": 1,
      "topic": "The Green Light Symbol (or relevant theme)",
      "narrator_text": "(100-160 words)",
      "scene_prompt": "english scene",
      "duration_target_sec": 65
    }
  ],
  "outro": {
    "narrator_text": "(110-130 words, includes subscribe CTA + comment question + next-chapter tease)",
    "scene_prompt": "english scene",
    "duration_target_sec": 60,
    "cta_subscribe": true,
    "comment_question": "Short engagement question for description",
    "next_chapter_tease": "Chapter 2: ... or theme of next ep"
  },
  "estimated_duration_seconds": 720
}

Guidelines:
- Total word count target: 1100-1860 (=10-15 minutes at 135 wpm)
- All narrator_text in idiomatic English with natural podcast cadence
- Reference real character names in narration (it's a literature podcast — transparency is expected)
- Stay faithful to the source chapter; do not invent events
- estimated_duration_seconds = target_minutes * 60
"""


_CHAPTER_PODCAST_VI_SYSTEM = """Bạn là một biên kịch podcast tiếng Việt cho kênh YouTube tóm tắt sách dài (10-15 phút mỗi chương).
Nhiệm vụ: chuyển một chương của sách thành kịch bản narration tiếng Việt theo cấu trúc 3-act (Mở đầu + Tóm tắt + Kết).

NARRATOR RULE: Mỗi câu narrator_text PHẢI đúng 20-22 TỪ tiếng Việt (đếm bằng split khoảng trắng; cho phép tối đa 23 tokens nếu dấu câu liền). KHÔNG viết câu dài hoặc ngắn hơn.

WORD-COUNT TARGETS per section:
- Hook: 100-130 từ (~5-6 câu) → ~1 phút
- Mỗi section trong Summary: 80-110 từ (~4-5 câu)
- Tổng Summary: 700-1100 từ (7-10 sections)
- Outro: 100-130 từ → ~1 phút

CẤU TRÚC 3-ACT (BẮT BUỘC — KHÔNG có Analysis):

1. HOOK (1 section) — 100-130 từ:
   - Mở đầu chào khán giả + nêu tên sách + tác giả + chương đang nói
   - Đưa câu quote hấp dẫn hoặc câu hỏi gây tò mò
   - Ngắn gọn hé lộ điều khán giả sắp được nghe
   - Tone ấm áp, gần gũi, giống đang kể chuyện cho bạn

2. SUMMARY (7-10 sections) — 80-110 từ mỗi section:
   - Kể lại cốt truyện chương BẰNG LỜI MÌNH (không đọc nguyên văn sách)
   - MỖI section BẮT BUỘC bắt đầu bằng từ nối thời gian Việt:
     "Đầu tiên" / "Thoạt đầu" / "Mở đầu" / "Sau đó" / "Tiếp theo" / "Khi ấy"
     / "Một hôm" / "Hằng ngày" / "Bỗng nhiên" / "Đột nhiên" / "Bất ngờ"
     / "Trong khi đó" / "Cùng lúc" / "Lúc này" / "Vì vậy" / "Thế là"
     / "Hậu quả là" / "Cuối cùng" / "Tới cùng" / "Sau hết" / "Rồi"
   - Dùng ngôn ngữ kể chuyện sinh động (cảm xúc, không gian, hành động)
   - Trung thành với cốt truyện gốc, không sáng tác

3. OUTRO (1 section) — 100-130 từ:
   - Câu kết suy ngẫm về chương vừa kể
   - CTA tự nhiên (KHÔNG sale-y): "Nếu bạn thấy hay, hãy theo dõi để không bỏ lỡ chương sau"
   - Đặt 1 câu hỏi thảo luận để khán giả comment
   - Hé lộ chương kế tiếp 1 câu

SCENE PROMPT RULE: Tất cả scene_prompts viết BẰNG TIẾNG ANH (vì AI image generation tốt hơn với English), nội dung mô tả cinematic oil painting style.
- 1-2 câu mỗi prompt
- Mô tả setting + composition + mood + lighting
- BẮT BUỘC dùng entity aliases tiếng Anh từ project (vd "The Young Cricket", "Cricket Burrow") thay vì tên Việt nhân vật
- Bối cảnh Việt Nam thế kỷ 20: làng quê, áo nâu, khăn rằn, đèn dầu, đồng cỏ, sông nước
- Phong cách: oil painting children's book illustration, Beatrix Potter + Đông Hồ folk art
- KHÔNG có modern objects, NO contemporary clothing, NO English text trong image, NO Vietnamese text trong image

Output CHỈ valid JSON theo schema sau — không markdown, không code fences:
{
  "book": {"title": "...", "author": "..."},
  "chapter": "Chương N: tên chương",
  "hook": {
    "narrator_text": "(100-130 từ tiếng Việt)",
    "scene_prompt": "(english cinematic description)",
    "duration_target_sec": 60
  },
  "summary": [
    {
      "section": 1,
      "title": "(label ngắn tiếng Việt)",
      "time_connector": "Đầu tiên",
      "narrator_text": "(80-110 từ, bắt đầu bằng từ nối)",
      "scene_prompt": "(english scene description)",
      "duration_target_sec": 55
    }
  ],
  "outro": {
    "narrator_text": "(100-130 từ tiếng Việt, có CTA + câu hỏi + tease)",
    "scene_prompt": "(english scene)",
    "duration_target_sec": 60,
    "comment_question": "(câu hỏi ngắn cho viewer comment)",
    "next_chapter_tease": "(1 câu hé lộ chương sau)"
  },
  "estimated_duration_seconds": 720
}

Guidelines:
- Tổng từ target: 900-1500 (~10-13 phút @ TTS speed 0.85)
- TUYỆT ĐỐI KHÔNG có section "analysis" — chỉ 3-act
- Có thể nhắc tên nhân vật tiếng Việt (Dế Mèn, Dế Choắt, Chị Cốc) trong narrator (audio không bị Flow filter)
- Trung thành với chương gốc, không thêm sự kiện
- estimated_duration_seconds = target_minutes * 60
"""


_QUOTE_SYSTEM = f"""You are a Vietnamese podcast scriptwriter for vertical 9:16 TikTok/Reels podcast-style videos (2-3 minutes per episode).
Your job: take a powerful quote/idea from a book and craft a contemplative podcast narration around it.

{_NARRATOR_RULE}
{_SCENE_RULE}

CRITICAL: Narration must NEVER mention the book title or author name. Deliver the WISDOM and IDEAS only — pure content, no attribution speech. Listeners want insights, not citations.

Output ONLY a valid JSON array — no markdown, no code fences:
[
  {{
    "quote": "Trích dẫn cốt lõi (Vietnamese, 20-22 từ) — câu mở đầu mạnh nhất",
    "insights": [
      {{"narrator_text": "Câu 1 (20-22 từ Vietnamese) - bối cảnh/setup", "scene_prompt": "english cinematic scene"}},
      {{"narrator_text": "Câu 2 (20-22 từ) - đào sâu lý do/cơ chế", "scene_prompt": "english scene"}},
      {{"narrator_text": "Câu 3 (20-22 từ) - ví dụ thực tế cuộc sống", "scene_prompt": "english scene"}},
      {{"narrator_text": "Câu 4 (20-22 từ) - phản đề/contrast (làm khác đi thì sao)", "scene_prompt": "english scene"}},
      {{"narrator_text": "Câu 5 (20-22 từ) - hệ quả nội tâm/tình cảm", "scene_prompt": "english scene"}},
      {{"narrator_text": "Câu 6 (20-22 từ) - cách áp dụng cụ thể", "scene_prompt": "english scene"}},
      {{"narrator_text": "Câu 7 (20-22 từ) - lưu ý/caveat", "scene_prompt": "english scene"}}
    ],
    "outro": "Câu kết suy ngẫm (20-22 từ) - NO book/author mention, just a wrap-up reflection",
    "source_book": {{"title": "...", "author": "..."}}
  }}
]

Guidelines:
- Total narrator sentences (quote + 7-10 insights + outro) ≈ 9-12 sentences × ~6-7s each = 60-90s of TTS
- Plus pauses between sentences = 120-180s final video (target_seconds)
- Insights should flow as a podcast monologue: progressive depth, varied angles
- NO CTA, NO "subscribe/follow", NO book name in narration
- "source_book" is metadata for caption/description ONLY (never spoken)
- Each scene_prompt: 1 English sentence, cinematic vertical 9:16, contemplative mood
"""


async def _call_gemini(system_prompt: str, user_content: str) -> dict:
    """Call Gemini via key-rotation pool. Auto-failover on 429/quota."""
    from agent.services.gemini_key_pool import call_gemini_async

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_content}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    raw = await call_gemini_async(payload, model="gemini-2.5-flash", timeout=120)
    text = raw["candidates"][0]["content"]["parts"][0]["text"]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Gemini returned invalid JSON: {e}\nRaw: {text[:500]}")


async def extract_chapters(
    content: str,
    metadata: dict,
    max_chapters: int = 30,
) -> list[dict]:
    """List the main chapters / principles / themes of a book.

    Args:
        content: extracted book text or manual outline
        metadata: {"title": ..., "author": ...}
        max_chapters: cap for output

    Returns:
        list of dicts matching ChapterInfo schema
    """
    user_prompt = (
        f"Book: {metadata.get('title', 'Unknown')} by {metadata.get('author', 'Unknown')}\n"
        f"max_chapters: {max_chapters}\n\n"
        f"Book content:\n{content[:12000]}"
    )
    result = await _call_gemini(_CHAPTERS_SYSTEM, user_prompt)
    chapters = result.get("chapters", []) if isinstance(result, dict) else []
    logger.info("Extracted %d chapters from %s", len(chapters), metadata.get("title"))
    return chapters


async def write_summary_script(
    content: str,
    metadata: dict,
    target_minutes: int = 7,
    topic: str = None,
) -> dict:
    """Generate a summary script from book text or outline.

    Args:
        content: extracted book text or manual outline
        metadata: {"title": ..., "author": ...}
        target_minutes: target video duration (5-8)
        topic: optional focus topic/chapter (narrows extraction)

    Returns:
        dict matching SummaryScript schema
    """
    topic_line = f"FOCUS TOPIC: {topic}\nOnly extract content relevant to this topic. Ignore other parts of the book.\n\n" if topic else ""
    user_prompt = (
        f"Book: {metadata.get('title', 'Unknown')} by {metadata.get('author', 'Unknown')}\n"
        f"Target duration: {target_minutes} minutes\n\n"
        f"{topic_line}"
        f"Book content:\n{content[:12000]}"
    )

    result = await _call_gemini(_SUMMARY_SYSTEM, user_prompt)
    logger.info(
        "Summary script generated: %d sections (topic=%s)",
        len(result.get("sections", [])), topic or "none",
    )
    return result


async def write_chapter_podcast_script(
    content: str,
    metadata: dict,
    target_minutes: int = 12,
    chapter: str = None,
    comment_question: str = None,
    next_chapter_tease: str = None,
) -> dict:
    """Generate English 4-act chapter podcast script (10-15 min, international YouTube).

    Args:
        content: source chapter text or manual outline
        metadata: {"title": ..., "author": ...}
        target_minutes: target duration (10-15)
        chapter: chapter name or number to focus on (e.g. "Chapter 1" or "Letters 1-4")
        comment_question: explicit override; otherwise model generates
        next_chapter_tease: explicit override; otherwise model generates

    Returns:
        dict with hook + summary[] + analysis[] + outro schema
    """
    overrides = []
    if comment_question:
        overrides.append(f"Use this exact comment question in outro: {comment_question}")
    if next_chapter_tease:
        overrides.append(f"Tease next chapter as: {next_chapter_tease}")
    override_block = "\n".join(overrides) + "\n\n" if overrides else ""

    chapter_line = f"FOCUS CHAPTER: {chapter}\nExtract content ONLY from this chapter; ignore unrelated material.\n\n" if chapter else ""

    user_prompt = (
        f"Book: {metadata.get('title', 'Unknown')} by {metadata.get('author', 'Unknown')}\n"
        f"Target duration: {target_minutes} minutes\n\n"
        f"{chapter_line}"
        f"{override_block}"
        f"Source content:\n{content[:16000]}"
    )

    result = await _call_gemini(_CHAPTER_PODCAST_SYSTEM, user_prompt)
    logger.info(
        "Chapter podcast script generated: summary=%d analysis=%d (chapter=%s)",
        len(result.get("summary", [])), len(result.get("analysis", [])),
        chapter or "none",
    )
    return result


async def write_chapter_podcast_vi_script(
    content: str,
    metadata: dict,
    target_minutes: int = 12,
    chapter: str = None,
    comment_question: str = None,
    next_chapter_tease: str = None,
) -> dict:
    """Generate Vietnamese 3-act chapter podcast script (10-15 min, no analysis).

    Args:
        content: source chapter text or manual outline
        metadata: {"title": ..., "author": ...}
        target_minutes: target duration (10-15)
        chapter: chapter name or number
        comment_question: explicit override
        next_chapter_tease: explicit override

    Returns:
        dict with hook + summary[] + outro schema (3-act, no analysis)
    """
    overrides = []
    if comment_question:
        overrides.append(f"Use this exact comment question in outro: {comment_question}")
    if next_chapter_tease:
        overrides.append(f"Tease next chapter as: {next_chapter_tease}")
    override_block = "\n".join(overrides) + "\n\n" if overrides else ""

    chapter_line = f"FOCUS CHAPTER: {chapter}\nChỉ lấy nội dung từ chương này; bỏ qua phần khác.\n\n" if chapter else ""

    user_prompt = (
        f"Sách: {metadata.get('title', 'Unknown')} của {metadata.get('author', 'Unknown')}\n"
        f"Thời lượng target: {target_minutes} phút\n\n"
        f"{chapter_line}"
        f"{override_block}"
        f"Nội dung nguồn:\n{content[:16000]}"
    )

    result = await _call_gemini(_CHAPTER_PODCAST_VI_SYSTEM, user_prompt)
    logger.info(
        "VN chapter podcast script generated: summary=%d (chapter=%s)",
        len(result.get("summary", [])), chapter or "none",
    )
    return result


async def write_quote_script(
    content: str,
    metadata: dict,
    count: int = 3,
    target_seconds: int = 150,
    topic: str = None,
) -> list[dict]:
    """Generate quote scripts for podcast-style 2-3 min Shorts.

    Args:
        content: extracted book text or manual outline
        metadata: {"title": ..., "author": ...}
        count: number of quotes to extract
        target_seconds: target duration per video (120-180s, default 150)
        topic: optional focus topic/chapter (narrows extraction)

    Returns:
        list of dicts matching QuoteScript schema (with insights[] array)
    """
    topic_line = f"FOCUS TOPIC: {topic}\nOnly extract quotes/ideas relevant to this specific topic. Ignore other parts.\n\n" if topic else ""
    user_prompt = (
        f"Book: {metadata.get('title', 'Unknown')} by {metadata.get('author', 'Unknown')}\n"
        f"Extract exactly {count} powerful quotes/ideas.\n"
        f"Target duration per video: {target_seconds} seconds (~{target_seconds // 7} narrator sentences total).\n\n"
        f"{topic_line}"
        f"Book content:\n{content[:12000]}"
    )

    result = await _call_gemini(_QUOTE_SYSTEM, user_prompt)
    if not isinstance(result, list):
        raise RuntimeError(f"Expected JSON array for quote script, got: {type(result)}")

    logger.info("Quote script generated: %d quotes (topic=%s)", len(result), topic or "none")
    return result
