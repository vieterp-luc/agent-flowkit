"""Assemble a cozy/ASMR tiny-animal reel from Meta clips + background music (NO narration).

Unlike meta_assemble (TTS-driven), this: gently slows each silent clip, scales 720x1280,
crossfades between scenes, then lays a soft looping BGM under the whole video with a fade-out.

Run: python scripts/tiny_assemble.py <slug> [music_path] [slowdown] [music_vol]
  slug      → output/<slug>/clips/scene_*.mp4 ; final → output/<slug>/<basename>_final.mp4
  music     → default output/tiny_animals/_bgm/cozy.mp3
"""
import glob
import os
import subprocess
import sys

XFADE = 0.5
DEFAULT_MUSIC = "output/tiny_animals/_bgm/cozy.mp3"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-400:])


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip())


def main(slug, music=DEFAULT_MUSIC, slowdown=1.3, music_vol=0.55):
    out = f"output/{slug}"
    seg_dir = f"{out}/segments"
    os.makedirs(seg_dir, exist_ok=True)
    clips = sorted(glob.glob(f"{out}/clips/scene_*.mp4"))
    if not clips:
        raise SystemExit(f"no clips in {out}/clips")

    # 1) per clip → slowed, scaled 720x1280, silent segment
    segs = []
    for i, clip in enumerate(clips):
        sg = f"{seg_dir}/seg_{i:02d}.mp4"
        vf = (f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
              f"setpts={slowdown}*PTS,fps=24")
        run(["ffmpeg", "-y", "-an", "-i", clip, "-vf", vf,
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", sg])
        segs.append(sg)

    # 2) crossfade-concat video (no audio yet)
    durs = [dur(s) for s in segs]
    tmp = f"{seg_dir}/_concat.mp4"
    if len(segs) == 1:
        run(["ffmpeg", "-y", "-i", segs[0], "-c", "copy", tmp])
    else:
        inputs = []
        for s in segs:
            inputs += ["-i", s]
        parts, vp, off = [], "[0:v]", durs[0] - XFADE
        for i in range(1, len(segs)):
            vo = f"[v{i}]"
            parts.append(f"{vp}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={off:.3f}{vo}")
            vp = vo
            off += durs[i] - XFADE
        run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts),
             "-map", vp, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", tmp])

    # 3) lay soft looping BGM under it, fade out at the end
    total = dur(tmp)
    final = f"{out}/{slug.split('/')[-1]}_final.mp4"
    if music and os.path.exists(music):
        af = f"volume={music_vol},afade=t=out:st={max(0, total - 2):.2f}:d=2"
        run(["ffmpeg", "-y", "-i", tmp, "-stream_loop", "-1", "-i", music,
             "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v", "-map", "[a]",
             "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", final])
    else:
        print(f"⚠ no music ({music}) — final has no audio")
        run(["ffmpeg", "-y", "-i", tmp, "-c", "copy", final])
    print(f"✓ FINAL: {final} ({total:.1f}s, {len(segs)} scenes, music={os.path.basename(music) if os.path.exists(music) else 'NONE'})")


if __name__ == "__main__":
    a = sys.argv
    main(a[1],
         a[2] if len(a) > 2 else DEFAULT_MUSIC,
         float(a[3]) if len(a) > 3 else 1.3,
         float(a[4]) if len(a) > 4 else 0.55)
