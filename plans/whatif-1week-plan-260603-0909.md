# Kế hoạch 1 tuần — Series Short "Nếu... thì sao" (Meta AI video)

**Mục tiêu:** test format "What if" — viễn cảnh siêu thực + giọng đọc, đúng sweet spot Meta AI video. 7 video, mỗi ngày 1.
**Ngày bắt đầu:** 2026-06-03 → 2026-06-09.

---

## Spec chung (áp cho cả 7 video)

| Tham số | Giá trị |
|---------|---------|
| Tỉ lệ | 9:16 dọc (720×1280) |
| Độ dài | 35–50s, **7 scene × ~5s** |
| Giọng | **`Phong_Vien_TTS` · speed 0.9** (đã A/B chọn) + nghỉ ~0.4s giữa scene (BUFFER 0.8) |
| Narrator | VN **18–22 từ/scene**, tiếng Anh cho image/motion prompt |
| Audio | Meta clip im lặng → lồng TTS + BGM cinematic nhẹ (volume ~0.15) tạo căng thẳng |
| Text overlay | Câu "Nếu..." làm hook chữ + nhãn mốc thời gian ("3 phút sau", "1 năm sau") — add CapCut/Canva sau |
| Pipeline | `/fk-video-khkd-meta` (script → ảnh Flow → Meta image→video → TTS → ghép stretch+xfade) |

## Công thức cấu trúc 7 scene (mọi video)

```
S0 HOOK     — đặt câu hỏi "Nếu X?" + hình sốc nhất (dừng ngón tay)
S1 Khoảnh khắc đầu — chuyện gì xảy ra NGAY lập tức (giây/phút đầu)
S2 Leo thang 1     — vài phút/giờ sau, hệ quả vật lý
S3 Leo thang 2     — vài ngày sau, hệ quả sinh tồn
S4 Đỉnh điểm       — cảnh tàn khốc/hùng vĩ nhất
S5 Hệ quả con người— điều gì xảy ra với loài người
S6 Kết ám ảnh      — câu chốt triết lý / con số gây lạnh gáy
```
Narrator theo mốc thời gian leo thang = giữ người xem tới cuối.

## Visual style (ép trong image prompt — Meta mạnh nhất ở đây)
`cinematic, hyper-realistic, dramatic atmospheric lighting, epic scale, photorealistic, 9:16 vertical`
Né: chữ trong khung, mặt người cận (Meta hay méo), hành động phức tạp.

---

## LỊCH 7 NGÀY

### Ngày 1 (T3) — "Nếu Mặt Trời biến mất 24 giờ?" ⭐ (đã script đầy đủ làm mẫu)
Khoa học lõi: ánh sáng mất sau 8 phút; nhiệt độ rơi tự do; quang hợp ngừng.

| S | Narrator VN (~20 từ) | Image/motion EN |
|---|----------------------|-----------------|
| 0 | Nếu ngay bây giờ Mặt Trời đột ngột biến mất, bạn sẽ có đúng tám phút cuối cùng được nhìn thấy ánh sáng. | the Sun vanishing from a daytime sky, light draining away, Earth plunging toward darkness, cinematic cosmic, slow |
| 1 | Tám phút sau, bầu trời tắt lịm hoàn toàn, cả hành tinh chìm trong bóng tối vĩnh viễn giữa ban ngày. | a city street at noon suddenly going pitch black, people frozen in shock, eerie darkness, dramatic |
| 2 | Chỉ trong một tuần, nhiệt độ bề mặt rơi xuống âm mười tám độ, đại dương bắt đầu đóng băng từ trên xuống. | frozen ocean surface forming, ice spreading over waves, cold blue desolate, cinematic wide |
| 3 | Cây cối chết hàng loạt vì không còn quang hợp, chuỗi thức ăn toàn cầu sụp đổ chỉ sau vài tháng. | a forest withering and freezing under starlight, dead trees in ice, bleak atmospheric |
| 4 | Các thành phố hoá thành nghĩa địa băng giá, ánh đèn cuối cùng vụt tắt khi lưới điện ngừng hoạt động. | a frozen metropolis covered in ice and snow under a black sky, last lights dying, epic desolate |
| 5 | Một số ít người sống sót co cụm quanh lò phản ứng và miệng núi lửa, nơi duy nhất còn hơi ấm. | small group of survivors huddled near a glowing geothermal vent in darkness, faint warm light, grim |
| 6 | Trái Đất trở thành một quả cầu băng trôi lặng lẽ trong vũ trụ, không còn ai nhìn thấy bình minh. | Earth as a dark frozen sphere drifting in space, no sunlight, silent cosmic, haunting |

### Ngày 2 (T4) — "Nếu trọng lực biến mất trong 5 giây?"
Lõi: mọi vật không cố định bay lên ~vận tốc quay Trái Đất; khí quyển xáo trộn.
Beats: S0 hỏi + người/xe bắt đầu nhấc khỏi mặt đất → S1 cả thành phố trôi nổi hỗn loạn → S2 đại dương dâng thành cột nước khổng lồ → S3 5 giây hết, mọi thứ rơi sầm xuống → S4 đống đổ nát toàn cầu → S5 ai sống sót (người đang ngồi/thắt dây) → S6 chốt: 5 giây đủ xoá sổ văn minh.

### Ngày 3 (T5) — "Nếu đại dương cạn khô?"
Lõi: lộ địa hình đáy biển sâu nhất; xác tàu; khí hậu sụp.
Beats: S0 nước biển rút để lộ đáy → S1 hàng triệu xác tàu & sinh vật biển mắc cạn → S2 rãnh Mariana lộ ra như vực thẳm → S3 mưa ngừng, lục địa hoá sa mạc muối → S4 thành phố ven biển trơ trọi giữa hoang mạc → S5 loài người khát nước, di cư → S6 chốt: 70% hành tinh thành mộ địa khô cằn.

### Ngày 4 (T6) — "Nếu loài người biến mất ngày mai?"
Lõi: Life After People — thiên nhiên đòi lại trong vài chục năm.
Beats: S0 thành phố vắng tanh không một bóng người → S1 vài ngày: điện tắt, thú hoang vào phố → S2 vài năm: cây leo phủ kín nhà chọc trời → S3 thú rừng đi lại trên đường cao tốc nứt vỡ → S4 công trình sụp đổ, rừng nuốt chửng đô thị → S5 chỉ còn tượng đài & nhựa tồn tại ngàn năm → S6 chốt: Trái Đất không cần chúng ta, vẫn xanh tươi.

### Ngày 5 (T7) — "Nếu Trái Đất ngừng quay?"
Lõi: quán tính 1670 km/h văng mọi thứ; nửa ngày nửa đêm vĩnh viễn.
Beats: S0 hỏi + chân trời bất động → S1 gió siêu bão quét sạch mọi thứ về phía đông → S2 đại dương dồn về hai cực thành siêu lục địa nước → S3 một nửa hành tinh cháy nắng, nửa kia đóng băng → S4 cảnh ranh giới ngày-đêm vĩnh cửu → S5 sự sống chỉ còn ở vành đai chạng vạng → S6 chốt: một vòng quay là tất cả những gì giữ ta sống.

### Ngày 6 (CN) — "Nếu bạn không bao giờ ngủ lại được?" (body-horror, đổi nhịp)
Lõi: dựa bệnh thật Mất ngủ gia đình gây tử vong (FFI).
Beats: S0 hỏi + đôi mắt trắng dã thức trắng đêm → S1 ngày 3: ảo giác bắt đầu → S2 tuần 2: não không thể "dọn rác", tế bào tổn thương → S3 cơ thể suy sụp dù vẫn tỉnh → S4 cảnh não bộ/đồi thị bị ăn mòn → S5 không thuốc nào chữa, chỉ chờ kết thúc → S6 chốt: giấc ngủ không phải nghỉ ngơi, nó giữ bạn sống.

### Ngày 7 (T2) — "Nếu Mặt Trăng rơi xuống Trái Đất?"
Lõi: thuỷ triều khổng lồ; Mặt Trăng vỡ bởi giới hạn Roche trước khi chạm.
Beats: S0 Mặt Trăng to dần lấp kín bầu trời → S1 thuỷ triều dâng nhấn chìm bờ biển → S2 động đất & núi lửa toàn cầu do lực hấp dẫn → S3 Mặt Trăng vỡ vụn thành vành đai đá → S4 mưa thiên thạch lửa rơi xuống → S5 bầu trời rực cháy, loài người trú ẩn → S6 chốt: bầu bạn 4 tỉ năm cũng là kẻ huỷ diệt.

---

## Quy trình sản xuất mỗi ngày (~30-45 phút máy chạy)
1. Tạo project 7 scene ROOT (VERTICAL, realistic), PATCH narrator_text.
2. Gen 7 ảnh Flow (batch nhỏ, pre-flight credits) → tải local.
3. Meta image→video 7 clip (tuần tự, timeout 600, gap 30s, headless) → clips/.
4. TTS 7 scene (Anh_Khoi_TTS 0.95).
5. Ghép: stretch-to-narrator + 720×1280 + xfade 0.4s + (tuỳ chọn) BGM cinematic 0.15.
6. CapCut: thêm text hook "Nếu...?" + nhãn mốc thời gian + watermark crop nếu cần.
7. Caption + hashtag.

## Lịch đăng
1 video/ngày, giờ vàng VN **20:00–21:00** (hoặc 12:00 trưa). Đăng đồng thời TikTok + Reels + YT Shorts.

## KPI test (sau 7 ngày đánh giá)
- Retention 3s & average view duration (hook có giữ không)
- View / share — chủ đề nào viral nhất → double-down tuần sau
- Watermark Meta có cản reach/monetize không

## Câu hỏi mở
- Có cần giọng kịch tính hơn Anh_Khoi_TTS (vd giọng nam trầm doom)? → cân nhắc tạo voice template mới.
- Watermark Meta: chấp nhận cho test, hay crop/che? Nếu monetize nghiêm túc → cân nhắc Veo cho bản chính.
