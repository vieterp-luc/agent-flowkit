"""Overlay a semi-transparent logo on a video's top-left corner. Reusable + importable.

Defaults match the What-if branding: 13% of video width, 75% transparent (alpha 0.25),
12px margin, logo at assets/whatif_logo.png.

CLI:  python scripts/add_logo.py <video> [out] [logo] [scale_pct] [alpha] [margin]
API:  from add_logo import brand;  brand(video) -> out_path ("<video>_logo.mp4")
"""
import os
import subprocess
import sys

DEFAULT_LOGO = "assets/whatif_logo.png"


def _video_width(path: str) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip()
    return int(out)


def brand(video: str, out: str = None, logo: str = DEFAULT_LOGO,
          scale_pct: float = 13, alpha: float = 0.25, margin: int = 12) -> str:
    if not os.path.exists(logo):
        raise FileNotFoundError(f"logo not found: {logo}")
    lw = max(1, round(_video_width(video) * scale_pct / 100))
    if out is None:
        base, ext = os.path.splitext(video)
        out = f"{base}_logo{ext}"
    fc = (f"[1:v]scale={lw}:-1,format=rgba,colorchannelmixer=aa={alpha}[lg];"
          f"[0:v][lg]overlay={margin}:{margin}[v]")
    cmd = ["ffmpeg", "-y", "-i", video, "-i", logo, "-filter_complex", fc,
           "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-r", "24", "-c:a", "copy", out]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-400:])
    return out


if __name__ == "__main__":
    a = sys.argv
    out = brand(
        a[1],
        out=a[2] if len(a) > 2 and a[2] != "-" else None,
        logo=a[3] if len(a) > 3 else DEFAULT_LOGO,
        scale_pct=float(a[4]) if len(a) > 4 else 13,
        alpha=float(a[5]) if len(a) > 5 else 0.25,
        margin=int(a[6]) if len(a) > 6 else 12,
    )
    print(f"✓ branded → {out} ({os.path.getsize(out)//1024} KB)")
