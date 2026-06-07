# Pocket Critters — Kế hoạch 7 ngày (19/06 → 25/06)

Nối tiếp ep1-19 (lịch tới 18/06). Cadence **1 video/ngày @ 20:00 ET**. Tập mới **ep20-26**,
con vật + arc MỚI (không trùng 19 tập trước). Giữ chuẩn: 9:16, 7 scene, ~45s, đồng bộ nhân
vật (entity ref) + nhạc riêng, không lời.

## Lịch đăng
| Ngày | ep | Con vật | Arc | Nhạc |
|------|----|---------|-----|------|
| 19/06 | ep20 | 🦉 cú con (real) | Thư viện đêm (đọc sách bên nến) | night_library |
| 20/06 | ep21 | 🦌 hươu con (real) | Sáng xuân hái hoa trên đồng cỏ | spring_meadow |
| 21/06 | ep22 | 🐨 gấu koala con (real) | Ngày lười ôm cây bạch đàn | eucalyptus_nap |
| 22/06 | ep23 | 🐢 rùa con (real) | Dạo vườn tí hon chậm rãi | garden_stroll |
| 23/06 | ep24 | 🦊✨ hồ ly con (fantasy) | Đêm lễ hội đèn lồng trôi | lantern_night |
| 24/06 | ep25 | 🦝 gấu mèo con (real) | Rửa kho báu tí hon (ASMR) | washing_asmr |
| 25/06 | ep26 | 🌙🐇 thỏ mặt trăng (fantasy) | Giã bánh mochi dưới trăng | moon_mochi |

5 real + 2 fantasy, xen kẽ. Mỗi arc khác hẳn 12 arc đã dùng.

## Cung 7 scene mỗi tập (tóm tắt)
- **ep20 cú — thư viện đêm:** đậu trên chồng sách → mở sách → nến ấm → lật trang → uống trà nhỏ → ngáp → ngủ gục trên sách
- **ep21 hươu — sáng xuân:** thức dậy trong cỏ → bước qua hoa → ngửi hoa → đội vòng hoa → uống sương → nằm giữa hoa → ngủ
- **ep22 koala — ôm cây:** ôm thân cây → gặm lá bạch đàn → ngáp → trèo chậm → rúc nách cây → được vuốt → ngủ ôm cây
- **ep23 rùa — dạo vườn:** ló đầu khỏi mai → bò qua rêu → gặm dâu nhỏ → trú dưới nấm → tắm giọt sương → rút vào mai → ngủ
- **ep24 hồ ly — đèn lồng:** đứng bên suối tối → thả đèn lồng nhỏ → đèn trôi sáng → đuôi phát sáng nhẹ → giữa rừng đèn → ngắm trăng → cuộn ngủ
- **ep25 gấu mèo — rửa kho báu:** ôm giỏ đồ nhỏ → nhúng nước → kỳ cọ (ASMR) → xếp hạt cườm → ngắm lấp lánh → lau khô → ôm kho báu ngủ
- **ep26 thỏ mặt trăng — giã mochi:** bên cối dưới trăng → giã bột (nhịp đều ASMR) → nặn mochi → rắc bột → nếm thử → no nê → ngủ dưới trăng

## Sản xuất (khi user OK)
1. Viết data đầy đủ → `scripts/tiny_days_batch4.py` (EPISODES_B4 = ep20-26), wire vào tiny_produce.
2. Gen 7 nhạc track (thêm vào tiny_gen_music TRACKS) — `venv/bin/python scripts/tiny_gen_music.py`.
3. `python3 scripts/tiny_produce.py ep20 .. ep26` — gen đã chậm 1 ảnh/12s (chống API_429), halt-on-0.
   - Quota: mỗi account ~vài chục ảnh/ngày → 7 tập (~56 ảnh) cần **2-3 account** hoặc trải ngày. Đổi account khi halt.
   - Vá clip Meta lỗi (timeout/chat-error) bằng generate-video endpoint + motion camera.
4. Lên lịch: `youtube/pocket_critters_upload_b4.py` 1/ngày từ 2026-06-19 (copy mẫu _b3).

## Ý tưởng dự phòng (cho đợt sau)
cún corgi, vịt con, nhím con solo, sóc con, chuột lang, cá voi tí hon (fantasy), kỳ lân biển,
rồng băng, mèo sao (fantasy), gấu bắc cực con, cáo tuyết, bọ rùa.
