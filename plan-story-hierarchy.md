# Plan: Hierarchical Story Management & Auto-Entity Extraction

## 1. Mục tiêu và Khả thi (Feasibility)
**Có thể triển khai được không?** -> HOÀN TOÀN CÓ THỂ.
Cấu trúc schema hiện tại của bạn đã hỗ trợ sẵn phần lớn yêu cầu này.
- Bảng `project` đã có cột `story`.
- Bảng `video` đã có cột `description` (có thể được xem như `story` của từng tập phim) và hoàn toàn phụ thuộc vào `project_id`.
- Bảng `character` lưu trữ assets, và được liên kết M:N với project qua bảng `project_character`.

## 2. Các bước triển khai (Implementation Steps)

### Bước 1: Điều chỉnh schema & API (Tùy chọn cho Video Story)
- **Kiểm tra Schema:** Bảng `video` hiện dùng cột `description` (TEXT). Bạn có thể tiếp tục sử dụng `description` làm nội dung story cho từng tập phim, HOẶC thêm một cột `story TEXT` vào bảng `video` trong `agent/db/schema.py` để tách biệt mô tả ngắn gọn và kịch bản chi tiết.
- *Khuyến nghị:* Giữ nguyên `description` và trên UI đổi tên label thành "Episode Story" để tránh phải migrate DB nếu không quá cần thiết.

### Bước 2: Bổ sung Pipeline "Phân tích & Trích xuất Asset" (Auto-Extraction)
Trước khi chạy hàm sinh ra các `scenes` (giống như logic trong `auto_generate_scenes` tại `agent/api/videos.py`), chúng ta cần chèn một bước kiểm tra và tự động thêm tài nguyên.
Logic cụ thể cho Agent:
1. **Đọc Context:** Lấy `project.story` và `video.description`.
2. **Fetch Existing Assets:** Truy vấn các entities (character, location, asset) đang có sẵn trong project.
3. **LLM Extraction:** Gửi prompt cho LLM để phân tích `video.description` và trả về danh sách các entities cần thiết cho tập phim này.
   - LLM đối chiếu với Existing Assets.
   - Nếu có nhân vật / bối cảnh mới chưa tồn tại, LLM trả về danh sách `missing_entities` (bao gồm name, entity_type, description, image_prompt).
4. **Auto-Create Assets:** Vòng lặp lưu các `missing_entities` vào database:
   - Insert vào bảng `character` (lưu ý: `entity_type` có thể là 'character', 'location', 'visual_asset', v.v).
   - Link với project thông qua bảng `project_character`.

### Bước 3: Cập nhật hàm tạo Scenes (Auto-Generate Scenes)
Sửa đổi logic của API `POST /{vid}/auto-generate-scenes` trong `agent/api/videos.py`:
- Sau khi "Bước 2" hoàn tất, fetch lại toàn bộ danh sách entities MỚI NHẤT của project.
- Truyền danh sách (bao gồm cả asset cũ và asset vừa được tự động thêm) vào prompt của LLM để chia cảnh (Scene Breakdown).
- Đảm bảo `character_names` sinh ra trong mỗi scene luôn khớp chuẩn 100% với danh sách đã có.

### Bước 4: Cập nhật Frontend UI (Dashboard)
- Trong trang chi tiết Project/Video, khi bấm nút "Auto-Generate Scenes", hệ thống sẽ tự động chạy pipeline gồm 2 phases:
  - Phase 1: Phân tích & thêm Entities còn thiếu (sẽ thấy danh sách Assets trên UI tự động cập nhật).
  - Phase 2: Sinh ra kịch bản Scenes dựa trên Assets đã hoàn thiện.
- Cập nhật text/label trên UI để người dùng rõ `project` là Story tổng (Series), còn `video` là Story con (Episode).

## 3. Kiến trúc luồng dữ liệu (Data Flow)

```text
User Input -> Video Episode Story
       |
       v
[Backend API] /videos/{vid}/auto-generate-scenes
       |
       +-- (1) Fetch Project Story + Video Story
       +-- (2) Fetch Current Assets
       +-- (3) LLM Request: Find Missing Assets?
       +-- (4) Save Missing Assets to DB (table: character, project_character)
       +-- (5) Fetch Updated Assets
       +-- (6) LLM Request: Break down to Scenes
       +-- (7) Save Scenes to DB
       |
       v
Return Success -> UI Refreshes Asset List & Scene List
```

## 4. Hành động tiếp theo
Nếu bạn đồng ý với Plan này, chúng ta sẽ bắt tay vào cập nhật code:
1. Viết prompt mới để extract missing characters.
2. Tích hợp prompt này vào `agent/api/videos.py`.
3. Test thử pipeline.
