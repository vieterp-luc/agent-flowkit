"""Interactive DOM recorder for the Meta AI **Vibes** image→video creation flow.

Opens https://www.meta.ai/vibes in a headed browser, then dumps the live DOM every
15s while YOU manually walk through one creation (start create → upload image → type
description → generate → wait for result). The log captures the real selectors of each
step so meta_browser can be wired to the Vibes flow.

Usage:
    python scripts/meta_vibes_inspect.py --wait 240
Then in the window: click Create, upload an image, enter a prompt, hit generate.
Log → output/_shared/meta_vibes_inspect.log
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright

from agent.services.meta_browser import PROFILE_DIR, LAUNCH_ARGS

VIBES_URL = "https://www.meta.ai/create"
LOGIN_FRAGMENTS = ("facebook.com/login", "instagram.com/accounts/login", "/login")

DUMP_JS = """() => {
  const sl = s => (s || '').toString().slice(0, 70);
  return {
    url: location.href,
    fileInputs: [...document.querySelectorAll('input[type=file]')].map(i => ({
      accept: i.getAttribute('accept') || '', testid: i.getAttribute('data-testid') || '',
      name: i.getAttribute('name') || '', hidden: i.offsetParent === null,
    })),
    composers: [...document.querySelectorAll('textarea,[contenteditable="true"]')].map(c => ({
      ph: c.getAttribute('placeholder') || '', testid: c.getAttribute('data-testid') || '',
      role: c.getAttribute('role') || '', val: sl(c.value || c.textContent),
    })),
    buttons: [...document.querySelectorAll('button,[role="button"]')]
      .map(b => ({
        aria: sl(b.getAttribute('aria-label')), text: sl(b.textContent).trim(),
        testid: b.getAttribute('data-testid') || '',
      }))
      .filter(b => /create|generate|make|imagine|video|upload|add|photo|image|remix|done|next|post/i
                    .test(b.aria + ' ' + b.text + ' ' + b.testid))
      .slice(0, 25),
    videos: [...document.querySelectorAll('video')].map(v => ({
      src: sl(v.src || v.querySelector('source')?.src), cls: sl(v.className),
    })).slice(0, 12),
    imgPreviews: [...document.querySelectorAll('img')]
      .filter(i => /blob:|scontent|fbcdn/.test(i.src || ''))
      .map(i => sl(i.src)).slice(0, 6),
  };
}"""


async def main(wait_s: int) -> int:
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR), headless=False, accept_downloads=True,
        args=LAUNCH_ARGS, viewport={"width": 1320, "height": 920},
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto(VIBES_URL, wait_until="domcontentloaded")
    if any(f in page.url for f in LOGIN_FRAGMENTS):
        print("⚠️  LOGIN_EXPIRED — run scripts/meta_bootstrap.py first.")
        await ctx.close(); await pw.stop(); return 1

    print("\n" + "=" * 64)
    print("→ Trong cửa sổ (meta.ai/create), làm image→video THỦ CÔNG:")
    print("    1) Bấm nút '+' ở composer → chọn 1 ảnh từ máy")
    print("    2) Gõ mô tả vào ô 'Describe an image or video...'")
    print("    3) Bấm 'Create' (hoặc mũi tên gửi)")
    print("    4) Khi 4 video render xong, RÊ CHUỘT lên 1 video để hiện toolbar,")
    print("       và BẤM MỞ 1 video (để lộ <video src>)")
    print(f"→ Script log DOM mỗi 15s trong {wait_s}s. Cứ thao tác bình thường.")
    print("=" * 64 + "\n")

    out = Path("output/_shared/meta_vibes_inspect.log")
    out.parent.mkdir(parents=True, exist_ok=True)
    f = out.open("w")
    for elapsed in range(0, wait_s, 15):
        await asyncio.sleep(min(15, wait_s - elapsed))
        try:
            rep = await page.evaluate(DUMP_JS)
        except Exception as e:
            rep = {"error": str(e)}
        block = (
            f"\n[t={elapsed+15}s] url={rep.get('url','')}\n"
            f"  fileInputs: {rep.get('fileInputs')}\n"
            f"  composers:  {rep.get('composers')}\n"
            f"  buttons:    {rep.get('buttons')}\n"
            f"  videos:     {rep.get('videos')}\n"
            f"  imgPreviews:{rep.get('imgPreviews')}\n"
        )
        print(block, flush=True)
        f.write(block); f.flush()

    print(f"\n→ Done. Log: {out}", flush=True)
    f.close()
    await ctx.close(); await pw.stop()
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", type=int, default=240, help="seconds to observe while you create")
    args = ap.parse_args()
    raise SystemExit(asyncio.run(main(args.wait)))
