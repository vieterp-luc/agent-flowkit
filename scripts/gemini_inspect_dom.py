"""Debug helper — sends a music prompt then dumps audio/video/download-button candidates.

Usage:
    python scripts/gemini_inspect_dom.py "tạo nhạc lo-fi" --wait 180
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright

from agent.services import gemini_selectors as sel
from agent.services.gemini_browser import PROFILE_DIR, LAUNCH_ARGS


async def main(prompt: str, wait_s: int) -> int:
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        accept_downloads=True,
        args=LAUNCH_ARGS,
        viewport={"width": 1280, "height": 800},
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()

    await page.goto(sel.APP_URL, wait_until="domcontentloaded")
    await page.locator(sel.COMPOSER).first.wait_for(state="visible", timeout=15_000)
    await page.locator(sel.COMPOSER).first.fill(prompt)
    await page.locator(sel.COMPOSER).first.press("Enter")
    print(f"→ Prompt sent. Waiting {wait_s}s while Gemini renders...")

    out_path = Path("output/_shared/gemini_inspect.log")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_f = out_path.open("w")
    for elapsed in range(0, wait_s, 30):
        await asyncio.sleep(min(30, wait_s - elapsed))
        report = await page.evaluate(
            """() => {
              const audios = [...document.querySelectorAll('audio')].map(a => ({
                src: a.src || a.querySelector('source')?.src || '',
                aria: a.getAttribute('aria-label') || '',
                cls: a.className,
              }));
              const videos = [...document.querySelectorAll('video')].map(v => ({
                src: v.src || v.querySelector('source')?.src || '',
                cls: v.className,
              }));
              const downloadBtns = [...document.querySelectorAll('button')]
                .filter(b => /download|tải/i.test(b.getAttribute('aria-label') || '')
                          || /download|tải/i.test(b.textContent || ''))
                .map(b => ({
                  aria: b.getAttribute('aria-label') || '',
                  text: (b.textContent || '').trim().slice(0, 60),
                  testid: b.getAttribute('data-test-id') || '',
                }));
              const lyriaSignals = [...document.querySelectorAll('[class*="lyria" i],[class*="music" i],[class*="audio" i]')]
                .slice(0, 10)
                .map(e => ({tag: e.tagName, cls: e.className.toString().slice(0, 80)}));
              return { audios, videos, downloadBtns, lyriaSignals };
            }"""
        )
        block = (
            f"\n[t={elapsed+30}s]\n"
            f"  audios:        {report['audios']}\n"
            f"  videos:        {report['videos']}\n"
            f"  downloadBtns:  {report['downloadBtns']}\n"
            f"  lyriaSignals:  {report['lyriaSignals']}\n"
        )
        print(block, flush=True)
        out_f.write(block); out_f.flush()

    print(f"\n→ Inspection done. Log: {out_path}", flush=True)
    out_f.close()
    await ctx.close()
    await pw.stop()
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--wait", type=int, default=180)
    args = p.parse_args()
    sys.exit(asyncio.run(main(args.prompt, args.wait)))
