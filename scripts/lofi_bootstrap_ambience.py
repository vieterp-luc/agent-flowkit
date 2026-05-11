"""Bootstrap ambience .wav files for /fk-video-lofi pipeline.

Synthesizes 5 royalty-free ambience tracks via ffmpeg noise generators + filters.
Run once after install. Idempotent — skips files that already exist.

Usage:
    python scripts/lofi_bootstrap_ambience.py
    python scripts/lofi_bootstrap_ambience.py --force   # re-generate all
"""
import argparse
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path("assets/ambience")

# Each entry: (filename, duration_s, ffmpeg_filter_chain)
# Filters use lavfi noise sources + bandpass/lowpass to shape into ambience textures.
RECIPES = {
    "vinyl_crackle.wav": (
        30,
        # Pink noise + bandpass for vinyl hiss + occasional pops via tremolo
        "anoisesrc=color=pink:amplitude=0.05:sample_rate=44100,"
        "highpass=f=2000,lowpass=f=8000,"
        "tremolo=f=0.3:d=0.4,"
        "volume=0.6"
    ),
    "rain_light.wav": (
        60,
        # White noise + lowpass for soft rain feel
        "anoisesrc=color=white:amplitude=0.08:sample_rate=44100,"
        "lowpass=f=4000,highpass=f=200,"
        "volume=0.7"
    ),
    "coffee_shop.wav": (
        60,
        # Brown noise (rumble) + slight resonance for distant chatter feel
        "anoisesrc=color=brown:amplitude=0.06:sample_rate=44100,"
        "lowpass=f=1500,"
        "volume=0.65"
    ),
    "fireplace.wav": (
        30,
        # Brown noise + tremolo for crackling fire
        "anoisesrc=color=brown:amplitude=0.07:sample_rate=44100,"
        "lowpass=f=1200,"
        "tremolo=f=2.5:d=0.6,"
        "volume=0.7"
    ),
    "tea_pour.wav": (
        5,
        # Short pink noise burst with envelope for water pour
        "anoisesrc=color=pink:amplitude=0.12:sample_rate=44100,"
        "highpass=f=400,lowpass=f=6000,"
        "afade=t=in:st=0:d=0.3,afade=t=out:st=4.2:d=0.8,"
        "volume=0.8"
    ),
}


def synthesize(filename: str, duration_s: int, filter_chain: str, dest: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", f"{filter_chain}",
        "-t", str(duration_s),
        "-ac", "2", "-ar", "44100",
        "-c:a", "pcm_s16le",
        str(dest),
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ ffmpeg failed for {filename}: {e}", file=sys.stderr)
        return False


def main(force: bool) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"→ Output: {OUT_DIR.resolve()}")
    if not _has_ffmpeg():
        print("✗ ffmpeg not found in PATH. Install: brew install ffmpeg", file=sys.stderr)
        return 1

    created, skipped, failed = 0, 0, 0
    for filename, (duration, filter_chain) in RECIPES.items():
        dest = OUT_DIR / filename
        if dest.exists() and not force:
            print(f"  ⊙ {filename} ({dest.stat().st_size // 1024} KB) — skip (exists)")
            skipped += 1
            continue
        print(f"  → synthesizing {filename} ({duration}s)...")
        if synthesize(filename, duration, filter_chain, dest):
            print(f"  ✓ {filename} ({dest.stat().st_size // 1024} KB)")
            created += 1
        else:
            failed += 1

    print(f"\nDone — {created} created, {skipped} skipped, {failed} failed.")
    return 0 if failed == 0 else 1


def _has_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="Re-generate even if file exists")
    sys.exit(main(p.parse_args().force))
