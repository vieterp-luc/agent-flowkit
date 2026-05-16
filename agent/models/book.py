"""Pydantic models for book extraction and script generation."""
from typing import Optional
from pydantic import BaseModel


# ─── Input Models ────────────────────────────────────────────

class BookMetadata(BaseModel):
    title: str
    author: str


class BookSource(BaseModel):
    file_path: Optional[str] = None
    outline: Optional[str] = None
    metadata: BookMetadata


class ScriptOptions(BaseModel):
    target_minutes: int = 7
    count: int = 3
    target_seconds: int = 150  # for quote format: 120-180s podcast-style
    topic: Optional[str] = None  # focus extraction on this chapter/topic
    # chapter_podcast extras
    chapter: Optional[str] = None  # chapter name or number (e.g. "Letters 1-4" or "3")
    language: str = "vi"  # "vi" (default for summary/quote) | "en" (chapter_podcast)
    comment_question: Optional[str] = None  # explicit override for outro engagement question
    next_chapter_tease: Optional[str] = None  # explicit override for outro tease line


class ExtractScriptRequest(BaseModel):
    mode: str  # "auto" | "manual"
    format: str  # "summary" | "quote" | "chapter_podcast"
    source: BookSource
    options: ScriptOptions = ScriptOptions()


# ─── Output Models (Summary) ─────────────────────────────────

class ScriptSection(BaseModel):
    narrator_text: str
    scene_prompts: list[str]


class SummarySection(BaseModel):
    title: str
    narrator_text: str
    scene_prompts: list[str]


class SummaryScript(BaseModel):
    book: BookMetadata
    hook: ScriptSection
    sections: list[SummarySection]
    outro: ScriptSection
    estimated_duration_seconds: int


# ─── Output Models (Quote) ────────────────────────────────────

class QuoteInsight(BaseModel):
    narrator_text: str
    scene_prompt: str


class QuoteScript(BaseModel):
    quote: str
    insights: list[QuoteInsight]  # 8-12 sentences for 2-3 min podcast
    outro: str  # closing thought, NO book/author mention
    source_book: BookMetadata  # metadata only — never spoken in narrator


# ─── Output Models (Chapters) ────────────────────────────────

class ChapterInfo(BaseModel):
    id: int  # 1-based index
    title: str  # short chapter title (Vietnamese)
    key_idea: str  # 1-sentence core idea (Vietnamese, 20-30 words)
    summary: str  # 30-60 word summary for context (Vietnamese)


class ExtractChaptersRequest(BaseModel):
    mode: str  # "auto" | "manual"
    source: BookSource
    max_chapters: int = 30  # cap to avoid overrun for huge books


class ExtractChaptersResponse(BaseModel):
    ok: bool
    chapters: list[ChapterInfo] = []
    error: Optional[str] = None


# ─── Response ────────────────────────────────────────────────

class ExtractScriptResponse(BaseModel):
    ok: bool
    format: str
    data: Optional[dict] = None
    error: Optional[str] = None
