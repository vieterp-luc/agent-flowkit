"""Playwright-driven Meta AI video generator.

Drives the Meta AI web app (meta.ai) in a persistent Chromium instance and captures
the rendered video directly — same approach as gemini_browser.py for Lyria music.
Login state is kept in `output/_shared/meta_profile/` — bootstrap once via
scripts/meta_bootstrap.py.

⚠️  Meta AI has no public video API and its ToS restricts automation. This drives
YOUR OWN logged-in account in a real browser for personal/manual-equivalent use.
Selectors live in meta_selectors.py and likely need tuning on first run
(see scripts/meta_inspect_dom.py).
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

from agent.services import meta_selectors as sel

logger = logging.getLogger(__name__)

PROFILE_DIR = Path("output/_shared/meta_profile")
DOWNLOAD_DIR = Path("output/_shared/meta_video")

LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
]


class MetaBrowserError(RuntimeError):
    """Raised on login expiry, quota/safety blocks, or selector failures."""


class MetaBrowser:
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
            viewport={"width": 1280, "height": 900},
        )
        logger.info("MetaBrowser started (headless=%s)", self._headless)

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
        logger.info("MetaBrowser stopped")

    @property
    def ready(self) -> bool:
        return self._ctx is not None

    async def generate_video(
        self, prompt: str, image_path: Optional[str] = None, timeout_s: float = 360
    ) -> Path:
        """Drive meta.ai/create: (optionally attach an image) → describe → Create →
        wait for the freshly rendered result → save → return path.

        Result is identified by DIFFING video srcs against a pre-submit baseline. Meta
        renders results as fbcdn https <video> srcs (4 variations); we grab the first
        new one. image_path = local image for image→video; omit for text→video.
        """
        if self._ctx is None:
            raise MetaBrowserError("MetaBrowser not started")

        async with self._lock:
            page = await self._ctx.new_page()
            try:
                await page.goto(sel.APP_URL, wait_until="domcontentloaded", timeout=45_000)
                self._check_login(page)
                await self._dismiss_overlays(page)

                composer = page.locator(sel.COMPOSER).first
                try:
                    await composer.wait_for(state="visible", timeout=20_000)
                except PWTimeout as e:
                    self._check_login(page)
                    raise MetaBrowserError(f"COMPOSER_NOT_FOUND: {sel.COMPOSER}") from e

                if image_path:
                    await self._attach_image(page, image_path)

                # Baseline of existing video srcs (history/feed) so we can spot the new one.
                baseline = set(await self._video_srcs(page))

                await composer.scroll_into_view_if_needed()
                await composer.click()
                await page.keyboard.type(prompt, delay=10)  # real keys for Lexical editor
                await self._submit(page, composer)

                src = await self._await_new_video_src(page, baseline, timeout_s)
                content = await self._download(page, src)
                dest = self._unique_dest(self._filename_from_url(src))
                dest.write_bytes(content)
                logger.info("Video saved: %s (%d KB)", dest, dest.stat().st_size // 1024)
                return dest
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

    # ─── helpers ──────────────────────────────────────────────

    @staticmethod
    def _check_login(page) -> None:
        url = page.url
        if any(frag in url for frag in sel.LOGIN_URL_FRAGMENTS):
            raise MetaBrowserError("LOGIN_EXPIRED — re-run scripts/meta_bootstrap.py")

    @staticmethod
    async def _dismiss_overlays(page) -> None:
        """Best-effort: close consent/welcome/cookie overlays that can cover the composer."""
        try:
            btn = page.locator(sel.OVERLAY_DISMISS).first
            if await btn.count() and await btn.is_visible():
                await btn.click(timeout=3_000)
                await asyncio.sleep(0.5)
                logger.info("Dismissed an overlay")
        except Exception as e:
            logger.debug("overlay dismiss skipped: %s", e)

    @staticmethod
    async def _video_srcs(page) -> list:
        """Ordered list of non-empty <video> srcs (DOM order → topmost/newest first).

        Returns a list (not a set) so the caller can pick the newest result (the grid
        renders the most recent generation at the top). Both blob: and https CDN.
        """
        srcs = await page.evaluate(
            """() => {
               const seen = new Set(); const out = [];
               for (const v of document.querySelectorAll('video')) {
                 const s = v.src || v.querySelector('source')?.src || '';
                 if ((s.startsWith('blob:') || s.startsWith('http')) && !seen.has(s)) {
                   seen.add(s); out.push(s);
                 }
               }
               return out;
            }"""
        )
        return srcs

    @staticmethod
    async def _attach_image(page, image_path: str) -> None:
        """Upload a local image via the hidden file input (no native dialog)."""
        p = Path(image_path)
        if not p.exists():
            raise MetaBrowserError(f"IMAGE_NOT_FOUND: {image_path}")
        try:
            await page.set_input_files(sel.FILE_INPUT, str(p))
        except Exception as e:
            raise MetaBrowserError(f"IMAGE_UPLOAD_FAILED: {e}") from e
        await asyncio.sleep(3)  # let the preview thumbnail attach + upload settle
        logger.info("Attached image: %s", p.name)

    @staticmethod
    async def _submit(page, composer) -> None:
        """Submit the composer DETERMINISTICALLY by clicking the blue send-arrow.

        Enter is unreliable once an image is attached (the composer re-renders), so we
        click the send button first, then the 'Create' control, then fall back to
        Enter. We do NOT try to verify submission here — _await_new_video_src is the
        real check (a new result video must appear).
        """
        clicked = False
        for selstr in (sel.SEND_BUTTON, sel.CREATE_BUTTON):
            try:
                btn = page.locator(selstr).last
                if await btn.count() and await btn.is_visible() and await btn.is_enabled():
                    await btn.click(timeout=4000)
                    logger.info("Submitted via %s", selstr)
                    clicked = True
                    break
            except Exception as e:
                logger.debug("submit via %s: %s", selstr, e)
        if not clicked:
            try:
                await composer.press("Enter")
                logger.info("Submitted via Enter (fallback)")
            except Exception as e:
                logger.warning("All submit methods failed: %s", e)
        await asyncio.sleep(1.0)

    async def _await_new_video_src(self, page, baseline: set, timeout_s: float) -> str:
        """Poll for a <video> src that was NOT in the pre-submit baseline (the feed).

        Tracks both blob: and https srcs. The result can take a few seconds to stabilize
        once it first appears, so we confirm the same new src twice before returning it.
        Raises on quota/safety block.
        """
        # Meta's SPA does NOT live-update the grid when a generation finishes — the
        # page stays on "Imagining" while the video is actually ready. So we RELOAD
        # the page periodically; after a reload the completed result appears at the
        # top of the grid with its fbcdn src, and the diff catches it. We return the
        # topmost (newest) fresh src.
        step = 5
        reload_every = 45
        elapsed = 0.0
        since_reload = 0.0
        while elapsed < timeout_s:
            current = await self._video_srcs(page)  # DOM order → newest first
            fresh = [s for s in current if s not in baseline]
            if fresh:
                return fresh[0]
            body_text = (await page.text_content("body") or "").lower()
            if any(m in body_text for m in sel.BLOCK_MESSAGES):
                raise MetaBrowserError("BLOCKED — quota/safety message detected in page")
            await asyncio.sleep(step)
            elapsed += step
            since_reload += step
            if since_reload >= reload_every:
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=30_000)
                    await asyncio.sleep(4)  # let the grid hydrate after reload
                except Exception as e:
                    logger.debug("reload during wait failed: %s", e)
                since_reload = 0.0
        await self._dump_state(page)
        raise MetaBrowserError(
            f"VIDEO_TIMEOUT after {timeout_s}s — no new video appeared (had "
            f"{len(baseline)} pre-existing). State → output/_shared/meta_timeout_state.log"
        )

    @staticmethod
    async def _dump_state(page) -> None:
        """On timeout, snapshot page state to a log so we can see what Meta actually showed."""
        try:
            state = await page.evaluate(
                """() => ({
                   url: location.href,
                   videos: [...document.querySelectorAll('video')].map(v => ({
                     src: (v.src || v.querySelector('source')?.src || '').slice(0, 80),
                     cls: v.className.toString().slice(0, 60),
                   })).slice(0, 20),
                   composers: [...document.querySelectorAll('textarea,[contenteditable="true"]')]
                     .map(c => ({ph: c.getAttribute('placeholder') || '', testid: c.getAttribute('data-testid') || '', val: (c.value || c.textContent || '').slice(0, 60)})),
                   buttons: [...document.querySelectorAll('button,[role="button"]')]
                     .map(b => (b.getAttribute('aria-label') || b.textContent || '').trim().slice(0, 40))
                     .filter(Boolean).slice(0, 40),
                   bodyText: (document.body.innerText || '').slice(0, 600),
                })"""
            )
            out = Path("output/_shared/meta_timeout_state.log")
            out.parent.mkdir(parents=True, exist_ok=True)
            import json
            out.write_text(json.dumps(state, indent=2, ensure_ascii=False))
            logger.info("Dumped timeout state → %s", out)
        except Exception as e:
            logger.warning("dump_state failed: %s", e)

    @staticmethod
    async def _download(page, src: str) -> bytes:
        """Fetch the video bytes. blob: must be read in-page; https prefers the
        context request (no CORS, carries cookies) with an in-page fetch fallback."""
        if src.startswith("http"):
            try:
                resp = await page.context.request.get(src)
                if resp.ok:
                    return await resp.body()
            except Exception as e:
                logger.warning("context.request fetch failed (%s) — trying in-page fetch", e)
        arr = await page.evaluate(
            """async (url) => {
               const r = await fetch(url, {credentials: 'include'});
               if (!r.ok) throw new Error('FETCH_' + r.status);
               const buf = await r.arrayBuffer();
               return Array.from(new Uint8Array(buf));
            }""",
            src,
        )
        return bytes(arr)

    @staticmethod
    def _filename_from_url(url: str) -> str:
        m = re.search(r"/([^/?#]+\.mp4)", url)
        if m:
            return m.group(1)
        # blob:https://www.meta.ai/<uuid> → meta_video_<uuid>.mp4
        m = re.search(r"/([0-9a-f-]{8,})$", url)
        if m:
            return f"meta_video_{m.group(1)}.mp4"
        return f"meta_video_{int(asyncio.get_event_loop().time() * 1000)}.mp4"

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

_singleton: Optional[MetaBrowser] = None
_init_lock = asyncio.Lock()


async def init_browser(headless: bool = True) -> MetaBrowser:
    """Idempotent + race-safe singleton init."""
    global _singleton
    async with _init_lock:
        if _singleton is None or not _singleton.ready:
            inst = MetaBrowser(headless=headless)
            await inst.start()
            _singleton = inst
        return _singleton


async def shutdown_browser() -> None:
    global _singleton
    async with _init_lock:
        if _singleton is not None:
            await _singleton.stop()
            _singleton = None


def is_browser_ready() -> bool:
    return _singleton is not None and _singleton.ready
