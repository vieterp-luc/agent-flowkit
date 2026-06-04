# Kế hoạch Tuần 2 — Series Short "Nếu... thì sao" (Meta AI video)

Tiếp nối Tuần 1 (`whatif-1week-plan-260603-0909.md`). **Spec + pipeline + giọng y hệt tuần 1**
(9:16, 7 scene × ~5s, **Phong_Vien_TTS 0.9 + nghỉ ~0.4s**, stretch+xfade, capture `/prompt`-anchored).
7 chủ đề mới, đã script đầy đủ trong `scripts/whatif_days_week2.py` (key `day8`–`day14`).

## 7 chủ đề
| Ngày | Chủ đề | slug | Lõi khoa học |
|------|--------|------|--------------|
| day8 | Nếu oxy biến mất 5 giây? | neu_oxy_bien_mat | bê tông rã, lửa tắt, ozone mất → cháy nắng |
| day9 | Nếu Trái Đất mất từ trường? | neu_mat_tu_truong | gió Mặt Trời bào mòn khí quyển (như Sao Hoả), cực quang |
| day10 | Nếu tất cả núi lửa phun cùng lúc? | neu_nui_lua_phun | mùa đông núi lửa, tro che Mặt Trời |
| day11 | Nếu nước biển dâng 100m? | neu_nuoc_bien_dang | thành phố chìm, di cư, đồng bằng ngập |
| day12 | Nếu hố đen bay qua Hệ Mặt Trời? | neu_ho_den_bay_qua | quỹ đạo vỡ, spaghettification, méo ánh sao |
| day13 | Nếu loài côn trùng biến mất? | neu_con_trung_bien_mat | sụp chuỗi thức ăn, mất thụ phấn → nạn đói |
| day14 | Nếu Mặt Trời phình thành sao đỏ? | neu_mat_troi_phinh_to | nuốt hành tinh trong (finale ~5 tỉ năm) |

Mỗi ngày theo công thức leo thang: HOOK → ngay lập tức → leo thang 1 → leo thang 2 → đỉnh điểm → con người → kết ám ảnh.

## Sản xuất (sẵn sàng chạy)

Pre-flight: server :8100 (extension + Flow credits), Meta login (`meta_bootstrap.py`).

**Cả tuần (orchestrator nền):**
```bash
nohup python3 scripts/whatif_produce.py day8 day9 day10 day11 day12 day13 day14 > /tmp/whatif_w2.out 2>&1 &
# poll output/_shared/whatif_run.log
```
Hoặc từng ngày: `python3 scripts/whatif_produce.py day8`

Mỗi ngày: tạo project + 7 scene + PATCH narrator → gen 7 ảnh Flow (batch nhỏ) → 7 clip Meta image→video → ghép (Phong_Vien 0.9).

📁 **Output:** tất cả vào `output/whatif/<slug>/` (orchestrator tự prefix `whatif/`). Final: `output/whatif/<slug>/<slug>_final_Phong_Vien_TTS_09.mp4`. Script lẻ (regen/assemble) → truyền slug `whatif/<slug>`.

## ⚠️ Lưu ý từ Tuần 1 (đã đúc kết)
- **Giãn cách gen ảnh:** chạy nhiều video 1 mạch → Flow reCAPTCHA (`UNUSUAL_ACTIVITY`). Nên rải, hoặc khi dính: user giải captcha tab Flow + regen **1 ảnh/lần, chậm**.
- **Motion prompt phải animate được từ ảnh** (camera + khí quyển) — đã viết sẵn đúng kiểu; nếu gặp `META_CHAT_ERROR "couldn't animate"` thì đổi motion hoặc gen ảnh khác.
- **Ảnh Flow thi thoảng xoay 90°** → regen ảnh.
- **Capture sai/nhầm video** → dùng `meta_rebuild_from_harvest.py` hoặc `/prompt`-anchored regen.
- Meta gen đôi khi fail 1 lần → retry là được.

## Hậu kỳ + đăng
CapCut: text hook "Nếu...?" + nhãn mốc thời gian; `/fk-gen-caption`. Đăng 1 video/ngày 20:00, TikTok+Reels+YT Shorts.
