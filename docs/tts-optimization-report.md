# Báo cáo Tối ưu hóa Hệ thống TTS (Text-to-Speech)

Tài liệu này ghi lại các thay đổi quan trọng trong hệ thống TTS để cải thiện hiệu suất xử lý trên phần cứng Apple Silicon (M1 Pro).

## 1. Vấn đề ban đầu
*   **Cold Start:** Model OmniVoice (~2GB) bị nạp lại từ đầu cho mỗi câu thoại, gây trễ 30s/câu.
*   **CPU Bottleneck:** Cấu hình mặc định chạy trên CPU, tốn ~30s để render 1 câu thoại ngắn.
*   **Xử lý tuần tự:** Các yêu cầu TTS bị khóa (Lock) và xử lý từng cái một.

## 2. Các giải pháp đã triển khai

### A. Persistent Worker (Tiến trình duy trì)
Thay vì khởi chạy script Python mới cho mỗi yêu cầu, một tiến trình con (subprocess) được duy trì liên tục.
*   **Cơ chế:** Giao tiếp qua `stdin/stdout` bằng định dạng JSON.
*   **Kết quả:** Loại bỏ hoàn toàn 30s nạp model cho các yêu cầu từ thứ hai trở đi.

### B. Kích hoạt GPU (MPS Acceleration)
Chuyển đổi thiết bị xử lý từ `cpu` sang `mps` (Metal Performance Shaders).
*   **Cấu hình:** `TTS_DEVICE = "mps"` trong `agent/config.py`.
*   **Kỹ thuật:** Ép kiểu `torch.float32` để tránh lỗi nhiễu âm thanh (gibberish) trên kiến trúc ARM.
*   **Kết quả:** Tốc độ render nhanh gấp **4 lần** (từ ~22s xuống ~6s mỗi câu).

### C. Multi-Worker Pool (Hệ thống đa luồng)
Triển khai `TTSManager` để quản lý một nhóm các workers.
*   **Cấu hình:** Mặc định **2 workers** chạy song song (phù hợp với 16GB RAM).
*   **Cơ chế:** Sử dụng `asyncio.Queue` để phân phối công việc cho worker đang rảnh.
*   **Kết quả:** Cho phép xử lý đồng thời nhiều câu thoại, giảm thêm 20-40% tổng thời gian xử lý batch.

## 3. Kết quả đo lường thực tế (M1 Pro 16GB)
| Trạng thái | Thời gian/Câu thoại | Tổng thời gian (4 câu) |
| :--- | :--- | :--- |
| Trước tối ưu | ~60s | ~240s |
| **Sau tối ưu** | **~6s** | **~40s (lần đầu) / ~18s (lần sau)** |

**=> Tốc độ tổng thể tăng trưởng: ~7x đến 10x.**

## 4. Hướng dẫn cho Agents khác
*   **File quan trọng:** `agent/services/tts.py` (chứa logic Pool & Worker), `agent/config.py` (chứa cấu hình Device).
*   **Lưu ý bộ nhớ:** Mỗi worker OmniVoice chiếm ~1.5GB RAM. Không nên tăng số lượng worker quá cao trên máy 16GB.
*   **Môi trường:** Luôn sử dụng `TTS_PYTHON_BIN` trỏ đến venv có cài đặt `omnivoice` và `torch`.
