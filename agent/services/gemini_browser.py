"""Playwright-driven Gemini music generator.

Drives the Gemini chat UI in a persistent Chromium instance to bypass the
brittle reverse-engineered StreamGenerate f.req payload. Login state is kept
in `output/_shared/gemini_profile/` — bootstrap once via scripts/gemini_bootstrap.py.
"""
import asyncio
import logging
import re
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    async_playwright,
    BrowserContext,
    Playwright,
    TimeoutError as PWTimeout,
)

from agent.services import gemini_selectors as sel

logger = logging.getLogger(__name__)

PROFILE_DIR = Path("output/_shared/gemini_profile")
DOWNLOAD_DIR = Path("output/_shared/gemini_music")

LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
]


class GeminiBrowserError(RuntimeError):
    """Raised on login expiry, quota, or selector failures."""


class GeminiBrowser:
    def __init__(self, headless: bool = True):
        self._pw: Optional[Playwright] = None
        self._ctx: Optional[BrowserContext] = None
        self._lock = asyncio.Lock()
        self._headless = headless

    async def start(self) -> None:
        if self._ctx is not None:
            return
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self._pw = await async_playwright().start()
        self._ctx = await self._pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=self._headless,
            accept_downloads=True,
            args=LAUNCH_ARGS,
            viewport={"width": 1280, "height": 800},
        )
        logger.info("GeminiBrowser started (headless=%s)", self._headless)

    async def stop(self) -> None:
        if self._ctx is not None:
            try:
                await self._ctx.close()
            except Exception as e:
                logger.warning("ctx.close error: %s", e)
            self._ctx = None
        if self._pw is not None:
            try:
                await self._pw.stop()
            except Exception as e:
                logger.warning("pw.stop error: %s", e)
            self._pw = None
        logger.info("GeminiBrowser stopped")

    @property
    def ready(self) -> bool:
        return self._ctx is not None

    async def generate_music(self, prompt: str, timeout_s: float = 300, model: str = "Pro") -> Path:
        """Open Gemini, ensure model, send prompt, wait for music, fetch → save → return path.

        model: "Pro" (longer 2-3min tracks) | "Nhanh" (default 30s) | "Tư duy"
        """
        if self._ctx is None:
            raise GeminiBrowserError("GeminiBrowser not started")

        async with self._lock:
            page = await self._ctx.new_page()
            try:
                await page.goto(sel.APP_URL, wait_until="domcontentloaded", timeout=30_000)

                if sel.LOGIN_URL_FRAGMENT in page.url:
                    raise GeminiBrowserError(
                        "LOGIN_EXPIRED — re-run scripts/gemini_bootstrap.py"
                    )

                composer = page.locator(sel.COMPOSER).first
                try:
                    await composer.wait_for(state="visible", timeout=15_000)
                except PWTimeout as e:
                    raise GeminiBrowserError(f"COMPOSER_NOT_FOUND: {sel.COMPOSER}") from e

                await self._ensure_new_chat(page)
                await self._select_model(page, model)

                await composer.fill(f"Tạo bản nhạc: {prompt}")
                await composer.press("Enter")

                video = page.locator(sel.MUSIC_VIDEO).first
                try:
                    await video.wait_for(state="attached", timeout=int(timeout_s * 1000))
                except PWTimeout as e:
                    body_text = (await page.text_content("body") or "").lower()
                    if any(q in body_text for q in sel.QUOTA_MESSAGES):
                        raise GeminiBrowserError("QUOTA_REACHED") from e
                    raise GeminiBrowserError(
                        f"MUSIC_TIMEOUT after {timeout_s}s — video element never appeared"
                    ) from e

                src = await video.get_attribute("src")
                if not src:
                    raise GeminiBrowserError("MUSIC_NO_SRC")
                filename = self._filename_from_url(src)
                content = await page.evaluate(
                    """async (url) => {
                       const r = await fetch(url, {credentials: 'include'});
                       if (!r.ok) throw new Error('FETCH_' + r.status);
                       const buf = await r.arrayBuffer();
                       return Array.from(new Uint8Array(buf));
                    }""",
                    src,
                )
                dest = self._unique_dest(filename)
                dest.write_bytes(bytes(content))
                logger.info("Music saved: %s (%d KB)", dest, dest.stat().st_size // 1024)
                return dest
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

    @staticmethod
    async def _ensure_new_chat(page) -> bool:
        """Click 'New chat' if a button is visible — avoids reusing prior conversation
        (which causes Lyria to skip music gen on duplicate prompts).
        Best-effort: returns True on success, False if button not found (caller proceeds anyway).
        """
        loc = page.locator(sel.NEW_CHAT_BUTTON).first
        try:
            if await loc.count() == 0:
                return False
            await loc.wait_for(state="visible", timeout=2_000)
            await loc.click()
            await asyncio.sleep(1.0)  # let chat reset
            logger.info("Started new chat")
            return True
        except Exception as e:
            logger.warning("new_chat click failed: %s — proceeding with current chat", e)
            return False

    @staticmethod
    async def _select_model(page, model: str) -> None:
        """Open model dropdown and click the requested model. Idempotent — safe to call when already selected."""
        trigger = page.locator(sel.MODEL_TRIGGER).first
        await trigger.wait_for(state="visible", timeout=10_000)
        current = ((await trigger.text_content()) or "").strip()
        if current.lower().startswith(model.lower()):
            logger.info("Model already %s, skip switch", model)
            return
        await trigger.click()
        item = page.get_by_role("menuitem", name=re.compile(rf"^{re.escape(model)}\b"))
        try:
            await item.first.wait_for(state="visible", timeout=5_000)
            await item.first.click()
        except PWTimeout as e:
            await page.keyboard.press("Escape")
            raise GeminiBrowserError(
                f"MODEL_NOT_AVAILABLE: '{model}' — check Google AI Plus subscription"
            ) from e
        await asyncio.sleep(0.5)
        logger.info("Switched model: %s → %s", current, model)

    @staticmethod
    def _filename_from_url(url: str) -> str:
        import re
        m = re.search(r"[?&]filename=([^&]+)", url)
        if m:
            from urllib.parse import unquote
            return unquote(m.group(1))
        return f"gemini_music_{int(asyncio.get_event_loop().time() * 1000)}.mp4"

    @staticmethod
    def _unique_dest(filename: str) -> Path:
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        dest = DOWNLOAD_DIR / filename
        i = 1
        stem, suffix = Path(filename).stem, Path(filename).suffix or ".mp4"
        while dest.exists():
            dest = DOWNLOAD_DIR / f"{stem}_{i}{suffix}"
            i += 1
        return dest


# ─── Singleton ────────────────────────────────────────────────

_singleton: Optional[GeminiBrowser] = None
_init_lock = asyncio.Lock()


async def init_browser(headless: bool = True) -> GeminiBrowser:
    """Idempotent + race-safe singleton init."""
    global _singleton
    async with _init_lock:
        if _singleton is None or not _singleton.ready:
            inst = GeminiBrowser(headless=headless)
            await inst.start()
            _singleton = inst
        return _singleton


async def shutdown_browser() -> None:
    global _singleton
    async with _init_lock:
        if _singleton is not None:
            await _singleton.stop()
            _singleton = None


def get_browser() -> GeminiBrowser:
    if _singleton is None or not _singleton.ready:
        raise GeminiBrowserError("GeminiBrowser not initialized — call init_browser() first")
    return _singleton


def is_browser_ready() -> bool:
    return _singleton is not None and _singleton.ready
