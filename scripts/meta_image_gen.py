"""Generate image(s) via Meta AI (browser automation) → save locally.

Calls POST /api/meta/browser/generate-image. Sequential (browser lock). Meta is slow
(1–5 min) — allow a generous timeout. Pass --ref <image> to attach a REFERENCE image
(image→image) so a recurring character stays consistent across scenes.

Single:  python scripts/meta_image_gen.py "a cat surfing a wave" output/foo/cat.jpg
With ref: python scripts/meta_image_gen.py "Thanh Dinh walking in a palace" out.jpg --ref ref/thanh_dinh.jpg
Batch:   python scripts/meta_image_gen.py --batch prompts.txt output/foo [--ref ref.jpg]
         (prompts.txt = one prompt per line → saved as image_01.jpg, image_02.jpg, …)
"""
import json
import os
import shutil
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8100"
GAP_S = 20  # cooldown between images (anti rate-limit), like the video batch


def gen_one(prompt, dest, ref=None, timeout=300):
    body = {"prompt": prompt, "timeout": timeout, "headless": True}
    if ref:
        body["image_path"] = os.path.abspath(ref)
    payload = json.dumps(body).encode()
    req = urllib.request.Request(BASE + "/api/meta/browser/generate-image",
                                 data=payload, headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=timeout + 80).read().decode())
    if not res.get("ok"):
        print(f"  FAILED: {res.get('error')}")
        return False
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    shutil.move(res["path"], dest)
    print(f"  OK → {dest} ({os.path.getsize(dest)//1024} KB)")
    return True


def main(argv):
    ref = None
    if "--ref" in argv:
        i = argv.index("--ref")
        ref = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if argv and argv[0] == "--batch":
        prompts = [l.strip() for l in open(argv[1], encoding="utf-8") if l.strip()]
        outdir = argv[2]
        for i, p in enumerate(prompts, 1):
            dest = f"{outdir}/image_{i:02d}.jpg"
            if os.path.exists(dest):
                print(f"image_{i:02d}: exists, skip"); continue
            if i > 1:
                time.sleep(GAP_S)
            print(f"image_{i:02d}: {p[:60]}…")
            gen_one(p, dest, ref=ref)
    else:
        prompt, dest = argv[0], (argv[1] if len(argv) > 1 else "output/_shared/meta_image/out.jpg")
        gen_one(prompt, dest, ref=ref)


if __name__ == "__main__":
    main(sys.argv[1:])
