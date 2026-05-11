# Phase 2: Ken Burns FFmpeg Helper

**Priority:** P0 (foundation cho 2 skill)
**Status:** ⏳ Pending
**Estimate:** 1 ngày
**Parallel-safe:** ✅ (không phụ thuộc Phase 1)

## Context Links

- Plan overview: [`plan.md`](plan.md)
- Reference patterns: existing FFmpeg trong `/fk-concat`, `/fk-concat-fit-narrator`

## Mục tiêu

Build helper module áp Ken Burns + parallax + transitions lên ảnh tĩnh, output video clip.

**Re-usable cho cả 2 skill** (`/fk-video-book-summary`, `/fk-video-book-quote`) và project khác.

## Architecture

```
[image.png 16:9 hoặc 9:16] → ken_burns_clip(duration, motion, target_resolution)
                          → output mp4 clip với zoom/pan đẹp + transition
```

**Motion presets:**

| Preset | Behavior | Use case |
|--------|----------|----------|
| `zoom_in` | Zoom 1.0 → 1.2x, center | Hook, climax scene |
| `zoom_out` | Zoom 1.2 → 1.0x, center | Reveal, intro |
| `pan_left` | Pan trái → phải | Wide landscape |
| `pan_right` | Pan phải → trái | Wide landscape |
| `pan_up` | Tilt từ dưới lên | Portrait full body |
| `pan_down` | Tilt từ trên xuống | Portrait full body |
| `parallax` | Foreground/background split, di chuyển khác tốc | Scene phức tạp |
| `static` | Không motion (1s freeze) | Quote text overlay |

## Related Code Files

### To create
- `agent/services/ken_burns.py` — FFmpeg filter builder
- `agent/api/ken_burns.py` — REST `POST /api/ken-burns/clip`, `POST /api/ken-burns/concat`
- `agent/models/ken_burns.py` — Pydantic models
- `scripts/test-ken-burns.sh` — visual test harness

### To modify
- `agent/main.py` — register router

## FFmpeg Filter Templates

### Zoom in (smooth)
```
-vf "zoompan=z='if(lte(zoom,1.0),1.0,zoom+0.0015)':d={frames}:s={W}x{H}:fps=30"
```

### Pan left → right
```
-vf "zoompan=z=1.2:x='iw*0.1+(iw*0.6)*on/{frames}':y='ih*0.2':d={frames}:s={W}x{H}:fps=30"
```

### Concat với crossfade
```
-filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset={t}[v]"
```

## Implementation Steps

1. **Implement `agent/services/ken_burns.py`**
   - `class KenBurnsBuilder`:
     - `clip(image_path, duration, motion, resolution) -> output_path`
     - `concat_clips(clips: list, transition='fade', xfade_dur=0.5) -> output_path`
     - `apply_text_overlay(video, text, style='bold_caption') -> output_path`

2. **Text overlay styles:**
   - `bold_caption` — text white + black stroke, bottom-third (Shorts)
   - `quote_centered` — large quote, center, fade in/out (Quote scenes)
   - `subtitle` — small bottom (long-form fallback)

3. **REST endpoint `agent/api/ken_burns.py`:**
   ```
   POST /api/ken-burns/clip
   body: {
     image_path: str,
     duration_seconds: float,
     motion: "zoom_in" | "zoom_out" | "pan_left" | ...,
     resolution: "1920x1080" | "1080x1920" | "1080x1080",
     output_path: str,
     text_overlay?: {text: str, style: str, position: str}
   }
   ```

   ```
   POST /api/ken-burns/concat
   body: {
     clips: [{path, duration}],
     xfade_duration: 0.5,
     output_path: str,
     audio_track?: {path, volume}  // optional music
   }
   ```

4. **Test script `scripts/test-ken-burns.sh`:**
   - Gen 4 ảnh test bằng Imagen
   - Apply 4 motion presets khác nhau
   - Concat 4 clips với crossfade
   - Verify output: 1080x1920, smooth motion, no jitter

## Todo List

- [ ] Implement `ken_burns.py` với 8 motion presets
- [ ] Implement text overlay 3 styles
- [ ] Implement REST endpoints (clip, concat)
- [ ] Register router
- [ ] Compile check pass
- [ ] Visual test: 1 ảnh × 8 motion → review smoothness
- [ ] Visual test: 4 clips concat → verify transition mượt
- [ ] Verify output luôn 30fps, h264, yuv420p (compatible YouTube/TikTok)

## Success Criteria

- ✅ 8 motion presets work, không jitter, không crash
- ✅ Output resolution chính xác 1920x1080 (long-form) hoặc 1080x1920 (Shorts)
- ✅ Crossfade mượt giữa clips
- ✅ Text overlay readable, font load đúng
- ✅ Endpoint trả output path + duration thực tế

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Ảnh aspect ratio khác target | Auto pad hoặc smart crop trước khi apply motion |
| Zoompan stutter ở fps thấp | Force fps=30 trong filter |
| Text overlay font không tồn tại | Bundle font default (Roboto/Inter) trong repo |
| FFmpeg version cũ không support filter | Check version > 4.4 trong startup |

## Next Steps

→ Phase 3 + 4 sẽ dùng helper này
