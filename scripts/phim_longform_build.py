"""Long-form assembler for /fk-phim YouTube episodes (~5-6 min).

KHÁC meta_assemble: không dùng clip Meta. Mỗi scene = 1 ẢNH TĨNH → Ken Burns (zoom/pan
chậm) kéo dài đúng bằng lời kể TTS, rồi concat tất cả với xfade. Nhanh, không watermark
video (chỉ ảnh + pan), hợp long-form storyteller.

Per scene: ensure TTS (Nguyen_Ngoc_Ngan 0.95) → Ken Burns image to (TTS_dur + buffer)
→ 720x1280 segment với audio = narrator. Hướng Ken Burns xen kẽ cho đỡ đơn điệu.

Run: python scripts/phim_longform_build.py <video_id> <slug> [voice] [speed]
     img ở output/<slug>/img/scene_NN.jpg ; narrator lấy từ scenes API theo video_id.
"""
import json
import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phim_scene_source import load  # noqa: E402

BASE = "http://127.0.0.1:8100"
W, H, FPS = 720, 1280, 24
BUFFER, XFADE = 0.6, 0.4  # đệm im lặng cuối mỗi scene; xfade chuyển cảnh


def post(path, payload, timeout=180):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-500:])


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip() or 0)


def ken_burns(img, out, d, idx):
    """1 ảnh tĩnh → clip Ken Burns d giây, 720x1280, no audio. Xen kẽ hướng zoom/pan."""
    frames = max(1, int(d * FPS))
    # 4 kiểu xen kẽ: zoom-in, zoom-out, pan-right, pan-down
    mode = idx % 4
    if mode == 0:
        z = "zoom+0.0006"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 1:
        z = "if(eq(on,1),1.12,zoom-0.0006)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 2:
        z = "1.10"; x = "(iw-iw/zoom)*on/%d" % frames; y = "ih/2-(ih/zoom/2)"
    else:
        z = "1.10"; x = "iw/2-(iw/zoom/2)"; y = "(ih-ih/zoom)*on/%d" % frames
    vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
          f"zoompan=z='{z}':d={frames}:x='{x}':y='{y}':s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", img, "-t", f"{d}", "-r", str(FPS),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19", out])


def main(vid, slug, voice="Nguyen_Ngoc_Ngan_TTS", speed=0.95):
    out = f"output/{slug}"
    tag = f"{voice}_{str(speed).replace('.', '')}"
    name = os.path.basename(slug)
    img_dir, tts, seg = f"{out}/img", f"{out}/tts_{tag}", f"{out}/segments_{tag}"
    final = f"{out}/{name}_final_{tag}.mp4"
    for d in (tts, seg):
        os.makedirs(d, exist_ok=True)

    scenes = load(vid, slug)
    segs = []
    for i, s in enumerate(scenes):
        n = s["display_order"]
        img = f"{img_dir}/scene_{n:02d}.jpg"
        if not os.path.exists(img):
            print(f"scene_{n:02d}: NO IMAGE, skip"); continue
        wav = f"{tts}/scene_{n:02d}.wav"
        if not os.path.exists(wav):
            post("/api/tts/generate", {"text": s["narrator_text"], "template": voice,
                                       "speed": speed, "output_path": wav})
        d = dur(wav) + BUFFER
        kb = f"{seg}/kb_{n:02d}.mp4"
        ken_burns(img, kb, d, i)
        # ghép audio narrator (pad cho khớp), xuất segment có cả A/V
        sg = f"{seg}/seg_{n:02d}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", kb, "-i", wav,
             "-filter_complex", f"[1:a]apad=pad_dur={BUFFER},volume=1.4,aformat=sample_rates=48000:channel_layouts=stereo[a]",
             "-map", "0:v", "-map", "[a]", "-t", f"{d}", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", sg])
        segs.append(sg)
        print(f"scene_{n:02d}: {d:.1f}s (KenBurns mode {i % 4})")

    if not segs:
        sys.exit("Không có segment nào — thiếu ảnh?")
    # concat với xfade dây chuyền
    inputs = []
    for sg in segs:
        inputs += ["-i", sg]
    fc, prev, off = [], "0", 0.0
    durs = [dur(s) for s in segs]
    if len(segs) == 1:
        run(["cp", segs[0], final])
    else:
        cur = "[0:v]"
        acur = "[0:a]"
        off = durs[0] - XFADE
        for k in range(1, len(segs)):
            vlab = f"[v{k}]"; alab = f"[a{k}]"
            fc.append(f"{cur}[{k}:v]xfade=transition=fade:duration={XFADE}:offset={off:.3f}{vlab}")
            fc.append(f"{acur}[{k}:a]acrossfade=d={XFADE}{alab}")
            cur, acur = vlab, alab
            if k < len(segs) - 1:
                off += durs[k] - XFADE
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
             "-map", cur, "-map", acur, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-c:a", "aac", "-ar", "48000", final])
    total = dur(final)
    print(f"\n✅ FINAL: {final} ({total:.1f}s = {total/60:.1f} min, {len(segs)} scenes)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         sys.argv[3] if len(sys.argv) > 3 else "Nguyen_Ngoc_Ngan_TTS",
         float(sys.argv[4]) if len(sys.argv) > 4 else 0.95)
