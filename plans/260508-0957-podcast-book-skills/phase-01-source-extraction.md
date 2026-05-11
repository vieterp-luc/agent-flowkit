# Phase 1: Source Extraction (PDF/EPUB → Outline → Script)

**Priority:** P0 (foundation cho 2 skill)
**Status:** ⏳ Pending
**Estimate:** 1-2 ngày

## Context Links

- Plan overview: [`plan.md`](plan.md)
- Related: existing `/fk-research` skill (fact-check pattern)
- Gemini API integration: `agent/api/gemini.py` (đã có)

## Mục tiêu

Tạo module `book_extractor` chuyển source → script JSON sẵn sàng cho video pipeline.

**2 input modes:**

| Mode | Input | Use case |
|------|-------|----------|
| **A. Auto** | File PDF/EPUB + book metadata | Có sách full text |
| **B. Manual** | `{title, author, outline, key_points}` | Chỉ có ý chính/research |

**2 output formats:**

| Format | Cho skill | Schema |
|--------|-----------|--------|
| `summary` | `/fk-video-book-summary` | `{hook, sections[], outro}` |
| `quote` | `/fk-video-book-quote` | `{quote, insight, cta, source_book}` |

## Architecture

```
[PDF/EPUB] → pypdf/ebooklib extract → text chunks
                                          ↓
[Manual outline] ────────────────→ Gemini summarize
                                          ↓
                                    Structured script
                                    (JSON validated)
```

## Related Code Files

### To create
- `agent/services/book_extractor.py` — extract PDF/EPUB → text
- `agent/services/book_script_writer.py` — text → structured script (Gemini)
- `agent/api/book.py` — REST endpoint `POST /api/book/extract-script`
- `agent/models/book.py` — Pydantic models (BookSource, ScriptOutput)

### To modify
- `agent/main.py` — register book router
- `requirements.txt` — add `pypdf`, `ebooklib`

## Implementation Steps

1. **Add deps to `requirements.txt`**
   ```
   pypdf>=4.0.0
   ebooklib>=0.18
   beautifulsoup4>=4.12.0
   ```

2. **Create `agent/services/book_extractor.py`**
   - `extract_pdf(path) -> str` — full text từ PDF
   - `extract_epub(path) -> str` — text từ EPUB chapters
   - `chunk_text(text, max_tokens=8000) -> list[str]` — chunk cho Gemini context

3. **Create `agent/services/book_script_writer.py`**
   - `write_summary_script(text|outline, target_minutes=7) -> dict`
     - Output: `{hook, sections: [{title, narrator, scene_prompts[]}], outro}`
   - `write_quote_script(text|outline, count=3) -> list[dict]`
     - Output: `[{quote, insight, cta, scene_prompts[]}]`
   - System prompt: tone podcast Vietnamese, 20-22 từ/câu narrator (rule từ memory)

4. **Create `agent/api/book.py`**
   ```
   POST /api/book/extract-script
   body: {
     mode: "auto" | "manual",
     format: "summary" | "quote",
     source: {file_path?: str, outline?: str, metadata: {title, author}},
     options: {target_minutes?: int, count?: int}
   }
   → returns structured script JSON
   ```

5. **Register router trong `agent/main.py`**

6. **Compile check:** `venv/bin/python -m py_compile agent/api/book.py agent/services/book_extractor.py agent/services/book_script_writer.py`

## Schema Output

### Summary script (long-form)
```json
{
  "book": {"title": "Đắc Nhân Tâm", "author": "Dale Carnegie"},
  "hook": {"narrator_text": "...", "scene_prompts": ["..."]},
  "sections": [
    {
      "title": "Nguyên tắc 1: ...",
      "narrator_text": "...",
      "scene_prompts": ["scene 1 prompt", "scene 2 prompt"]
    }
  ],
  "outro": {"narrator_text": "...", "scene_prompts": ["..."]},
  "estimated_duration_seconds": 420
}
```

### Quote script (Shorts)
```json
[
  {
    "quote": "Quote nguyên văn từ sách (Vietnamese)",
    "insight": "Lý giải insight 30-40 từ",
    "cta": "Sách [tên] - [tác giả]. Follow để đọc thêm",
    "scene_prompts": ["scene 1 prompt", "scene 2 prompt", "scene 3 prompt"],
    "source_book": {"title": "...", "author": "..."}
  }
]
```

## Todo List

- [ ] Add deps `pypdf`, `ebooklib`, `beautifulsoup4`
- [ ] Implement `book_extractor.py` (PDF + EPUB)
- [ ] Implement `book_script_writer.py` (Gemini calls với system prompts)
- [ ] Implement `agent/api/book.py` REST endpoint
- [ ] Register router in `main.py`
- [ ] Compile check pass
- [ ] Manual test: 1 PDF + 1 outline → verify JSON schema valid
- [ ] Manual test: 1 quote extraction → verify 20-22 từ/câu

## Success Criteria

- ✅ Endpoint `POST /api/book/extract-script` returns valid JSON cho cả 2 format
- ✅ PDF/EPUB extract trung thực với source (không hallucination)
- ✅ Narrator text 20-22 từ/câu (Vietnamese)
- ✅ Scene prompts in English (cho Imagen)

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| PDF có scan ảnh không có text layer | Báo lỗi rõ + suggest user dùng OCR trước |
| Gemini hallucinate khi chunk dài | Chunk nhỏ + cite source page numbers |
| Vi phạm bản quyền sách | Disclaimer: tóm tắt fair use + ghi rõ source |

## Next Steps

→ Phase 2: Ken Burns helper (parallel có thể chạy)
→ Phase 3: `/fk-video-book-summary` skill (depends Phase 1 + 2)
