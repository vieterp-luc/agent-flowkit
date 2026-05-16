# Register in main.py: from agent.api.book import router as book_router; app.include_router(book_router, prefix="/api")
"""FastAPI router for book extraction and script generation."""
import logging

from fastapi import APIRouter, HTTPException

from agent.models.book import (
    ExtractScriptRequest, ExtractScriptResponse,
    ExtractChaptersRequest, ExtractChaptersResponse, ChapterInfo,
)
from agent.services.book_extractor import extract_book, chunk_text
from agent.services.book_script_writer import (
    write_summary_script, write_quote_script, write_chapter_podcast_script,
    write_chapter_podcast_vi_script, extract_chapters,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["book"])


def _validate_request(body: ExtractScriptRequest) -> None:
    if body.mode not in ("auto", "manual"):
        raise HTTPException(400, "mode must be 'auto' or 'manual'")
    if body.format not in ("summary", "quote", "chapter_podcast", "chapter_podcast_vi"):
        raise HTTPException(400, "format must be 'summary', 'quote', 'chapter_podcast', or 'chapter_podcast_vi'")
    if body.mode == "auto" and not body.source.file_path:
        raise HTTPException(400, "source.file_path required for auto mode")
    if body.mode == "manual" and not body.source.outline:
        raise HTTPException(400, "source.outline required for manual mode")


def _get_content(body: ExtractScriptRequest) -> str:
    if body.mode == "auto":
        try:
            raw = extract_book(body.source.file_path)
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            raise HTTPException(422, str(e))
        chunks = chunk_text(raw)
        # Use first chunk; for long books the summary prompt caps at 12k chars internally
        return chunks[0] if len(chunks) == 1 else "\n\n".join(chunks[:3])
    else:
        return body.source.outline


@router.post("/book/extract-script", response_model=ExtractScriptResponse)
async def extract_script(body: ExtractScriptRequest):
    """Extract book content and generate a structured script for video production."""
    _validate_request(body)

    content = _get_content(body)
    metadata = body.source.metadata.model_dump()

    try:
        if body.format == "summary":
            data = await write_summary_script(
                content=content,
                metadata=metadata,
                target_minutes=body.options.target_minutes,
                topic=body.options.topic,
            )
        elif body.format == "chapter_podcast":
            data = await write_chapter_podcast_script(
                content=content,
                metadata=metadata,
                target_minutes=body.options.target_minutes,
                chapter=body.options.chapter or body.options.topic,
                comment_question=body.options.comment_question,
                next_chapter_tease=body.options.next_chapter_tease,
            )
        elif body.format == "chapter_podcast_vi":
            data = await write_chapter_podcast_vi_script(
                content=content,
                metadata=metadata,
                target_minutes=body.options.target_minutes,
                chapter=body.options.chapter or body.options.topic,
                comment_question=body.options.comment_question,
                next_chapter_tease=body.options.next_chapter_tease,
            )
        else:
            data = await write_quote_script(
                content=content,
                metadata=metadata,
                count=body.options.count,
                target_seconds=body.options.target_seconds,
                topic=body.options.topic,
            )
    except RuntimeError as e:
        logger.error("book script writer failed: %s", e)
        raise HTTPException(502, str(e))

    return ExtractScriptResponse(ok=True, format=body.format, data={"script": data})


def _validate_chapters_request(body: ExtractChaptersRequest) -> None:
    if body.mode not in ("auto", "manual"):
        raise HTTPException(400, "mode must be 'auto' or 'manual'")
    if body.mode == "auto" and not body.source.file_path:
        raise HTTPException(400, "source.file_path required for auto mode")
    if body.mode == "manual" and not body.source.outline:
        raise HTTPException(400, "source.outline required for manual mode")


def _get_content_for_chapters(body: ExtractChaptersRequest) -> str:
    if body.mode == "auto":
        try:
            raw = extract_book(body.source.file_path)
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            raise HTTPException(422, str(e))
        chunks = chunk_text(raw)
        return chunks[0] if len(chunks) == 1 else "\n\n".join(chunks[:3])
    return body.source.outline


@router.post("/book/extract-chapters", response_model=ExtractChaptersResponse)
async def extract_chapters_endpoint(body: ExtractChaptersRequest):
    """List the main chapters / principles / themes of a book for series planning."""
    _validate_chapters_request(body)
    content = _get_content_for_chapters(body)
    metadata = body.source.metadata.model_dump()

    try:
        chapters_raw = await extract_chapters(
            content=content,
            metadata=metadata,
            max_chapters=body.max_chapters,
        )
    except RuntimeError as e:
        logger.error("extract chapters failed: %s", e)
        raise HTTPException(502, str(e))

    chapters = [ChapterInfo(**c) for c in chapters_raw]
    return ExtractChaptersResponse(ok=True, chapters=chapters)
