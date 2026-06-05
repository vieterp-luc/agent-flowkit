#!/usr/bin/env python3
"""Generate TTS per scene then assemble final video with stretch + xfade.

Usage: meta-tts-and-assemble.py <slug>

Per scene N:
  1. Generate TTS to output/<slug>/tts/scene_NN.wav (Anh_Khoi_TTS, speed 0.95, full ref_text).
  2. Build segment seg_NN.mp4 = stretch clip to (TTS_dur + 0.5s buffer) via setpts
     (no freeze/tpad), scale to 720x1280, fps 24, audio = TTS only.
  3. Concat all segments with xfade 0.4s + acrossfade → <slug>_final.mp4.

Assumes:
  output/<slug>/ids.json (video_id)
  output/<slug>/clips/scene_NN.mp4 (Meta clips)
"""
import json
import os
import subprocess
import sys
import urllib.request

BASE = "http://127.0.0.1:8100"
REF_AUDIO = "output/_shared/tts_templates/Anh_Khoi_TTS.wav"
SPEED = 0.95
XFADE = 0.4
BUFFER = 0.5


def load_ref_text() -> str:
    with open("output/_shared/tts_templates/templates.json", encoding="utf-8") as f:
        return json.load(f)["Anh_Khoi_TTS"]["text"]


def get_scenes(video_id: str) -> list:
    with urllib.request.urlopen(f"{BASE}/api/scenes?video_id={video_id}", timeout=30) as r:
        return json.loads(r.read())


def ffprobe_dur(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def gen_tts(text: str, out_path: str) -> None:
    if os.path.exists(out_path):
        print(f"  [tts skip] {os.path.basename(out_path)} exists")
        return
    payload = json.dumps({
        "text": text,
        "ref_audio": REF_AUDIO,
        "ref_text": load_ref_text(),
        "speed": SPEED,
        "output_path": out_path,
    }, ensure_ascii=False)
    r = subprocess.run(
        ["curl", "-s", "-m", "180", "-X", "POST",
         f"{BASE}/api/tts/generate",
         "-H", "Content-Type: application/json", "-d", payload],
        capture_output=True, text=True,
    )
    if not os.path.exists(out_path):
        print(f"  [tts ERR] {r.stdout[:200]}")


def build_segment(clip: str, tts: str, seg_out: str) -> None:
    """Stretch clip to (TTS_dur + buffer) via setpts, scale to 720x1280, audio = TTS only."""
    target = ffprobe_dur(tts) + BUFFER
    clip_dur = ffprobe_dur(clip)
    ratio = target / clip_dur  # >1 means slow down (longer)
    # setpts multiplier — to make output LONGER, multiply PTS by ratio
    vf = (
        f"setpts={ratio:.4f}*PTS,"
        "scale=720:1280:force_original_aspect_ratio=increase,"
        "crop=720:1280,fps=24"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", clip,
        "-i", tts,
        "-filter_complex",
        f"[0:v]{vf}[v];[1:a]volume=1.4[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", f"{target:.4f}",
        seg_out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [seg ERR] {r.stderr[-400:]}")
    else:
        print(f"  [seg ok] {os.path.basename(seg_out)} ({target:.2f}s)")


def concat_xfade(segments: list, final_out: str) -> None:
    """Concat segments with xfade 0.4s on video + acrossfade on audio."""
    if not segments:
        print("[ERR] no segments to concat")
        return

    # Build filter_complex chain progressively
    n = len(segments)
    inputs = []
    for seg in segments:
        inputs.extend(["-i", seg])

    # Get durations for xfade offset calculation
    durs = [ffprobe_dur(s) for s in segments]

    fc_parts = []
    last_v, last_a = "[0:v]", "[0:a]"
    cumulative = durs[0]
    for i in range(1, n):
        cumulative -= XFADE  # xfade overlaps
        offset = cumulative
        fc_parts.append(
            f"{last_v}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.4f}[v{i}];"
            f"{last_a}[{i}:a]acrossfade=d={XFADE}[a{i}]"
        )
        last_v, last_a = f"[v{i}]", f"[a{i}]"
        cumulative += durs[i]

    filter_complex = ";".join(fc_parts)
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", last_v, "-map", last_a,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        final_out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[concat ERR] {r.stderr[-500:]}")
    else:
        sz = os.path.getsize(final_out) // 1024 // 1024
        print(f"[OK] Final: {final_out} ({sz} MB)")


def main(slug: str) -> None:
    outdir = f"output/{slug}"
    ids = json.load(open(f"{outdir}/ids.json", encoding="utf-8"))
    os.makedirs(f"{outdir}/tts", exist_ok=True)
    os.makedirs(f"{outdir}/segments", exist_ok=True)

    scenes = sorted(get_scenes(ids["video_id"]), key=lambda s: s["display_order"])

    # Step 1: TTS for all scenes
    print("=== TTS ===")
    for s in scenes:
        idx = f"{s['display_order']:02d}"
        text = (s.get("narrator_text") or "").strip()
        if not text:
            print(f"  [warn] scene_{idx}: no narrator_text")
            continue
        gen_tts(text, f"{outdir}/tts/scene_{idx}.wav")

    # Step 2: Build segments
    print("=== SEGMENTS ===")
    segments = []
    for s in scenes:
        idx = f"{s['display_order']:02d}"
        clip = f"{outdir}/clips/scene_{idx}.mp4"
        tts = f"{outdir}/tts/scene_{idx}.wav"
        seg = f"{outdir}/segments/seg_{idx}.mp4"
        if not (os.path.exists(clip) and os.path.exists(tts)):
            print(f"  [skip] scene_{idx}: missing clip or tts")
            continue
        build_segment(clip, tts, seg)
        if os.path.exists(seg):
            segments.append(seg)

    # Step 3: Concat with xfade
    print("=== CONCAT ===")
    final = f"{outdir}/{slug}_final.mp4"
    concat_xfade(segments, final)


if __name__ == "__main__":
    main(sys.argv[1])
