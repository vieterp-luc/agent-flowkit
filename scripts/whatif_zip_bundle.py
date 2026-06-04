"""Bundle each What-if video's caption.txt + logo mp4 into per-video folders inside ONE
zip: output/whatif/whatif_upload.zip  →  NN_<slug>/{caption.txt, <slug>_..._logo.mp4}
Run: python scripts/whatif_zip_bundle.py
"""
import os
import sys
import zipfile

sys.path.insert(0, os.getcwd())
from youtube.whatif_batch_upload import ORDER  # [(slug, title), ...] fixed order

OUT = "output/whatif/whatif_upload.zip"


def main():
    with zipfile.ZipFile(OUT, "w") as z:
        for i, (slug, _title) in enumerate(ORDER, 1):
            d = f"output/whatif/{slug}"
            cap = f"{d}/caption.txt"
            vid = f"{d}/{slug}_final_Phong_Vien_TTS_09_logo.mp4"
            folder = f"{i:02d}_{slug}"
            if os.path.exists(cap):
                z.write(cap, f"{folder}/caption.txt", zipfile.ZIP_DEFLATED)
            if os.path.exists(vid):
                z.write(vid, f"{folder}/{os.path.basename(vid)}", zipfile.ZIP_STORED)
                print(f"✓ {folder} (+caption +video)")
            else:
                print(f"⚠ {folder}: thiếu video logo")
    print(f"\n→ {OUT} ({os.path.getsize(OUT)//1024//1024} MB)")


if __name__ == "__main__":
    main()
