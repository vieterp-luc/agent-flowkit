"""Debug helper — sends a video prompt to Meta AI, then dumps live DOM candidates
(videos, composers, download buttons) so you can patch agent/services/meta_selectors.py.

Meta AI's DOM is undocumented and shifts often. Run this whenever generation breaks:
    python scripts/meta_inspect_dom.py "a cat surfing a wave" --wait 120
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright

from agent.services import meta_selectors as sel
from agent.services.meta_browser import PROFILE_DIR, LAUNCH_ARGS


async def main(prompt: str, wait_s: int) -> int:
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        accept_downloads=True,
        args=LAUNCH_ARGS,
        viewport={"width": 1280, "height": 900},
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()

    await page.goto(sel.APP_URL, wait_until="domcontentloaded")
    if any(frag in page.url for frag in sel.LOGIN_URL_FRAGMENTS):
        print("⚠️  LOGIN_EXPIRED — run scripts/meta_bootstrap.py first.")
        await ctx.close(); await pw.stop()
        return 1

    # Enter the dedicated video flow first (matches meta_browser.generate_video)
    try:
        toggle = page.locator(sel.VIDEO_MODE_TOGGLE).first
        if await toggle.count() and await toggle.is_visible():
            await toggle.click()
            await page.locator(sel.COMPOSER_VIDEO).first.wait_for(state="visible", timeout=10_000)
            print("→ Entered video mode (Create video).")
    except Exception as e:
        print(f"⚠️  Could not enter video mode ({e}) — using chat composer.")

    composer = page.locator(sel.COMPOSER).first
    try:
        await composer.wait_for(state="visible", timeout=20_000)
        await composer.fill(prompt)
        await composer.press("Enter")
        print(f"→ Prompt sent. Waiting {wait_s}s while Meta AI renders...")
    except Exception as e:
        print(f"⚠️  COMPOSER not found ({e}). Dumping composer candidates only.")

    out_path = Path("output/_shared/meta_inspect.log")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_f = out_path.open("w")
    for elapsed in range(0, wait_s, 20):
        await asyncio.sleep(min(20, wait_s - elapsed))
        report = await page.evaluate(
            """() => {
              const videos = [...document.querySelectorAll('video')].map(v => ({
                src: (v.src || v.querySelector('source')?.src || '').slice(0, 120),
                cls: v.className.toString().slice(0, 80),
              }));
              const composers = [...document.querySelectorAll('textarea,[contenteditable="true"]')]
                .map(c => ({
                  tag: c.tagName,
                  placeholder: c.getAttribute('placeholder') || '',
                  role: c.getAttribute('role') || '',
                }));
              const buttons = [...document.querySelectorAll('button,[role="button"]')]
                .filter(b => /download|video|send|tải/i.test(
                  (b.getAttribute('aria-label') || '') + ' ' + (b.textContent || '')))
                .slice(0, 15)
                .map(b => ({
                  aria: b.getAttribute('aria-label') || '',
                  text: (b.textContent || '').trim().slice(0, 40),
                }));
              return { videos, composers, buttons };
            }"""
        )
        block = (
            f"\n[t={elapsed+20}s]\n"
            f"  videos:    {report['videos']}\n"
            f"  composers: {report['composers']}\n"
            f"  buttons:   {report['buttons']}\n"
        )
        print(block, flush=True)
        out_f.write(block); out_f.flush()

    print(f"\n→ Inspection done. Log: {out_path}", flush=True)
    out_f.close()
    await ctx.close()
    await pw.stop()
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", help="video prompt to send")
    ap.add_argument("--wait", type=int, default=120, help="seconds to observe the DOM")
    args = ap.parse_args()
    raise SystemExit(asyncio.run(main(args.prompt, args.wait)))
