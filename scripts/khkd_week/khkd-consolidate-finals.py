#!/usr/bin/env python3
"""Consolidate all KHKD final videos into output/khkd_video/<slug>/{video.mp4,caption.txt}.

Pipeline:
  1. Move any new v4 W1 finals (output/<slug>_vn/) into khkd_video/ as flat files.
  2. Deduplicate by md5 — drop identical clips that exist under multiple names.
  3. For each remaining .mp4 in khkd_video/, create a folder named after its slug
     and move the mp4 + matching caption inside as video.mp4 + caption.txt.
  4. Clean up leftover loose txt files + remove empty source project folders.
"""
import hashlib
import shutil
from pathlib import Path

DEST = Path("output/khkd_video")
NEW_SOURCES = [
    "cordyceps_vn", "hairworm_vn", "toxoplasma_vn", "wolbachia_vn",
    "anglerfish_vn", "phorid_fly_vn", "mantis_shrimp_vn",
]


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)

    # Step 1 — move new v4 W1 finals into khkd_video flat
    for slug in NEW_SOURCES:
        src = Path(f"output/{slug}")
        if not src.exists():
            continue
        final = src / f"{slug}_narrator_cut.mp4"
        cap = src / "caption.txt"
        if final.exists():
            shutil.move(str(final), DEST / f"{slug}.mp4")
            print(f"[moved] {slug}.mp4")
        if cap.exists():
            shutil.move(str(cap), DEST / f"{slug}-caption.txt")
        shutil.rmtree(src)
        print(f"[clean] removed source {src}")

    # Step 2 — dedup by md5
    seen_md5: dict[str, str] = {}
    for mp4 in sorted(DEST.glob("*.mp4")):
        digest = md5_of(mp4)
        if digest in seen_md5:
            print(f"[DUP] {mp4.name} same as {seen_md5[digest]} → delete")
            mp4.unlink()
        else:
            seen_md5[digest] = mp4.name

    # Step 3 — restructure flat → per-folder
    for mp4 in sorted(DEST.glob("*.mp4")):
        stem = mp4.stem
        # Caption naming variants observed:
        #   <slug>-caption.txt  (v4)
        #   <slug>.txt          (numbered legacy from khkd_final)
        cap_src = None
        for cand in (DEST / f"{stem}-caption.txt", DEST / f"{stem}.txt"):
            if cand.exists():
                cap_src = cand
                break
        folder = DEST / stem
        folder.mkdir(exist_ok=True)
        shutil.move(str(mp4), str(folder / "video.mp4"))
        if cap_src:
            shutil.move(str(cap_src), str(folder / "caption.txt"))
        print(f"[folder] {stem}/ (caption={'yes' if cap_src else 'no'})")

    # Step 4 — remove any leftover loose txt at root (e.g., _ALL_CAPTIONS.txt)
    for f in DEST.glob("*.txt"):
        f.unlink()
        print(f"[clean] removed loose {f.name}")

    print()
    print("=== FINAL STRUCTURE ===")
    folders = sorted(p for p in DEST.iterdir() if p.is_dir())
    for f in folders:
        has_video = (f / "video.mp4").exists()
        has_cap = (f / "caption.txt").exists()
        size_mb = (f / "video.mp4").stat().st_size // 1024 // 1024 if has_video else 0
        print(f"  {f.name:<32} {size_mb:>3}MB  video={'✓' if has_video else '✗'} caption={'✓' if has_cap else '✗'}")
    print(f"\n  TOTAL: {len(folders)} videos")


if __name__ == "__main__":
    main()
