"""Smoke test for GeminiBrowser music generation.

Runs end-to-end: launch context → generate → save file → print path.
Requires bootstrap done first (scripts/gemini_bootstrap.py).

Usage:
    python scripts/gemini_test_gen.py "lo-fi cafe music, warm piano"
    python scripts/gemini_test_gen.py "..." --headed
"""
import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.services.gemini_browser import GeminiBrowser, GeminiBrowserError


async def main(prompt: str, headless: bool, timeout: float, model: str) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    browser = GeminiBrowser(headless=headless)
    await browser.start()
    try:
        t0 = time.time()
        path = await browser.generate_music(prompt, timeout_s=timeout, model=model)
        elapsed = time.time() - t0
        size_kb = path.stat().st_size // 1024
        print(f"\n✓ OK in {elapsed:.1f}s — {path} ({size_kb} KB)")
        return 0
    except GeminiBrowserError as e:
        print(f"\n✗ FAIL — {e}", file=sys.stderr)
        return 1
    finally:
        await browser.stop()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("prompt", help="Music prompt")
    p.add_argument("--headed", action="store_true", help="Show Chromium window (debug)")
    p.add_argument("--timeout", type=float, default=300, help="Audio render timeout (s)")
    p.add_argument("--model", default="Pro", help="Gemini model: Pro | Nhanh | Tư duy")
    args = p.parse_args()
    sys.exit(asyncio.run(main(args.prompt, headless=not args.headed, timeout=args.timeout, model=args.model)))
