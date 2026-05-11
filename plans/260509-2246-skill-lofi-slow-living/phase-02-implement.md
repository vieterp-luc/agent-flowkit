# Phase 02 — Implementation

## Overview

Build skill markdown + backend orchestrator + ambience bootstrap. ~3-4 files mới, 1 file edit.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ User: /fk-video-lofi --preset night_focus --duration 60     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ skills/fk-video-lofi.md  (Claude reads + executes curl)     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ POST /api/lofi/generate {preset, duration_min, visual_mode} │
│   ↓                                                         │
│ agent/api/lofi.py → agent/services/lofi_pipeline.py         │
│   ↓                                                         │
│   1. Load preset from assets/lofi-presets.json              │
│   2. Generate 4 music tracks (Gemini Lyria Pro, sequential) │
│   3. Generate 1 visual image (Flow API)                     │
│   4. Concat music → 12min unique block                      │
│   5. Loop block → target duration                           │
│   6. Mix with ambience (.wav from assets/ambience/)         │
│   7. Image → ken-burns video (ffmpeg zoompan)               │
│   8. Combine video + audio → final.mp4                      │
│   9. Generate YouTube metadata                              │
└─────────────────────────────────────────────────────────────┘
```

## Files to Create

### 1. `assets/lofi-presets.json`
Schema từ phase-01 (5 presets: morning_tea, night_focus, vintage_cafe, sunday_reset, cozy_evening).

### 2. `assets/ambience/*.wav`
Bundled CC0 from Freesound/Pixabay. Files:
- `vinyl_crackle.wav` (~30s loop)
- `rain_light.wav` (~60s)
- `coffee_shop.wav` (~60s)
- `fireplace.wav` (~30s)
- `tea_pour.wav` (~5s one-shot)

### 3. `scripts/lofi_bootstrap_ambience.py`
Download ambience files lần đầu setup. Nếu file đã tồn tại → skip. URLs CC0 hardcoded.

```python
AMBIENCE_SOURCES = {
    "vinyl_crackle.wav": "https://freesound.org/data/previews/.../...wav",
    # ... (need to research and lock CC0 sources)
}
```

### 4. `agent/services/lofi_pipeline.py`
Core orchestrator (~250 lines). Public API:

```python
async def generate_lofi_video(
    preset_id: str,
    duration_min: int = 60,
    visual_mode: str = "static",  # static | slideshow | veo
    output_dir: Path | None = None,
) -> dict:
    """Returns {ok, final_video_path, metadata_path, breakdown}"""
```

Sub-functions (modularize):
- `_generate_music_tracks(prompt, count=4) -> list[Path]` — call Gemini browser N×
- `_concat_music(tracks, output) -> Path` — ffmpeg concat
- `_loop_audio(input, target_sec, output) -> Path` — ffmpeg `-stream_loop`
- `_mix_with_ambience(music, ambience_files, output, music_vol, amb_vol) -> Path`
- `_generate_image(prompt, output) -> Path` — call Flow image gen
- `_image_to_kenburns(image, target_sec, output) -> Path` — ffmpeg zoompan
- `_combine_av(video, audio, output) -> Path`
- `_build_youtube_meta(preset, duration_min) -> dict`

### 5. `agent/api/lofi.py`
FastAPI router (~60 lines):
- `POST /api/lofi/generate` (body: preset, duration_min, visual_mode, async/poll)
- `GET /api/lofi/presets` — list all preset IDs + titles
- `GET /api/lofi/jobs/{job_id}` — poll status (long jobs run as asyncio task)

### 6. `agent/main.py` (EDIT)
Register `lofi_router` at line 184 (`app.include_router(lofi_router, prefix="/api")`).

### 7. `skills/fk-video-lofi.md`
Skill instructions for Claude (~120 lines). Sections:
- Tổng quan + 5 presets
- Bước 0: Chọn preset + duration
- Bước 1: (1 lần) Bootstrap ambience (`python scripts/lofi_bootstrap_ambience.py`)
- Bước 2: Generate (1 curl call, poll)
- Bước 3: Output structure (folders, files)
- Bước 4: YouTube upload (optional, gọi `/fk-youtube-upload`)
- Common errors + fixes

## Implementation Order (TDD-friendly)

1. **Step A**: Create preset JSON + bootstrap ambience script (smallest unit, testable manually)
2. **Step B**: Implement `_generate_music_tracks` + `_concat_music` + `_loop_audio` (audio sub-pipeline)
3. **Step C**: Implement `_generate_image` + `_image_to_kenburns` (visual sub-pipeline)
4. **Step D**: Implement `_mix_with_ambience` + `_combine_av` (mixing)
5. **Step E**: Wire `generate_lofi_video()` orchestrator
6. **Step F**: Add API router + register in main.py
7. **Step G**: Write skill markdown
8. **Step H**: Smoke test (Phase 03)

## Key Code Patterns

### Music gen — sequential vì asyncio.Lock trong GeminiBrowser

```python
async def _generate_music_tracks(prompt: str, count: int, output_dir: Path):
    tracks = []
    for i in range(count):
        resp = await call_gemini_browser({
            "prompt": prompt,
            "model": "Pro",
            "timeout": 300,
        })
        if not resp["ok"]:
            raise RuntimeError(f"Music gen {i+1} failed: {resp['error']}")
        # Move file from output/_shared/gemini_music/ to our output_dir
        src = Path(resp["path"])
        dst = output_dir / f"track_{i+1:02d}.mp4"
        src.rename(dst)
        tracks.append(dst)
    return tracks
```

### Concat music (ffmpeg concat demuxer)

```python
def _concat_music(tracks: list[Path], output: Path) -> Path:
    list_file = output.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{t.absolute()}'" for t in tracks))
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c:a", "libmp3lame", "-b:a", "192k",
        str(output)
    ], check=True)
    return output
```

### Loop to target duration

```python
def _loop_audio(input_path: Path, target_sec: int, output: Path) -> Path:
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(input_path),
        "-t", str(target_sec), "-c", "copy", str(output)
    ], check=True)
    return output
```

### Mix music + ambience (multi-input mix)

```python
def _mix_with_ambience(music, ambience_files, output, music_vol=0.75, amb_vol=0.25):
    inputs = ["-i", str(music)]
    for amb in ambience_files:
        inputs += ["-stream_loop", "-1", "-i", str(amb)]

    # Build filter: music has volume music_vol; each ambience scaled to amb_vol/N
    n_amb = len(ambience_files)
    filter_parts = [f"[0:a]volume={music_vol}[music]"]
    for i in range(n_amb):
        filter_parts.append(f"[{i+1}:a]volume={amb_vol/n_amb}[amb{i}]")
    mix_inputs = "[music]" + "".join(f"[amb{i}]" for i in range(n_amb))
    filter_parts.append(f"{mix_inputs}amix=inputs={n_amb+1}:duration=first[out]")

    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k",
        str(output)
    ], check=True)
    return output
```

### Ken-burns zoom (slow zoom-in over duration)

```python
def _image_to_kenburns(image: Path, target_sec: int, output: Path):
    fps = 30
    total_frames = target_sec * fps
    # Slow zoom from 1.0 → 1.1 over duration; gentle pan
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image),
        "-vf", f"scale=2400:-1,zoompan=z='min(zoom+0.0003,1.1)':d={total_frames}:s=1920x1080:fps={fps}",
        "-t", str(target_sec), "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "fast", "-crf", "23", str(output)
    ], check=True)
    return output
```

### Combine audio + video

```python
def _combine_av(video: Path, audio: Path, output: Path):
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(output)
    ], check=True)
    return output
```

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| 4× Gemini gen tốn ~6min wall (asyncio.Lock serialize) | Acceptable cho 1h video; document trade-off |
| Ambience download fail (URL dead) | Bootstrap script try multiple sources, log failures |
| ffmpeg `zoompan` jitter on long durations | Use `-fps_mode cfr -r 30`, test with 30min sample |
| Loop boundary click/pop | ffmpeg `acrossfade` between iterations (advanced, Phase 04 if needed) |
| Final file size 1h@1080p ~500MB | Document, OK cho YouTube |

## Phase 02 Success Criteria

- [ ] All files created với compile pass
- [ ] `lofi_bootstrap_ambience.py` chạy thành công, tạo 5 .wav files
- [ ] `POST /api/lofi/presets` trả về 5 preset entries
- [ ] Helper functions có docstring + type hints

## Dependencies on Phase 01

Cần user xác nhận 5 decisions trước khi start implement (đặc biệt D2 visual mode → ảnh hưởng `_image_to_kenburns` vs Veo path).
