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
import uuid
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

        Result is identified by anchoring on a **unique fingerprint token** appended
        to the prompt. Meta's UI redisplays the submitted prompt next to each result;
        searching the DOM for our specific fingerprint then walking up to the nearest
        `<video>` reliably picks OUR generation (no false positives from gallery
        history / other projects sharing the same account). Falls back to baseline
        diff only as a last-resort if the fingerprint never materializes.
        image_path = local image for image→video; omit for text→video.
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

                # Unique fingerprint anchored to THIS gen — Meta echoes the prompt
                # text back in the UI next to each result, so we can locate our
                # specific video by DOM-walking from this token.
                fingerprint = f"[fk-{uuid.uuid4().hex[:6]}]"
                prompt_with_fp = f"{prompt} {fingerprint}"

                # Baselines captured BEFORE submit. Primary anchor = the new
                # /prompt/<id> link Meta mints per generation (unique, unambiguous);
                # video-src / fingerprint kept only as fallbacks.
                baseline_prompts = set(await self._prompt_hrefs(page))
                baseline = set(await self._video_srcs(page))

                await composer.scroll_into_view_if_needed()
                await composer.click()
                await page.keyboard.type(prompt_with_fp, delay=10)  # real keys for Lexical editor
                await self._submit(page, composer)

                src = await self._await_video_by_prompt(
                    page, baseline_prompts, fingerprint, baseline, timeout_s
                )
                content = await self._download(page, src)
                dest = self._unique_dest(self._filename_from_url(src))
                dest.write_bytes(content)
                logger.info(
                    "Video saved: %s (%d KB) [fp=%s]",
                    dest, dest.stat().st_size // 1024, fingerprint,
                )
                return dest
            finally:
                try:
                    await page.close()
                except Exception:
                    pass

    async def harvest(self, limit: int = 20) -> list:
        """Open recent /prompt/<id> pages and return {url, prompt text, video src} for
        each — lets the caller reclaim ALREADY-generated videos by matching the prompt
        text to a scene (no re-generation needed)."""
        if self._ctx is None:
            raise MetaBrowserError("MetaBrowser not started")
        async with self._lock:
            page = await self._ctx.new_page()
            try:
                await page.goto(sel.APP_URL, wait_until="domcontentloaded", timeout=45_000)
                self._check_login(page)
                await self._dismiss_overlays(page)
                await asyncio.sleep(2)
                hrefs = (await self._prompt_hrefs(page))[:limit]
                out = []
                for h in hrefs:
                    item = {"url": h, "src": "", "text": ""}
                    try:
                        await page.goto(h, wait_until="domcontentloaded", timeout=30_000)
                        for _ in range(3):
                            await asyncio.sleep(2)
                            srcs = await self._video_srcs(page)
                            if srcs:
                                item["src"] = srcs[0]
                                break
                            await page.reload(wait_until="domcontentloaded", timeout=30_000)
                        item["text"] = ((await page.text_content("body")) or "")[:6000]
                    except Exception as e:
                        item["error"] = str(e)
                    out.append(item)
                return out
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

    @staticmethod
    async def _prompt_hrefs(page) -> list:
        """Ordered list (DOM order → newest first) of /prompt/<id> links on the page.
        Each Meta generation gets a unique /prompt/<id> URL — the stable anchor."""
        return await page.evaluate(
            """() => {
               const seen = new Set(); const out = [];
               for (const a of document.querySelectorAll('a[href*="/prompt/"]')) {
                 const h = a.href;
                 if (h && !seen.has(h)) { seen.add(h); out.push(h); }
               }
               return out;
            }"""
        )

    async def _await_video_by_prompt(
        self, page, baseline_prompts: set, fingerprint: str, baseline_srcs: set, timeout_s: float
    ) -> str:
        """Capture OUR generation by its unique /prompt/<id> URL.

        Phase A: poll (with reload) for a NEW /prompt/<id> link not in the pre-submit
        baseline — the topmost new one is THIS generation. Phase B: open that prompt
        page (shows only our generation) and poll-reload until its <video> has a real
        src → that's unambiguously our video. Falls back to the fingerprint walker if
        no new prompt link ever appears.
        """
        step, reload_every = 5, 45
        elapsed = since_reload = 0.0
        prompt_url = None

        # ── Phase A: find our new prompt link ──
        while elapsed < timeout_s and not prompt_url:
            fresh = [h for h in (await self._prompt_hrefs(page)) if h not in baseline_prompts]
            if fresh:
                prompt_url = fresh[0]  # topmost (newest) = our generation
                logger.info("New prompt URL: %s", prompt_url)
                break
            body = (await page.text_content("body") or "").lower()
            if any(m in body for m in sel.BLOCK_MESSAGES):
                raise MetaBrowserError("BLOCKED — quota/safety message detected in page")
            await asyncio.sleep(step)
            elapsed += step
            since_reload += step
            if since_reload >= reload_every:
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=30_000)
                    await asyncio.sleep(4)
                except Exception as e:
                    logger.debug("reload (phase A) failed: %s", e)
                since_reload = 0.0

        if not prompt_url:
            logger.warning("No new /prompt link — falling back to fingerprint walker")
            return await self._await_video_by_fingerprint(
                page, fingerprint, baseline_srcs, max(30.0, timeout_s - elapsed)
            )

        # ── Phase B: open the prompt page, wait for ITS video to render ──
        try:
            await page.goto(prompt_url, wait_until="domcontentloaded", timeout=30_000)
            await asyncio.sleep(3)
        except Exception as e:
            logger.debug("goto prompt page failed: %s", e)
        since_reload = 0.0
        while elapsed < timeout_s:
            srcs = await self._video_srcs(page)  # this page = only our generation
            if srcs:
                logger.info("Prompt-page video → %s…", srcs[0][:64])
                return srcs[0]
            raw = (await page.text_content("body")) or ""
            low = raw.lower()
            # Meta chat error ("couldn't animate that scene…") → fail fast WITH the
            # message so the caller knows to change the motion prompt / image.
            hit = next((m for m in sel.CHAT_ERROR_MESSAGES if m in low), None)
            if hit:
                i = low.find(hit)
                snip = " ".join(raw[max(0, i - 50): i + 170].split())
                raise MetaBrowserError(f"META_CHAT_ERROR: {snip}")
            if any(m in low for m in sel.BLOCK_MESSAGES):
                raise MetaBrowserError("BLOCKED — quota/safety message detected in page")
            await asyncio.sleep(step)
            elapsed += step
            since_reload += step
            if since_reload >= reload_every:
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=30_000)
                    await asyncio.sleep(4)
                except Exception as e:
                    logger.debug("reload (phase B) failed: %s", e)
                since_reload = 0.0
        await self._dump_state(page)
        raise MetaBrowserError(
            f"VIDEO_TIMEOUT after {timeout_s}s — prompt page {prompt_url} had no video. "
            "State → output/_shared/meta_timeout_state.log"
        )

    async def _await_video_by_fingerprint(
        self, page, fingerprint: str, baseline: set, timeout_s: float
    ) -> str:
        """Poll for OUR result anchored by `fingerprint` text in the DOM.

        Strategy:
          1. PRIMARY — find the text node containing `fingerprint` (Meta echoes the
             submitted prompt back beside each result), walk up to the nearest
             ancestor that contains a <video>, return that src.
          2. FALLBACK — if the fingerprint never appears after `fingerprint_grace`
             seconds AND a new baseline-diff src exists, return that (legacy
             behavior, only triggers when Meta did NOT echo the prompt).

        Meta's SPA does NOT live-update the grid when a generation finishes — the
        page stays on "Imagining" while the result is actually ready. So we reload
        every `reload_every` seconds; the result then renders in the grid.
        """
        step = 5
        reload_every = 45
        # Fallback after this many seconds — short enough to recover quickly on
        # accounts where Meta doesn't echo prompt text in the UI (so fingerprint
        # anchor never appears), long enough to give the prompt a chance to
        # render on accounts that do echo it.
        fingerprint_grace = 30
        elapsed = 0.0
        since_reload = 0.0
        baseline_list = list(baseline)
        # Meta sometimes responds with a chat-style error instead of a video.
        # When that happens our fingerprint is still found in DOM but no video
        # lives in the result block; without explicit detection the walker would
        # climb out of scope and grab an unrelated stale clip from history.
        meta_error_patterns = [
            r"oops!?\s*something went wrong",
            r"would you like me to try",
            r"unable to (?:animate|generate)",
            r"i (?:had|ran into) trouble",
            r"let me try again",
            r"can'?t (?:animate|generate|create) that",
            r"couldn'?t (?:animate|generate|create)",
        ]
        while elapsed < timeout_s:
            # PRIMARY: locate by fingerprint anchor AND require the video be NEW
            # (not in pre-submit baseline). Walker depth limited to 5 ancestors so
            # we stay strictly inside the result block belonging to OUR prompt —
            # any farther up and we'd reach a shared parent and could pick up a
            # neighboring block's video by accident.
            try:
                result = await page.evaluate(
                    """({fp, baseline, errPatterns}) => {
                       const blSet = new Set(baseline);
                       const reList = errPatterns.map(p => new RegExp(p, 'i'));
                       const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                       let tn;
                       while ((tn = tw.nextNode())) {
                         if (!tn.textContent.includes(fp)) continue;
                         let cur = tn.parentElement;
                         for (let i = 0; i < 5 && cur; i++) {
                           const txt = cur.textContent || '';
                           if (reList.some(re => re.test(txt))) {
                             return {error: 'meta_chat_error', text: txt.slice(0, 200)};
                           }
                           const vids = cur.querySelectorAll ? cur.querySelectorAll('video') : [];
                           for (const vid of vids) {
                             const s = vid.src
                               || (vid.querySelector('source') && vid.querySelector('source').src)
                               || '';
                             if ((s.startsWith('blob:') || s.startsWith('http')) && !blSet.has(s)) {
                               return {src: s};
                             }
                           }
                           cur = cur.parentElement;
                         }
                       }
                       return null;
                    }""",
                    {
                        "fp": fingerprint,
                        "baseline": baseline_list,
                        "errPatterns": meta_error_patterns,
                    },
                )
            except Exception as e:
                logger.debug("fingerprint eval failed: %s", e)
                result = None
            if isinstance(result, dict):
                if result.get("error") == "meta_chat_error":
                    snippet = (result.get("text") or "").strip()
                    raise MetaBrowserError(
                        f"META_CHAT_ERROR: {snippet[:160]} [fp={fingerprint}]"
                    )
                src = result.get("src")
                if src:
                    logger.info("Fingerprint hit (%s) → %s…", fingerprint, src[:64])
                    return src

            # FALLBACK: only after grace period, if fingerprint never showed up
            if elapsed >= fingerprint_grace:
                fresh = [s for s in (await self._video_srcs(page)) if s not in baseline]
                if fresh:
                    logger.warning(
                        "Fingerprint %s not echoed by Meta — falling back to "
                        "baseline-diff (returning topmost new src)", fingerprint,
                    )
                    return fresh[0]

            # Quota / safety block check
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
            f"VIDEO_TIMEOUT after {timeout_s}s — fingerprint {fingerprint} never "
            f"resolved (had {len(baseline)} pre-existing). "
            "State → output/_shared/meta_timeout_state.log"
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
