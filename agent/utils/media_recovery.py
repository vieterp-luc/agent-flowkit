import aiohttp
import base64
import logging
import re
import time
from pathlib import Path

from agent.db import crud
from agent.services.flow_client import get_flow_client
from agent.utils.slugify import slugify
from agent.utils.paths import project_dir, scene_img_path, scene_video_path

logger = logging.getLogger(__name__)

def is_url_expired(url: str) -> bool:
    """Check if a GCS signed URL is expired or close to expiration (<60s)."""
    if not url or "Expires=" not in url:
        return False
    m = re.search(r'Expires=(\d+)', url)
    if m:
        # Buffer 60 seconds
        return int(m.group(1)) < time.time() + 60
    return False

def get_local_path(req_type: str, project_slug: str, scene_or_char: dict) -> Path | None:
    if not scene_or_char:
        return None
    if req_type in ("GENERATE_IMAGE", "REGENERATE_IMAGE", "EDIT_IMAGE"):
        return scene_img_path(project_slug, scene_or_char["id"])
    elif req_type in ("GENERATE_VIDEO", "REGENERATE_VIDEO", "GENERATE_VIDEO_REFS"):
        return scene_video_path(project_slug, scene_or_char["id"])
    elif req_type in ("UPSCALE_VIDEO",):
        return scene_video_path(project_slug, scene_or_char["id"], subdir="4k")
    elif req_type in ("GENERATE_CHARACTER_IMAGE", "REGENERATE_CHARACTER_IMAGE", "EDIT_CHARACTER_IMAGE"):
        return project_dir(project_slug) / "assets" / f"{scene_or_char['id']}.jpg"
    return None

async def download_media_to_local(url: str, project_slug: str, req_type: str, scene_or_char: dict):
    if not url or not url.startswith("http"):
        return
    path = get_local_path(req_type, project_slug, scene_or_char)
    if not path:
        return
    
    # Don't download if it already exists
    if path.exists():
        return
        
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    path.write_bytes(await resp.read())
                    logger.info("Saved local media: %s", path)
    except Exception as e:
        logger.warning("Failed to save local media %s: %s", url[:60], e)

async def check_and_recover_media(media_id: str, url: str, project_id: str, local_path: Path | None, auto_reupload: bool = True) -> tuple[bool, str | None]:
    """Returns (is_available, optional_error_message).
    Recovery order:
      1. Fresh signed URL via get_media (data.fifeUrl / data.servingUri) — images mostly
      2. encodedVideo/encodedImage in get_media response — save to local backup
      3. Existing local backup file
      4. Re-upload local backup to get new media_id (only if auto_reupload=True)
    Returns (True, None) on signed URL refresh or encoded recovery,
            (True, "LOCAL") when only local backup is usable,
            (True, "RECOVERED:<new_mid>") when re-uploaded,
            (False, "<reason>") otherwise."""
    if not media_id:
        return False, "No media_id provided"

    if not is_url_expired(url):
        return True, None

    client = get_flow_client()
    logger.info("Media URL expired for %s, trying to refresh via get_media", media_id[:12])

    # 1. Try to refresh via get_media — handles both fresh URL and encoded inline content
    try:
        res = await client.get_media(media_id)
        if isinstance(res, dict) and not res.get("error") and res.get("status") == 200:
            data = res.get("data", {})

            # 1a. Fresh signed URL (typical for images)
            fresh_url = data.get("fifeUrl") or data.get("servingUri")
            if fresh_url:
                media_type = "image"
                if local_path and local_path.suffix == ".mp4":
                    media_type = "video"
                await client._refresh_media_urls([{"mediaId": media_id, "mediaType": media_type, "url": fresh_url}])
                logger.info("Successfully refreshed media URL for %s", media_id[:12])
                return True, None

            # 1b. Encoded inline content (typical for videos — `{"video":{"encodedVideo":"..."}}`)
            encoded = (data.get("video") or {}).get("encodedVideo") \
                   or (data.get("image") or {}).get("encodedImage")
            if encoded and local_path:
                try:
                    content = base64.b64decode(encoded)
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    local_path.write_bytes(content)
                    logger.info("Recovered media %s from encodedVideo (%d bytes) → %s",
                                media_id[:12], len(content), local_path)
                    return True, "LOCAL"
                except Exception as e:
                    logger.warning("Failed to decode encoded content for %s: %s", media_id[:12], e)
    except Exception as e:
        logger.warning("Refresh get_media failed for %s: %s", media_id[:12], e)

    # 2. Local backup file already exists — usable without re-upload
    if local_path and local_path.exists() and not auto_reupload:
        logger.info("Using existing local backup for %s: %s", media_id[:12], local_path)
        return True, "LOCAL"

    # 3. Re-upload local backup to get a new media_id (requires auto_reupload=True)
    if local_path and local_path.exists():
        logger.info("Google deleted media %s, re-uploading from local %s", media_id[:12], local_path)
        try:
            image_bytes = local_path.read_bytes()
            image_b64 = base64.b64encode(image_bytes).decode()
            mime = "video/mp4" if local_path.suffix == ".mp4" else "image/jpeg"
            result = await client.upload_image(image_b64, mime_type=mime, project_id=project_id, file_name=local_path.name)
            new_mid = result.get("_mediaId")
            if new_mid:
                # Update DB
                # Note: We return a special string and let processor update the correct DB fields
                return True, f"RECOVERED:{new_mid}"
            else:
                err_msg = result.get("error") or result.get("status") or result
                logger.error("Failed to re-upload local media %s. Flow result: %s", local_path, err_msg)
                return False, f"Upload API failed: {err_msg}"
        except Exception as e:
            logger.error("Failed to re-upload local media %s: %s", local_path, e)
            return False, f"Failed to re-upload local media: {e}"
            
    return False, "Media URL expired, entity not found on Google, and no local backup available"
