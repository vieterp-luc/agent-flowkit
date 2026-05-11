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
