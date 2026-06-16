"""Generic assembler: build a final vertical video from Meta clips + TTS narration.

Per scene: ensure TTS (Anh_Khoi_TTS, 0.95) → STRETCH the Meta clip smoothly to narrator
duration (setpts — no freeze) → scale/crop 720x1280 → narrator audio → segment. Then
concat all with a 0.4s crossfade. Meta clips are silent → narrator is the only audio.

Run: python scripts/meta_assemble.py <video_id> <slug> [voice] [speed]
     (voice default Anh_Khoi_TTS, speed default 0.95; outputs are suffixed by voice so
      multiple voices can coexist for A/B comparison)
"""
import json
import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phim_scene_source import load  # noqa: E402

BASE = "http://127.0.0.1:8100"
# BUFFER = trailing silence after each narration; audible inter-scene pause ≈ BUFFER − XFADE
BUFFER, XFADE = 0.8, 0.4


def post(path, payload, timeout=180):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-400:])


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip())


def main(vid, slug, voice="Phong_Vien_TTS", speed=0.9):
    out = f"output/{slug}"
    tag = f"{voice}_{str(speed).replace('.', '')}"  # e.g. Phong_Vien_TTS_085
    name = os.path.basename(slug)  # slug may be "whatif/<x>" → use only "<x>" in filenames
    clips, tts, seg = f"{out}/clips", f"{out}/tts_{tag}", f"{out}/segments_{tag}"
    final = f"{out}/{name}_final_{tag}.mp4"
    for d in (tts, seg):
        os.makedirs(d, exist_ok=True)
    scenes = load(vid, slug)

    # auto-detect target orientation from the first available clip (landscape → 1280x720,
    # else portrait 720x1280). Lets the same builder serve 16:9 and 9:16 without a flag.
    W, H = 720, 1280
    for s in scenes:
        c = f"{clips}/scene_{s['display_order']:02d}.mp4"
        if os.path.exists(c):
            wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v",
                                 "-show_entries", "stream=width,height", "-of", "csv=p=0", c],
                                capture_output=True, text=True).stdout.strip().split(",")
            if len(wh) == 2 and int(wh[0]) > int(wh[1]):
                W, H = 1280, 720
            break
    print(f"[orient] target {W}x{H}")

    segs = []
    for s in scenes:
        n = s["display_order"]
        clip = f"{clips}/scene_{n:02d}.mp4"
        if not os.path.exists(clip):
            print(f"scene_{n:02d}: NO CLIP, skip"); continue
        wav = f"{tts}/scene_{n:02d}.wav"
        if not os.path.exists(wav):
            post("/api/tts/generate", {"text": s["narrator_text"], "template": voice,
                                       "speed": speed, "output_path": wav})
        target = round(dur(wav) + BUFFER, 2)
        sg = f"{seg}/seg_{n:02d}.mp4"
        factor = target / dur(clip)
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"setpts={factor:.5f}*PTS,fps=24")
        # apad pads narrator audio with silence so the segment's AUDIO length == VIDEO
        # length (target). Without it, -t doesn't pad audio → acrossfade packs
        # narrations together and audio drifts ~BUFFER ahead of video per scene.
        run(["ffmpeg", "-y", "-i", clip, "-i", wav, "-filter_complex",
             f"[0:v]{vf}[v];[1:a]volume=1.4,apad[a]", "-map", "[v]", "-map", "[a]",
             "-t", str(target), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
             "-c:a", "aac", "-ar", "48000", "-ac", "2", sg])
        segs.append(sg)
        print(f"scene_{n:02d}: stretch x{factor:.2f} → {target:.1f}s")

    inputs = []
    for sg in segs:
        inputs += ["-i", sg]
    durs = [dur(x) for x in segs]
    parts, vp, ap, off = [], "[0:v]", "[0:a]", durs[0] - XFADE
    for i in range(1, len(segs)):
        vo, ao = f"[v{i}]", f"[a{i}]"
        parts.append(f"{vp}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={off:.3f}{vo}")
        parts.append(f"{ap}[{i}:a]acrossfade=d={XFADE}{ao}")
        vp, ap = vo, ao
        off += durs[i] - XFADE
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", vp, "-map", ap,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
         "-c:a", "aac", "-ar", "48000", "-ac", "2", final])
    print(f"\n✓ FINAL: {final} ({len(segs)} scenes, {dur(final):.1f}s)")


if __name__ == "__main__":
    voice = sys.argv[3] if len(sys.argv) > 3 else "Phong_Vien_TTS"
    speed = float(sys.argv[4]) if len(sys.argv) > 4 else 0.9
    main(sys.argv[1], sys.argv[2], voice, speed)
