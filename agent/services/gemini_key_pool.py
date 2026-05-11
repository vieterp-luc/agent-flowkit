"""Multi-key rotation pool for Gemini REST API.

Bypasses per-key free-tier rate limits by rotating through N keys.
Tracks cooldowns (per-minute 429) and daily exhaustion (per-day quota).
In-memory only — resets on server restart.
"""
import asyncio
import json
import logging
import threading
import time
from typing import Optional

import aiohttp
import requests

from agent.config import GEMINI_API_KEYS

logger = logging.getLogger(__name__)


GEMINI_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)
DEFAULT_MODEL = "gemini-2.5-flash"
COOLDOWN_DEFAULT = 60.0  # seconds, used when 429 has no Retry-After header
MAX_ATTEMPTS_FACTOR = 2  # try each key up to N times in one call


class GeminiKeyPool:
    """Thread-safe key rotator with cooldown tracking."""

    def __init__(self, keys: list[str]):
        if not keys:
            raise RuntimeError(
                "No Gemini keys configured. Set GEMINI_API_KEYS=k1,k2,k3 in .env"
            )
        self.keys = keys
        self.cooldowns: dict[str, float] = {}  # key → unix ts when unblocked
        self.daily_exhausted: set[str] = set()
        self._lock = threading.Lock()
        self._idx = 0  # round-robin start position
        logger.info("Gemini key pool initialized with %d keys", len(keys))

    def _key_label(self, key: str) -> str:
        """Last 6 chars for log identification (don't leak full key)."""
        return f"...{key[-6:]}" if len(key) > 6 else key

    def _is_available(self, key: str, now: float) -> bool:
        if key in self.daily_exhausted:
            return False
        cd = self.cooldowns.get(key, 0)
        return cd <= now

    def acquire(self) -> Optional[str]:
        """Return next available key (round-robin). None if all blocked."""
        with self._lock:
            now = time.time()
            n = len(self.keys)
            for offset in range(n):
                idx = (self._idx + offset) % n
                key = self.keys[idx]
                if self._is_available(key, now):
                    self._idx = (idx + 1) % n  # advance for next caller
                    return key
            return None

    def shortest_wait(self) -> float:
        """Seconds until any key recovers. 0 if some available, math.inf if all daily-exhausted."""
        with self._lock:
            now = time.time()
            available_cooldowns = [
                self.cooldowns.get(k, 0)
                for k in self.keys
                if k not in self.daily_exhausted
            ]
            if not available_cooldowns:
                return float("inf")
            future = [cd - now for cd in available_cooldowns if cd > now]
            return min(future) if future else 0

    def mark_429(self, key: str, retry_after: float = COOLDOWN_DEFAULT) -> None:
        with self._lock:
            self.cooldowns[key] = time.time() + max(retry_after, 5.0)
            logger.warning(
                "Key %s 429, cooldown %.0fs", self._key_label(key), retry_after
            )

    def mark_daily(self, key: str) -> None:
        with self._lock:
            self.daily_exhausted.add(key)
            logger.warning(
                "Key %s daily quota exhausted", self._key_label(key)
            )

    def report_success(self, key: str) -> None:
        # No-op (could track success count for stats)
        pass


# ─── Singleton ─────────────────────────────────────────────────

_pool_instance: Optional[GeminiKeyPool] = None


def get_pool() -> GeminiKeyPool:
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = GeminiKeyPool(GEMINI_API_KEYS)
    return _pool_instance


# ─── HTTP helpers (sync + async) ───────────────────────────────


def _classify_error(status: int, body: str) -> str:
    """Categorize HTTP error: 'cooldown' | 'daily' | 'transient' | 'fatal'."""
    if status == 429:
        # Could be RPM (per-minute) or RPD (per-day)
        if "RequestsPerDayPerProjectPerModel" in body or "free_tier_requests" in body and "Day" in body:
            return "daily"
        return "cooldown"
    if status == 403 and "quota" in body.lower():
        return "daily"
    if status in (500, 502, 503, 504):
        return "transient"
    return "fatal"


def _parse_retry_after(headers: dict, body: str) -> float:
    """Extract retry-after from headers or response body."""
    # HTTP header
    ra = headers.get("Retry-After") or headers.get("retry-after")
    if ra:
        try:
            return float(ra)
        except ValueError:
            pass
    # Body has e.g. "Please retry in 38.275816085s."
    import re
    m = re.search(r"retry in ([\d.]+)s", body)
    if m:
        return float(m.group(1))
    return COOLDOWN_DEFAULT


def call_gemini_sync(payload: dict, model: str = DEFAULT_MODEL,
                     timeout: int = 120) -> dict:
    """Sync POST to Gemini with key rotation. Raises if all keys exhausted."""
    pool = get_pool()
    max_attempts = len(pool.keys) * MAX_ATTEMPTS_FACTOR
    last_err: Optional[Exception] = None

    for attempt in range(max_attempts):
        key = pool.acquire()
        if key is None:
            wait = pool.shortest_wait()
            if wait == float("inf"):
                raise RuntimeError("All Gemini keys daily-exhausted")
            sleep_s = min(wait, 30.0)
            logger.info("All keys cooling, sleep %.0fs", sleep_s)
            time.sleep(max(sleep_s, 1.0))
            continue

        url = GEMINI_URL_TEMPLATE.format(model=model, key=key)
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            body = r.text[:1000]
            if r.status_code == 200:
                pool.report_success(key)
                return r.json()
            cls = _classify_error(r.status_code, body)
            if cls == "cooldown":
                pool.mark_429(key, _parse_retry_after(dict(r.headers), body))
                continue
            if cls == "daily":
                pool.mark_daily(key)
                continue
            if cls == "transient":
                last_err = RuntimeError(f"Gemini {r.status_code}: {body[:200]}")
                time.sleep(5)
                continue
            # fatal
            r.raise_for_status()
        except requests.exceptions.Timeout as e:
            last_err = e
            time.sleep(3)
            continue
        except requests.exceptions.RequestException as e:
            last_err = e
            time.sleep(3)
            continue

    raise last_err or RuntimeError("Gemini call failed after retries")


async def call_gemini_async(payload: dict, model: str = DEFAULT_MODEL,
                            timeout: int = 120) -> dict:
    """Async POST to Gemini with key rotation."""
    pool = get_pool()
    max_attempts = len(pool.keys) * MAX_ATTEMPTS_FACTOR
    last_err: Optional[Exception] = None

    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
        for attempt in range(max_attempts):
            key = pool.acquire()
            if key is None:
                wait = pool.shortest_wait()
                if wait == float("inf"):
                    raise RuntimeError("All Gemini keys daily-exhausted")
                sleep_s = min(wait, 30.0)
                logger.info("All keys cooling, sleep %.0fs", sleep_s)
                await asyncio.sleep(max(sleep_s, 1.0))
                continue

            url = GEMINI_URL_TEMPLATE.format(model=model, key=key)
            try:
                async with session.post(url, json=payload) as resp:
                    body = (await resp.text())[:1000]
                    if resp.status == 200:
                        pool.report_success(key)
                        return json.loads(body) if len(body) < 1000 else await resp.json()
                    cls = _classify_error(resp.status, body)
                    if cls == "cooldown":
                        pool.mark_429(key, _parse_retry_after(dict(resp.headers), body))
                        continue
                    if cls == "daily":
                        pool.mark_daily(key)
                        continue
                    if cls == "transient":
                        last_err = RuntimeError(f"Gemini {resp.status}: {body[:200]}")
                        await asyncio.sleep(5)
                        continue
                    raise RuntimeError(f"Gemini fatal {resp.status}: {body[:300]}")
            except asyncio.TimeoutError as e:
                last_err = e
                await asyncio.sleep(3)
                continue
            except aiohttp.ClientError as e:
                last_err = e
                await asyncio.sleep(3)
                continue

    raise last_err or RuntimeError("Gemini call failed after retries")
