"""Headed Chromium login helper for Meta AI.

One-time setup: opens a visible Chromium with the persistent profile so you can log
into Meta AI (via Facebook / Instagram / Meta account). After login, close the
window — the profile (cookies/session) is saved for headless generation later.

Usage:
    python scripts/meta_bootstrap.py
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

PROFILE_DIR = Path("output/_shared/meta_profile")
APP_URL = "https://www.meta.ai/"


async def main() -> None:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.goto(APP_URL)

    print(f"\n→ Profile: {PROFILE_DIR.resolve()}")
    print("→ Đăng nhập Meta AI (Facebook/Instagram/Meta account) trong cửa sổ vừa mở.")
    print("→ Sau khi vào được Meta AI chat, ĐÓNG cửa sổ để lưu session.\n")

    closed = asyncio.Event()
    ctx.on("close", lambda _: closed.set())
    await closed.wait()

    await pw.stop()
    print("✓ Bootstrap done — profile saved.")


if __name__ == "__main__":
    asyncio.run(main())
