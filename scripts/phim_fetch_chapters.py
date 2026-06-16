"""Fetch a range of web-novel chapters → local text for /fk-phim scripting.

Many reader sites 403 the default fetcher but serve to a browser UA. This uses curl with a
browser UA + extracts the `chapter-content` container (div-balanced, tags stripped). Saves
each chapter to output/phim/<story>/source/chuong-NN.txt. Skips existing, gap between reqs.

URL template must contain `{n}` for the chapter number.
Run: python3 scripts/phim_fetch_chapters.py <story_slug> "<url_with_{n}>" <start> <end>
e.g. python3 scripts/phim_fetch_chapters.py ngo_hai_tung_le \
        "https://thuviensachpdf.com/truyen-chu/ngo-hai-tung-le-phu-can/chuong-{n}" 2 31
"""
import html
import os
import re
import subprocess
import sys
import time

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
GAP_S = 3


def fetch(url):
    p = subprocess.run(
        ["curl", "-s", "-A", UA, "-H", "Accept-Language: vi,en;q=0.9", "--compressed", "-L", url],
        capture_output=True, text=True, timeout=60)
    return p.stdout


def extract(raw):
    """Pull the real chapter-content element text (skip the <style> block of same class)."""
    for m in re.finditer(r'<div[^>]*class="[^"]*chapter-content[^"]*"[^>]*>', raw):
        start = m.end()
        depth, end = 1, start
        for mm in re.finditer(r'<(/?)div\b', raw[start:]):
            depth += -1 if mm.group(1) else 1
            if depth == 0:
                end = start + mm.start(); break
        chunk = raw[start:end]
        body = re.sub(r'<br\s*/?>', '\n', chunk)
        body = re.sub(r'</p>', '\n\n', body)
        body = re.sub(r'<[^>]+>', '', body)
        body = html.unescape(body).strip()
        # drop trailing cloudflare/js noise
        body = re.split(r'\(function\(\)\{', body)[0].strip()
        if len(body) > 200:
            return body
    return ""


def main(slug, tmpl, start, end):
    out = f"output/phim/{slug}/source"
    os.makedirs(out, exist_ok=True)
    tot = 0
    for n in range(int(start), int(end) + 1):
        dest = f"{out}/chuong-{n:02d}.txt"
        if os.path.exists(dest) and os.path.getsize(dest) > 200:
            w = len(open(dest, encoding="utf-8").read().split())
            print(f"chuong-{n:02d}: exists ({w}w), skip"); tot += w; continue
        raw = fetch(tmpl.replace("{n}", str(n)))
        body = extract(raw)
        if not body:
            print(f"chuong-{n:02d}: ⚠️ EMPTY (blocked? {len(raw)}b) — retry later"); continue
        open(dest, "w", encoding="utf-8").write(body)
        w = len(body.split())
        tot += w
        print(f"chuong-{n:02d}: {w}w → {dest}")
        time.sleep(GAP_S)
    print(f"\n=== total {tot} words across chapters {start}-{end} ===")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
