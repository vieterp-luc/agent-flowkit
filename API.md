# MZ FlowKit API Documentation
**Base URL**: `http://127.0.0.1:8100`
**Version**: 0.2.0

---

## 1. System & Extensions

- **`GET /health`**
  - **Mô tả:** Kiểm tra trạng thái server và kết nối của extension. Trả về `{"extension_connected": true/false}`.
- **`POST /api/ext/callback`**
  - **Mô tả:** Webhook nội bộ để Chrome extension gửi kết quả API về agent. Dùng header `X-Callback-Secret`.
- **`GET /api/skills`**
  - **Mô tả:** Danh sách các command `/fk-*` (skills) hiện có trong hệ thống.

---

## 2. Projects & Active Project

- **`POST /api/projects`**
  - **Mô tả:** Tạo project mới. Yêu cầu `name`. Nhận các tham số mở rộng: `description`, `material`, `characters`, v.v.
- **`GET /api/projects`**
  - **Mô tả:** Lấy danh sách tất cả projects. Hỗ trợ query filter `status`.
- **`GET /api/projects/{pid}`**
  - **Mô tả:** Lấy chi tiết project theo ID.
- **`PATCH /api/projects/{pid}`**
  - **Mô tả:** Cập nhật thông tin project (hỗ trợ update từng phần).
- **`DELETE /api/projects/{pid}`**
  - **Mô tả:** Xóa project.
- **`GET /api/projects/{pid}/output-dir`**
  - **Mô tả:** Trả về thư mục lưu trữ output của project (tự động tạo nếu chưa có cùng `meta.json`).
- **`POST /api/projects/{pid}/generate-thumbnail`**
  - **Mô tả:** Tạo ảnh thumbnail đại diện cho project thông qua Google Flow (chạy đồng bộ).
- **`GET /api/active-project`**
  - **Mô tả:** Lấy project đang làm việc (active). Nếu chưa set, tự động fallback về project tạo gần nhất.
- **`PUT /api/active-project`**
  - **Mô tả:** Gắn cờ active cho một project cụ thể (`{ "project_id": "..." }`).
- **`DELETE /api/active-project`**
  - **Mô tả:** Xóa cờ active project hiện hành.

---

## 3. Characters & Entities

- **`POST /api/characters`**
  - **Mô tả:** Tạo character/thực thể mới.
- **`GET /api/characters`**
  - **Mô tả:** Lấy danh sách toàn bộ characters lưu trong DB.
- **`GET /api/characters/{cid}`**
  - **Mô tả:** Lấy chi tiết một character.
- **`PATCH /api/characters/{cid}`**
  - **Mô tả:** Cập nhật chi tiết character.
- **`DELETE /api/characters/{cid}`**
  - **Mô tả:** Xóa character.
- **`GET /api/projects/{pid}/characters`**
  - **Mô tả:** Lấy danh sách các character đang được liên kết với một project cụ thể.
- **`POST /api/projects/{pid}/characters/{cid}`**
  - **Mô tả:** Map/Liên kết một character vào một project.
- **`DELETE /api/projects/{pid}/characters/{cid}`**
  - **Mô tả:** Hủy liên kết character khỏi project.

---

## 4. Videos & Scenes

- **`POST /api/videos`**
  - **Mô tả:** Khởi tạo một video sequence mới cho project.
- **`GET /api/videos`**
  - **Mô tả:** Lấy danh sách video (bắt buộc truyền query `project_id`).
- **`GET /api/videos/{vid}`**
  - **Mô tả:** Lấy chi tiết video.
- **`PATCH /api/videos/{vid}`**
  - **Mô tả:** Cập nhật thông tin cấu hình, status hoặc URL của video.
- **`DELETE /api/videos/{vid}`**
  - **Mô tả:** Xóa một video sequence.
- **`POST /api/scenes`**
  - **Mô tả:** Tạo scene con thuộc về video. Gửi các thông tin về `prompt`, `video_id`, `chain_type`.
- **`GET /api/scenes`**
  - **Mô tả:** Lấy danh sách scenes thuộc video (truyền query `video_id`).
- **`DELETE /api/scenes`**
  - **Mô tả:** Xóa sỉ (bulk delete) toàn bộ scenes theo `video_id` và `source`, tự động re-compact lại `display_order`.
- **`GET /api/scenes/{sid}`**
  - **Mô tả:** Lấy chi tiết scene.
- **`PATCH /api/scenes/{sid}`**
  - **Mô tả:** Cập nhật scene (status, image/video URLs, media IDs, prompt).
- **`DELETE /api/scenes/{sid}`**
  - **Mô tả:** Xóa một scene chỉ định.

---

## 5. Async Requests & Batching (Quản lý Hàng Đợi Queue)

- **`POST /api/requests`**
  - **Mô tả:** Tạo một request đơn lẻ đưa vào hàng đợi xử lý ảnh/video.
- **`GET /api/requests`**
  - **Mô tả:** Lấy danh sách requests.
- **`POST /api/requests/batch`**
  - **Mô tả:** Gửi một batch nhiều requests cùng lúc. Backend sẽ tự động xử lý throttle (giới hạn 5 concurrent). Tự động skip nếu request trùng lặp.
- **`GET /api/requests/batch-status`**
  - **Mô tả:** API tối ưu dùng để polling. Trả về thống kê tổng hợp: `{ total, pending, processing, completed, failed, done, all_succeeded }`
- **`GET /api/requests/pending`**
  - **Mô tả:** Lấy danh sách tất cả request đang chờ xử lý (`PENDING`).
- **`GET /api/requests/{rid}`** / **`PATCH /api/requests/{rid}`**
  - **Mô tả:** Đọc và cập nhật trạng thái chi tiết của request.

---

## 6. Flow Proxy (Google Flow & Veo 3)

*Lưu ý: Các APIs này proxy qua Chrome Extension đang kết nối để dùng credentials của trình duyệt.*

- **`GET /api/flow/status`**
  - **Mô tả:** Trạng thái kết nối Google Flow.
- **`GET /api/flow/credits`**
  - **Mô tả:** Kiểm tra tín dụng/quota của Google Flow.
- **`POST /api/flow/generate-image`**
  - **Mô tả:** Gửi lệnh generate ảnh.
- **`POST /api/flow/edit-image`**
  - **Mô tả:** Chỉnh sửa ảnh từ một ảnh gốc có sẵn (`source_media_id`).
- **`POST /api/flow/upload-image`**
  - **Mô tả:** Upload ảnh local lên Google Flow để lấy `media_id`.
- **`POST /api/flow/generate-video`** / **`POST /api/flow/generate-video-refs`**
  - **Mô tả:** Gọi Veo 3 gen video từ ảnh (i2v) hoặc có reference.
- **`POST /api/flow/upscale-video`**
  - **Mô tả:** Chạy upscale chất lượng cho video.
- **`POST /api/flow/check-status`**
  - **Mô tả:** Kiểm tra trạng thái của các task gen video trên Flow.
- **`GET /api/flow/media/{media_id}`**
  - **Mô tả:** Lấy metadata và signed URL tươi (chưa expire) từ GCS.
- **`POST /api/flow/refresh-urls/{project_id}`**
  - **Mô tả:** Bulk refresh URL chống hết hạn cho tất cả asset của project.

---

## 7. AI Reviews (Claude Vision)

- **`POST /api/videos/{vid}/review`**
  - **Mô tả:** Chạy quy trình review toàn bộ video clip trong video sequence bằng Claude Vision (chấm điểm chất lượng theo fps).
- **`POST /api/videos/{vid}/scenes/{sid}/review`**
  - **Mô tả:** Tương tự nhưng review cho duy nhất một scene.

---

## 8. TTS & Audio Narration

- **`POST /api/tts/generate`**
  - **Mô tả:** Tạo audio từ đoạn text. Trả về đường dẫn `.wav`.
- **`POST /api/videos/{vid}/narrate`**
  - **Mô tả:** Tự động tạo audio cho tất cả các text narration của scenes trong video và có tùy chọn mix thẳng vào video mp4.
- **`GET /api/tts/templates`** / **`POST /api/tts/templates`**
  - **Mô tả:** Lấy danh sách và khởi tạo Voice Template (để giữ được giọng điệu TTS ổn định xuyên suốt).
- **`GET /api/tts/templates/{name}`** / **`DELETE /api/tts/templates/{name}`**
  - **Mô tả:** Chi tiết và xóa Voice Template.

---

## 9. Music (Suno AI Integration)

- **`GET /api/music/templates`** / **`GET /api/music/templates/{id}`**
  - **Mô tả:** Lấy list hoặc lấy chi tiết template nhạc.
- **`POST /api/music/generate`**
  - **Mô tả:** Gọi tạo nhạc (có thể qua lyrics + style mode hoặc mô tả tự nhiên).
- **`GET /api/music/tasks/{task_id}`**
  - **Mô tả:** Check chi tiết tiến trình bài nhạc.
- **`POST /api/music/tasks/{task_id}/poll`**
  - **Mô tả:** Long-polling chờ bài nhạc gen xong.
- **`POST /api/music/tasks/{task_id}/download`**
  - **Mô tả:** Tải nhạc về thư mục output của project.
- **`POST /api/music/generate-lyrics`**
  - **Mô tả:** AI tự sáng tác lời bài hát.
- **`POST /api/music/extend`**
  - **Mô tả:** Nối thêm thời lượng cho bài hát đang có.
- **`POST /api/music/vocal-removal`**
  - **Mô tả:** Tách lời và beat nhạc.
- **`POST /api/music/convert-to-wav`**
  - **Mô tả:** Convert file sang WAV.
- **`GET /api/music/credits`**
  - **Mô tả:** Kiểm tra quota của Suno.

---

## 10. Materials & Models

- **`GET /api/materials`**
  - **Mô tả:** Lấy các loại Material (kiểu vẽ/phong cách - vd: `3d_pixar`, `realistic`).
- **`POST /api/materials`**
  - **Mô tả:** Tạo style material custom của user.
- **`GET /api/materials/{material_id}`** / **`DELETE /api/materials/{material_id}`**
  - **Mô tả:** Get detail / Xóa custom material.
- **`GET /api/models`**
  - **Mô tả:** Lấy cấu hình models hiện tại của hệ thống.
- **`PATCH /api/models`**
  - **Mô tả:** Cập nhật file cấu hình model (sử dụng logic deep-merge object).
- **`GET /api/models/chat`**
  - **Mô tả:** Lấy danh sách các text AI model từ 9Router.

---

## 11. Chat Gateway

- **`POST /api/chat`**
  - **Mô tả:** Proxy stream chuyển các request từ giao diện Chatbox của UI sang 9Router API (hoặc OpenAI/Anthropic tùy cấu hình). Hỗ trợ trả về chuẩn Server-Sent Events (SSE).
