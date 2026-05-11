# fk-gen-caption — Tạo Caption + Hashtag cho MXH

Generate caption và hashtag cho Facebook Reels và TikTok từ thông tin project. Lưu vào `social_caption` — dashboard sẽ hiển thị tự động.

Usage: `/fk-gen-caption <project_id>`

---

## Bước 1: Fetch project data

```bash
curl -s http://127.0.0.1:8100/api/projects/<PROJECT_ID>
```

Ghi nhớ: `name`, `story`, `description`, `language`.

Fetch narrator texts từ scenes (nếu có):
```bash
# Get videos
curl -s "http://127.0.0.1:8100/api/projects/<PROJECT_ID>/videos" 2>/dev/null || \
curl -s "http://127.0.0.1:8100/api/videos?project_id=<PROJECT_ID>"

# Get scenes của video đầu tiên
curl -s "http://127.0.0.1:8100/api/scenes?video_id=<VIDEO_ID>"
```

Collect tất cả `narrator_text` khác null từ các scenes.

---

## Bước 2: Generate captions

Dựa vào context (name, story, description, narrator_texts), tự viết captions theo tiêu chí sau:

### Facebook Reels caption
- 2-3 câu tiếng Việt, gợi cảm xúc, kêu gọi xem video
- Không dùng hashtag trong caption
- Tone: ấm áp, chiều sâu, phù hợp content nghệ thuật/triết lý

### Facebook hashtags
- 6-8 hashtag tiếng Việt + quốc tế liên quan
- Format: `#tag1 #tag2 #tag3 ...`

### TikTok caption
- 1-2 câu ngắn, có thể dùng emoji
- Trendy, hook ngay từ đầu
- Không dùng hashtag trong caption

### TikTok hashtags
- 10-12 hashtag: mix viral (#fyp #xuhuong) + niche (#vetranh #sonhdau)
- Format: `#tag1 #tag2 #tag3 ...`

---

## Bước 3: Lưu vào database

```bash
curl -s -X POST http://127.0.0.1:8100/api/projects/<PROJECT_ID>/social-caption \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json, sys
data = {
  'fb_caption': '<FB_CAPTION>',
  'fb_hashtags': '<FB_HASHTAGS>',
  'tiktok_caption': '<TIKTOK_CAPTION>',
  'tiktok_hashtags': '<TIKTOK_HASHTAGS>'
}
print(json.dumps(data, ensure_ascii=False))
")"
```

**Verify lưu thành công:**
```bash
curl -s http://127.0.0.1:8100/api/projects/<PROJECT_ID>/social-caption
```

Phải trả về đúng 4 trường JSON.

---

## Bước 4: Báo cáo kết quả

Hiển thị caption đã lưu để user review:

```
✅ Caption đã lưu cho project: <name>

📘 Facebook
<fb_caption>
<fb_hashtags>

🎵 TikTok
<tiktok_caption>
<tiktok_hashtags>
```

Dashboard sẽ tự hiển thị khi reload project.
