# Kế hoạch Tuần 3 + 4 — Series "Nếu... thì sao" (Meta AI video)

Tiếp nối Tuần 1-2. **Spec/pipeline/giọng y hệt**: 9:16, 7 scene × ~5s, Phong_Vien_TTS 0.9 +
nghỉ 0.4s, capture `/prompt`, output `output/whatif/<slug>/`, tự gắn logo. Công thức leo
thang theo mốc thời gian. 14 chủ đề mới (không trùng tuần 1-2).

Khi sản xuất: viết full script vào `scripts/whatif_days_week3.py` / `_week4.py` (keys
`day15`–`day28`), `whatif_produce.py` tự gộp (như week2) → chạy `whatif_produce.py day15 …`.

---

## TUẦN 3 (day15–day21)

| Ngày | Chủ đề | slug | Lõi khoa học | Beats (hook → leo thang → kết) |
|------|--------|------|--------------|--------------------------------|
| 15 | Siêu bão Mặt Trời (Carrington) đánh Trái Đất? | `neu_bao_mat_troi` | bão địa từ đốt lưới điện/vệ tinh | Mặt Trời phun lửa → cực quang tràn trời → vệ tinh & lưới điện cháy → mất điện toàn cầu → nước/y tế sụp → về thời tiền điện → 1 cơn bão vô hình đẩy ta lùi 100 năm |
| 16 | Sao Mộc biến mất? | `neu_sao_moc_bien_mat` | mất "lá chắn hấp dẫn" hút thiên thạch | Sao Mộc biến mất → mất lá chắn → mưa tiểu hành tinh vào trong → quỹ đạo nhiễu loạn → nguy cơ va chạm tăng vọt → bầu trời đầy sao băng đe doạ → kẻ khổng lồ thầm lặng bảo vệ ta 4 tỉ năm |
| 17 | Trái Đất to gấp đôi? | `neu_trai_dat_to_gap_doi` | khối lượng↑ → trọng lực↑ | phình gấp đôi → trọng lực gấp đôi, mọi thứ nặng trĩu → người không đứng nổi → công trình sụp → khí quyển dày, trời đổi màu → chim không bay nổi → kích thước quyết định số phận sự sống |
| 18 | Siêu núi lửa Yellowstone thức giấc? | `neu_sieu_nui_lua_yellowstone` | supervolcano → mùa đông núi lửa | Yellowstone thức giấc → phun trào lớn nhất lịch sử → tro phủ kín Bắc Mỹ → mây tro che Mặt Trời → mùa màng chết → nạn đói toàn cầu → quả bom hẹn giờ ngủ dưới chân ta |
| 19 | Trái Đất có hai Mặt Trời? | `neu_hai_mat_troi` | hệ sao đôi → khí hậu cực đoan | 2 Mặt Trời → không còn ban đêm → nhiệt độ tăng vọt → quỹ đạo bất ổn → đại dương bốc hơi, bão dữ → sống chỉ ở vùng chạng vạng → bóng tối hoá ra cũng quý giá |
| 20 | Toàn bộ băng trên Trái Đất tan hết? | `neu_bang_tan_het` | mực nước +70m, đảo lộn hải lưu | băng tan → biển dâng 70m → thành phố ven biển chìm → hải lưu đảo, khí hậu điên loạn → đất mới lộ ở hai cực → di cư hàng tỉ người → băng giữ bản đồ thế giới đứng yên |
| 21 | Tiểu hành tinh khổng lồ đâm Trái Đất? | `neu_tieu_hanh_tinh_dam` | impact winter (như khủng long) | thiên thạch lao tới → hố khổng lồ + sóng xung kích → sóng thần + cháy toàn cầu → bụi che Mặt Trời, mùa đông va chạm → chuỗi thức ăn sụp → số ít sống dưới lòng đất → thứ xoá sổ khủng long vẫn rình rập |

## TUẦN 4 (day22–day28)

| Ngày | Chủ đề | slug | Lõi khoa học | Beats |
|------|--------|------|--------------|-------|
| 22 | Trái Đất quay ngược? | `neu_trai_dat_quay_nguoc` | đảo gió & hải lưu → khí hậu vẽ lại | quay ngược → Mặt Trời mọc hướng tây → gió/hải lưu đảo chiều → sa mạc hoá xanh, vùng xanh hoá sa mạc → khí hậu toàn cầu vẽ lại → hệ sinh thái thích nghi hoặc chết → chiều quay định hình cả thế giới |
| 23 | Mặt Trời mờ đi một nửa? | `neu_mat_troi_mo_di` | giảm bức xạ → kỷ băng hà | Mặt Trời mờ 50% → ngày như hoàng hôn → nhiệt độ lao dốc → quang hợp giảm, cây chết → băng lan, kỷ băng hà mới → người co cụm quanh nguồn nhiệt → ta phụ thuộc từng tia nắng |
| 24 | Một ngày dài 48 giờ? | `neu_ngay_dai_48h` | chu kỳ quay chậm → biên nhiệt cực đoan | ngày 48h → 24h nắng thiêu → 24h đêm lạnh cóng → biên nhiệt cực đoan → sinh vật vật lộn chu kỳ mới → người sống theo nhịp lạ → nhịp quay nhỏ bé giữ cân bằng |
| 25 | Bầu khí quyển dày gấp đôi? | `neu_khi_quyen_day_gap_doi` | áp suất↑, truyền âm/sáng đổi | khí quyển dày gấp đôi → áp suất nghiền, trời đổi màu → âm thanh & ánh sáng truyền khác → bão mạnh hơn nhiều → sinh vật khó thở → thế giới dưới bầu trời nặng nề → lớp khí mỏng manh là vừa đủ |
| 26 | Toàn bộ nước ngọt biến mất? | `neu_nuoc_ngot_bien_mat` | 3% nước ngọt giữ văn minh | nước ngọt biến mất → sông hồ cạn → cây trồng & gia súc chết → tranh giành từng giọt → thành phố thành hoang mạc → di cư tuyệt vọng → 3% nước ngọt giữ cả văn minh |
| 27 | Trái Đất bị khoá thuỷ triều với Mặt Trời? | `neu_trai_dat_khoa_thuy_trieu` | một mặt vĩnh viễn ngày/đêm | khoá thuỷ triều → một mặt cháy nắng vĩnh viễn → mặt kia băng giá vĩnh cửu → bão dữ ở ranh giới → sống chỉ ở vành chạng vạng → người trú dải hẹp → ngày-đêm luân phiên là món quà |
| 28 | Từ trường Trái Đất đảo cực? | `neu_tu_truong_dao_cuc` | đảo cực địa từ (có thật trong lịch sử) | từ trường đảo cực → la bàn chỉ ngược, chim lạc → từ trường yếu đi → bức xạ lọt nhiều hơn → lưới điện & vệ tinh trục trặc → cực quang ở xích đạo → điều đã xảy ra nhiều lần trong lịch sử Trái Đất |

---

## Lịch đăng (nối tiếp tuần 1-2)
1 video/ngày 18:30 ICT. Tuần 1-2 phủ 04/06→17/06 → **Tuần 3: 18/06→24/06**, **Tuần 4: 25/06→01/07**.
Batch upload dùng `youtube/whatif_batch_upload.py` (mở rộng ORDER + `--start`).

## Lưu ý (đúc kết tuần 1-2)
- Gen ảnh giãn cách tránh reCAPTCHA; motion prompt phải **animate được từ ảnh** (camera+khí quyển), tránh `META_CHAT_ERROR`.
- Meta gen đôi khi fail 1 lần → retry; capture nhầm/ảnh xoay → harvest/`/prompt`/regen.
- Mỗi video tự gắn logo (`add_logo`), caption (`whatif_captions.py`), gói zip (`whatif_zip_bundle.py`).

## Câu hỏi mở
- Có muốn xen kẽ **body-horror/sinh học** (như "không bao giờ ngủ", "côn trùng") để đổi nhịp giữa toàn chủ đề vũ trụ/địa cầu không? (vd thêm: "Nếu não bạn ngừng quên?", "Nếu con người sống 500 năm?")
- Tuần 3-4 sản xuất 1 lượt hay rải để né reCAPTCHA/quota?
