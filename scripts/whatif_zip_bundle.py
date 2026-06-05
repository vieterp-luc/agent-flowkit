"""Bundle each What-if video's caption.txt + logo mp4 into per-video folders inside ONE
zip → NN_<slug>/{caption.txt, <slug>_..._logo.mp4}.

  python scripts/whatif_zip_bundle.py                          # all → whatif_upload.zip
  python scripts/whatif_zip_bundle.py --from 15 --to 28 --out output/whatif/whatif_week34_upload.zip
"""
import argparse
import os
import sys
import zipfile

sys.path.insert(0, os.getcwd())
from youtube.whatif_batch_upload import ORDER  # [(slug, title), ...] fixed order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", type=int, default=1, help="1-indexed start in ORDER")
    ap.add_argument("--to", dest="end", type=int, default=len(ORDER), help="1-indexed end (inclusive)")
    ap.add_argument("--out", default="output/whatif/whatif_upload.zip")
    args = ap.parse_args()

    subset = ORDER[args.start - 1:args.end]
    with zipfile.ZipFile(args.out, "w") as z:
        for n, (slug, _title) in enumerate(subset, 1):
            d = f"output/whatif/{slug}"
            cap = f"{d}/caption.txt"
            vid = f"{d}/{slug}_final_Phong_Vien_TTS_09_logo.mp4"
            folder = f"{n:02d}_{slug}"
            if os.path.exists(cap):
                z.write(cap, f"{folder}/caption.txt", zipfile.ZIP_DEFLATED)
            if os.path.exists(vid):
                z.write(vid, f"{folder}/{os.path.basename(vid)}", zipfile.ZIP_STORED)
                print(f"✓ {folder} (+caption +video)")
            else:
                print(f"⚠ {folder}: thiếu video logo")
    print(f"\n→ {args.out} ({os.path.getsize(args.out)//1024//1024} MB)")


if __name__ == "__main__":
    main()
