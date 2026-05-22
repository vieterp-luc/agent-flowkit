# Plan — `/fk-dub-url` skill: lồng tiếng đa giọng + sub VN cho video Trung Quốc

**Date:** 2026-05-21 · **Status:** In progress

## Mục tiêu

Skill mới lấy nguyên video Trung Quốc (donghua / video novel) → **dịch trung thành thoại
gốc** → **lồng tiếng AI đa giọng theo nhân vật** → **burn sub tiếng Việt**.
Hình ảnh & độ dài giữ nguyên 100% — KHÔNG cắt, KHÔNG stretch video.

Khác với skill cũ:
- `/fk-sub-url` — chỉ sub, giữ audio gốc 100%, không lồng tiếng.
- `/fk-reup-url` — narrator AI tự bình luận, KHÔNG dịch trung thành thoại.
- `/fk-dub-url` (mới) — dịch đúng thoại + thay audio bằng lồng tiếng đa giọng.

## Lưu ý bản quyền (cho user quyết định)

Reup full bộ phim TQ chưa được cấp phép lên YouTube ≈ chắc chắn bị Content-ID match /
gậy bản quyền dù đã lồng tiếng. Skill là công cụ trung lập (dịch/localize hợp pháp khi
có quyền hoặc nội dung public-domain/được cấp phép). Việc chọn nguồn & rủi ro pháp lý
thuộc về user — đây chỉ là ghi chú trung thực, không phải lời từ chối.

## Kiến trúc

```
URL ─ReClip:8899─► raw.mp4
  └─► dub_video.py (python3, orchestrator)
       1. ffmpeg extract audio 16k mono
       2. faster-whisper transcribe zh  ← reuse sub_video.transcribe
       3. pyannote diarize  → dub_diarize.py (python3.10 subprocess)
       4. gán speaker cho từng segment (max overlap)
       5. Claude dịch zh→vi + glossary tu-tiên  ← reuse sub_video.translate_batch
       6. voice map: speaker→template (đoán gender qua F0, ghi voicemap.json)
       7. OmniVoice TTS đa giọng → dub_tts_batch.py (python3.10 subprocess)
       8. atempo-fit + numpy ráp dub-track theo timestamp gốc
       9. ffmpeg mix: [audio gốc duck 12%] + [dub] → burn ASS sub VN → final.mp4
```

Diarization + TTS chạy `python3.10` (có torch/omnivoice). Transcribe + dịch chạy
`python3` (có faster-whisper). Pattern subprocess giống `agent/services/tts.py`.

## Fit lồng tiếng (giữ video bất biến)

Mỗi clip TTS neo tại `segment.start`. window = `next.start - this.start`.
Clip dài hơn window → atempo nén (cap 1.7x, giữ pitch). Vẫn dài → cho overlap nhẹ.
Clip ngắn hơn → audio gốc (đã duck) lấp khoảng lặng. Video stream `-map 0:v` copy ý tưởng,
chỉ re-encode khi burn sub. Độ dài = độ dài gốc.

## File

| File | Hành động |
|---|---|
| `scripts/sub_video.py` | Sửa: `extra_rules` cho translate, `vn_only` cho write_ass (backward-compat) |
| `scripts/dub_diarize.py` | Mới — pyannote diarization + F0 gender (python3.10) |
| `scripts/dub_tts_batch.py` | Mới — OmniVoice batch đa giọng (python3.10) |
| `scripts/dub_video.py` | Mới — orchestrator |
| `skills/fk-dub-url.md` | Mới — skill doc |
| `CLAUDE.md` | Sửa: thêm dòng `/fk-dub-url` |

## Phụ thuộc

- ✅ python3.10 + omnivoice, faster-whisper, claude, ffmpeg, pyannote.audio 4.0.4
- ⚠️ **HF token** — model diarization gated. User cần: tạo token HuggingFace, accept
  license `pyannote/speaker-diarization-community-1`, set `HF_TOKEN`.
- Fallback: thiếu pyannote/HF token → tự hạ về chế độ 1 giọng (skill vẫn chạy được).

## Re-run nhanh

Lần chạy đầu cache `segments/translations/turns` vào `<stem>.cache.json` + sinh
`voicemap.json`. User sửa giọng trong voicemap.json → chạy lại `--voicemap` → bỏ qua
whisper/dịch/diarize, chỉ render lại TTS+mix (nhanh).

## Todo

- [ ] Sửa sub_video.py
- [ ] dub_diarize.py
- [ ] dub_tts_batch.py
- [ ] dub_video.py
- [ ] fk-dub-url.md + CLAUDE.md
- [ ] Syntax check + dry-run; document live-test
