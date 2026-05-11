"""Probe Gemini UI to find model selector + dropdown items.

Usage: PYTHONUNBUFFERED=1 venv/bin/python scripts/gemini_inspect_model.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright

from agent.services import gemini_selectors as sel
from agent.services.gemini_browser import PROFILE_DIR, LAUNCH_ARGS


async def main() -> int:
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR), headless=False,
        args=LAUNCH_ARGS, viewport={"width": 1280, "height": 800},
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto(sel.APP_URL, wait_until="domcontentloaded")
    await page.locator(sel.COMPOSER).first.wait_for(state="visible", timeout=15_000)
    await asyncio.sleep(2)

    pre = await page.evaluate(
        """() => [...document.querySelectorAll('button')]
            .filter(b => /Nhanh|Pro|Tư duy|Gemini/i.test((b.textContent||'') + ' ' + (b.getAttribute('aria-label')||'')))
            .map(b => ({
              text: (b.textContent||'').trim().slice(0,40),
              aria: b.getAttribute('aria-label')||'',
              testid: b.getAttribute('data-test-id')||'',
              cls: b.className.toString().slice(0,80),
            }))"""
    )
    print("=== Pre-click candidates ===", flush=True)
    for c in pre:
        print(" ", c, flush=True)

    # Try clicking the most likely trigger (smallest button that mentions a model name)
    trigger = page.locator('button:has-text("Nhanh"), button:has-text("Pro"), button:has-text("Tư duy")').last
    if await trigger.count():
        print("\n→ Clicking trigger...", flush=True)
        await trigger.click()
        await asyncio.sleep(1.5)
        post = await page.evaluate(
            """() => [...document.querySelectorAll('[role="menuitem"], [role="option"], li, button')]
                .filter(e => {
                  const t = (e.textContent||'').trim();
                  return /^(Nhanh|Pro|Tư duy|Google AI Plus)$/.test(t.split('\\n')[0]) || /Nhanh|^Pro$|Tư duy/.test(t.slice(0,30));
                })
                .slice(0,15)
                .map(e => ({
                  tag: e.tagName,
                  role: e.getAttribute('role')||'',
                  text: (e.textContent||'').trim().slice(0,60).replace(/\\s+/g,' '),
                  cls: e.className.toString().slice(0,80),
                }))"""
        )
        print("=== Post-click candidates (menu items) ===", flush=True)
        for c in post:
            print(" ", c, flush=True)

    await asyncio.sleep(2)
    await ctx.close()
    await pw.stop()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
