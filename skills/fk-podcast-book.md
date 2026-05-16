# fk-podcast-book — Podcast Shorts từ sách (TikTok/Reels/YT Shorts)

Tạo series podcast Shorts (~60-90s/tập) từ một cuốn sách: 7 scenes Ken Burns + narrator tiếng Việt + nhạc nền + caption. Output theo trình tự tự động cho cả serie.

Usage: `/fk-podcast-book "<tên sách>" "<tác giả>" [--format chapter|theme] [--episodes N] [--voice phap_van|hong_hanh|podcast_male]`

**Default voice: `phap_van`** (nam, trầm — hợp văn học bi tráng, triết lý). Chỉ hỏi voice khi user explicit yêu cầu đổi.

Examples:
- `/fk-podcast-book "Đắc Nhân Tâm" "Dale Carnegie"` — interactive hỏi format/episodes, voice=phap_van mặc định
- `/fk-podcast-book "Nhà giả kim" "Paulo Coelho" --format chapter --episodes 14`
- `/fk-podcast-book "Đời thừa" "Nam Cao" --format theme --episodes 7 --voice hong_hanh`

---

## Khi nào dùng

- User yêu cầu "tạo podcast sách X" hoặc "làm series podcast từ X"
- Cần series 5-20 tập, mỗi tập ~60-90s Shorts
- Đã có sẵn `scripts/render_podcast_episode.py` + `podcast_render_lib.py`

---

## Pre-flight

```bash
curl -s http://127.0.0.1:8100/health
# Must return: {"extension_connected": true}
```

Nếu fail → `/fk-doctor` trước khi tiếp tục.

---

## Step 1 — Hỏi user (nếu thiếu args)

Dùng `AskUserQuestion` hỏi tối đa 2 câu:

1. **Format**: `chapter` (kể theo cảnh/chương — audiobook-style) hoặc `theme` (rút bài học theo chủ đề — gọn, triết lý)
2. **Số tập**: gợi ý 5/7/10/14 tuỳ format

**KHÔNG hỏi voice** — default `phap_van` (nam, trầm — hợp đa số podcast văn học + triết lý). Chỉ override khi user tự pass `--voice` hoặc nói rõ muốn voice khác (`hong_hanh` nữ ấm cho self-help, `podcast_male` nam podcaster).

Nếu user đã cho qua args, skip câu đã có.

---

## Step 2 — Sinh calendar.json

Path: `output/podcast-book/<slug>/calendar.json` (slug = kebab-case của tên sách, bỏ dấu, dùng `_` thay `-`, vd `nha_gia_kim`, `doi_thua`).

Schema:

```json
{
  "book": {
    "title": "<Tên sách>",
    "author": "<Tác giả>",
    "outline": "<2-4 câu mô tả sách + định hướng N tập>"
  },
  "extracted_at": "<ISO 8601 now>",
  "total_episodes": N,
  "completed": 0,
  "episodes": [
    {
      "id": 1,
      "title": "<Tiêu đề tập — Title Case Vietnamese>",
      "key_idea": "<1 câu cốt lõi>",
      "summary": "<2-4 câu mô tả tập>",
      "status": "pending"
    }
  ]
}
```

**Quan trọng:**
- `book.outline` LÀ BẮT BUỘC — `extract_topic_script` sẽ dùng nó (đã patch để không hardcode "Đắc Nhân Tâm")
- Tiêu đề tập ngắn gọn, gợi cảm xúc — sẽ là Line 1 của caption
- `summary` định hướng Gemini sinh script chuẩn — viết kỹ
- Đếm `id` từ 1, không skip

**Format chapter:** mỗi tập = 1 cảnh/chương theo trình tự truyện (audiobook). 
**Format theme:** mỗi tập = 1 chủ đề/bài học rút từ sách (không theo trình tự).

---

## Step 3 — Render EP01 để duyệt

```bash
./venv/bin/python scripts/render_podcast_episode.py <slug> 1 --voice <voice> --skip-music-gen
```

**Luôn dùng `--skip-music-gen`** — Suno music gen hiện không ổn định (MUSIC_TIMEOUT 360s). Pipeline reuse track từ `output/_shared/gemini_music/`.

**Logo overlay luôn bật:** Script luôn overlay logo kênh `sach-thi-tham` 150×150 góc trên trái ở step 9. Output cuối **chỉ một file `final.mp4`** đã có logo. KHÔNG concat intro/outro. File trung gian `_main.mp4` (chưa có logo) được giữ trong cùng dir.

CLI flags:
- `--brand <channel>` — đổi kênh (default `sach-thi-tham`)
- `--logo-size 130` — đổi size logo (default 150)
- `--logo-pos top-right|bottom-left|bottom-right` — đổi vị trí (default top-left)

Pipeline 9 bước (idempotent — re-run sẽ skip bước đã xong):
1. Extract script (Gemini, ~30s, dùng `book.outline` + `book.character_context` + `ep.key_idea`)
2. Gen 7 ảnh qua Flow extension (~2 phút, dùng `book.image_style` nếu có)
3. Apply Ken Burns motion (local ffmpeg, ~15s)
4. Concat + xfade (~10s)
5. Gen TTS (~4-5 phút)
6. Music (skipped → pick từ `_shared/gemini_music/`)
7. Audio mix → `_main.mp4` (intermediate, ~2s)
8. Gen caption (Gemini, ~5s)
9. **Logo overlay → `final.mp4` (~5-10s)**

Tổng EP01: ~7-9 phút. Run nền + Monitor.

**Channel assets BẮT BUỘC ở `youtube/channels/<channel>/`:**
- `<channel>_icon.png` — Logo (square, transparent background) — **bắt buộc, abort nếu thiếu**

**Calendar fields hỗ trợ tùy chọn:**
- `book.image_style` — Prefix cho image_prompt (vd cartoon, watercolor). Ảnh hưởng visual style mọi scene
- `book.character_context` — Inject vào Gemini extract prompt. Ép buộc nhân vật/setting (vd "all characters are insects, no humans")

Sau khi xong, hiển thị cho user verify chất lượng EP01.

---

## Step 4 — Render EP02..N sau khi user duyệt

Sequential trong 1 background command:

```bash
for ep in 2 3 4 ... N; do
  echo "===== Rendering EP $ep ====="
  ./venv/bin/python scripts/render_podcast_episode.py <slug> $ep --voice <voice> --skip-music-gen 2>&1 | tail -12
  echo ""
done
echo "===== ALL DONE ====="
```

Monitor stream với grep `Rendering EP|✓ DONE|Traceback|RuntimeError|FAILED`.

---

## Step 5 — Retry tập fail

Khi gặp `RuntimeError: Scene N has no image URL after polling` (Flow extension reconnect):

1. Identify EP fail (status `rendering` trong calendar — không phải `done`)
2. **Dọn artifact** (giữ `script.json`, xoá tất cả khác để Flow project mới):
   ```bash
   rm -rf output/podcast-book/<slug>/ep_<NN>_<slug>/{scene_ids.json,images,clips,concat_scenes.mp4,tts,music,final.mp4,caption.txt}
   ```
3. **Reset status** trong `calendar.json`: `rendering` → `pending`
4. Re-run render command cho EP đó

---

## Format caption (deterministic)

`gen_caption` (đã patch trong `podcast_render_lib.py`) hardcode Line 1, Gemini chỉ sinh hook + hashtags:

```
{book.title} - (EP{ep.id}) {ep.title}.
{hook 1-2 câu} {emoji?}

#{book_slug} #sachhay #podcast #tinhhoasach #<topic-tags> #<en-tags>
```

KHÔNG mention tên sách/tác giả trong hook (Gemini đã có instruction).

---

## Lưu ý

- **YAGNI**: KHÔNG sinh music mới — luôn `--skip-music-gen` (reuse pool)
- **Memory**: User prefer narrator 20-22 từ/câu Vietnamese (đã set trong `book.outline` instruction)
- **No text overlay**: Pure visual + voice (đã set trong pipeline)
- **Slug rule**: Vietnamese diacritics → lowercase ASCII + `_` (vd `Đời Thừa` → `doi_thua`)
- Nếu user reject EP01 → hỏi điều chỉnh (đổi voice, đổi outline, đổi key_idea), KHÔNG render bừa tập 2-N
- Render đồng thời max 1 (extension không chịu nổi parallel — đã thấy 3 fail liên tiếp khi reconnect)

---

## Failure recipes

| Lỗi | Giải pháp |
|-----|-----------|
| `MUSIC_TIMEOUT 360s` | Dùng `--skip-music-gen` (luôn dùng từ đầu) |
| `Scene N has no image URL` | Dọn artifact + reset status → retry (xem Step 5) |
| `extension_connected: false` | `/fk-doctor` — reload Chrome extension |
| Calendar `book.title` hardcode "Đắc Nhân Tâm" | Đã fix (`extract_topic_script` dùng `book.get('outline')`) |
| Caption thiếu Line 1 tiêu đề | Đã fix (`gen_caption` hardcode prepend) |
| **Image bị xoay 90° (landscape thay vì portrait)** | Flow đôi khi gen sai orientation. PATCH scene image_prompt thêm `"VERTICAL PORTRAIT 9:16 COMPOSITION ONLY — sky on top, water on bottom, palm trees growing UPWARD from ground, NO landscape orientation, NO rotated composition"`, reset `vertical_image_status=PENDING` + clear url, resubmit GENERATE_IMAGE, download, xoá `clips/scene_N.mp4` + `concat_scenes.mp4` + `_main.mp4` + `final.mp4` + `caption.txt`, reset EP status `pending`, re-run render. |
| **Image có text/chữ không mong muốn** | Tương tự: PATCH prompt thêm `"STRICTLY NO TEXT, NO LETTERS, NO WORDS, NO LABELS, NO TITLES visible anywhere"`, regen, re-render. Tốt hơn: thêm vào `book.image_style` từ đầu để áp cho mọi scene. |
| **Video chỉ dùng N scene nhưng images có nhiều hơn** | Default `--scene-count 5` từ 2026-05-15. Trước đó default 7 nhưng TTS ~60s chỉ phát ~5 scene → 2 scene cuối bị trim. Nếu thấy bug này, giảm `--scene-count` hoặc tăng `--target-seconds`. |

---

## Output structure

```
output/podcast-book/<slug>/
├── calendar.json                       # Tracking 1 series
└── ep_NN_<slug-title>/
    ├── script.json                     # Gemini-extracted insights
    ├── scene_ids.json                  # Flow project metadata
    ├── images/scene_N.jpg              # 5 ảnh AI (default scene_count=5)
    ├── clips/scene_N.mp4               # Ken Burns motion clips
    ├── concat_scenes.mp4               # Concat + xfade
    ├── tts/narrator.wav                # TTS Vietnamese
    ├── music/                          # Reused MP3
    ├── final.mp4                       # ⭐ Output cuối
    └── caption.txt                     # TikTok/Reels caption
```

Final video: ~15-25 MB, vertical 9:16 ~60-90s.
