"""
Skill executor — parses skill markdown files and executes them by calling
the agent's own FastAPI endpoints directly.

Intercepts /fk:* commands from chat messages, reads skills/fk-<name>.md,
and runs the equivalent Python logic (no curl, no subprocess).
"""
import asyncio
import base64
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any

import httpx

from agent.config import API_HOST, API_PORT

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"
LOCAL_BASE = f"http://{API_HOST}:{API_PORT}"


class SkillError(Exception):
    """Skill execution failed."""
    pass


# ─── API client (shared) ────────────────────────────────────────────────────

_client: httpx.AsyncClient | None = None


async def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=60.0)
    return _client


async def api_get(path: str) -> Any:
    """GET /api/<path>"""
    client = await _get_client()
    r = await client.get(f"{LOCAL_BASE}{path}")
    r.raise_for_status()
    return r.json()


async def api_post(path: str, data: dict | list) -> Any:
    """POST /api/<path> with JSON body"""
    client = await _get_client()
    r = await client.post(f"{LOCAL_BASE}{path}", json=data)
    r.raise_for_status()
    return r.json()


async def api_patch(path: str, data: dict) -> Any:
    """PATCH /api/<path> with JSON body"""
    client = await _get_client()
    r = await client.patch(f"{LOCAL_BASE}{path}", json=data)
    r.raise_for_status()
    return r.json()


async def api_health() -> dict:
    """GET /health"""
    client = await _get_client()
    r = await client.get(f"{LOCAL_BASE}/health")
    r.raise_for_status()
    return r.json()


# ─── Output helpers ─────────────────────────────────────────────────────────

def _read_meta(path_str: str) -> dict:
    """Read a meta.json file from the output directory."""
    p = Path(__file__).parent.parent.parent / path_str
    if not p.exists():
        raise SkillError(f"File not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _read_output_dir(pid: str) -> dict:
    """Get output dir for project."""
    resp = asyncio.run(api_get(f"/api/projects/{pid}/output-dir"))
    meta = _read_meta(resp["path"] + "/meta.json")
    return resp["path"], meta


# ─── Download helpers ────────────────────────────────────────────────────────

def _download_url_to_path(url: str, dest: Path) -> bool:
    """Download a URL to a local path. Returns True on success."""
    if not url or url.startswith("gs://") or not url.startswith("http"):
        return False
    try:
        import urllib.request
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        logger.warning("Failed to download %s → %s: %s", url[:80], dest, e)
        return False


async def _download_scene_media(pid: str, scenes: list[dict], media_type: str,
                                ori: str, out_dir: Path) -> None:
    """Download scene media (img or 4k) to output dir."""
    if not scenes:
        return

    prefix = ori.lower()

    if media_type == "img":
        url_field = f"{prefix}_image_url"
        def path_fn(s: dict) -> Path:
            return out_dir / "img" / f"scene_{s.get('display_order', 0):03d}_{s['id']}.jpg"
    else:
        url_field = f"{prefix}_video_url"
        upscale_field = f"{prefix}_upscale_url"
        def path_fn(s: dict) -> Path:
            return out_dir / "4k" / f"scene_{s.get('display_order', 0):03d}_{s['id']}.mp4"

    downloaded = 0
    for scene in scenes:
        url = scene.get(upscale_field if media_type == "4k" and scene.get(upscale_field) else url_field, "")
        dest = path_fn(scene)
        if not url or dest.exists():
            continue
        if _download_url_to_path(url, dest):
            downloaded += 1
            logger.info("Downloaded %s: %s", media_type, dest.name)

    if downloaded:
        logger.info("Downloaded %d %s files for project %s", downloaded, media_type, pid[:12])


# ─── Polling ────────────────────────────────────────────────────────────────

async def poll_batch_status(
    video_id: str,
    req_type: str,
    interval: float = 5.0,
    timeout: float = 600.0,
) -> dict:
    """Poll /api/requests/batch-status until done=true."""
    import time
    elapsed = 0.0
    while elapsed < timeout:
        result = await api_get(f"/api/requests/batch-status?video_id={video_id}&type={req_type}")
        if result.get("done"):
            return result
        await asyncio.sleep(interval)
        elapsed += interval
    raise SkillError(f"Timeout ({timeout}s) waiting for {req_type} to complete")


# ─── Bash command parser & executor ────────────────────────────────────────

# Patterns found in skill bash blocks:
# curl -s http://127.0.0.1:8100/api/...              → GET
# curl -X POST http://127.0.0.1:8100/api/...         → POST
# curl -X PATCH http://127.0.0.1:8100/api/...        → PATCH
# curl -L -o <file> <url>                             → download
# curl ... -d '{...}'                                  → body JSON
# ffprobe ... | ...                                   → subprocess
# ffmpeg ... | ...                                   → subprocess
# echo "$VAR" | python3 -c "..."                    → python eval


def _extract_api_path(url: str) -> str | None:
    """Extract /api/... path from a curl URL."""
    m = re.search(r'http://[^/]+(/api/[^\s\'"]+)', url)
    if m:
        return m.group(1)
    m = re.search(r'https://[^/]+(/api/[^\s\'"]+)', url)
    if m:
        return m.group(1)
    return None


def _sub_vars(text: str, ctx: dict) -> str:
    """Substitute <VAR>, ${VAR}, $VAR, ${!VAR} patterns."""
    result = text

    # <VAR> style (angle brackets from skill placeholders)
    def replace_angle(m):
        name = m.group(1)
        return str(ctx.get(name, m.group(0)))

    # ${!VAR} indirect reference
    def replace_indirect(m):
        name = m.group(1)
        val = ctx.get(name, "")
        return str(ctx.get(val, ""))

    result = re.sub(r'<(\w+)>', replace_angle, result)
    result = re.sub(r'\$\{!(\w+)\}', replace_indirect, result)

    # ${VAR} and $VAR
    def replace_dollar(m):
        full = m.group(0)
        if full.startswith('${{'):
            return full  # literal ${{
        name = m.group(1) if m.group(1) else m.group(2)
        return str(ctx.get(name, full))

    result = re.sub(r'\$\{(\w+)\}', replace_dollar, result)
    result = re.sub(r'\$(\w+)\b', replace_dollar, result)
    return result


def _extract_json_body(cmd: str) -> str | None:
    """Extract JSON from curl -d argument."""
    m = re.search(r"-d\s+'({.*?})'", cmd, re.DOTALL)
    if m:
        return m.group(1)
    m = re.search(r'-d\s+"({.*?})"', cmd, re.DOTALL)
    if m:
        return m.group(1)
    m = re.search(r'-d\s+({.*})', cmd, re.DOTALL)
    if m:
        return m.group(1)
    return None


def _parse_python_eval(cmd: str) -> tuple[str, str] | None:
    """Detect 'echo $VAR | python3 -c \"...\"' pattern. Returns (var_name, python_code)."""
    m = re.search(
        r'echo\s+\$?(\w+)\s+\|\s+python3\s+-c\s+"((?:[^"\\]|\\.)*)"',
        cmd,
    )
    if m:
        return m.group(1), m.group(2)
    # Also handle: echo "$PROJ_OUT" | python3 -c "..."
    m = re.search(
        r'echo\s+"\$\{?(\w+)\}?"\s+\|\s+python3\s+-c\s+"((?:[^"\\]|\\.)*)"',
        cmd,
    )
    if m:
        return m.group(1), m.group(2)
    return None


async def _exec_bash(cmd: str, ctx: dict) -> tuple[str, dict]:
    """Execute a bash command as subprocess, return (stdout, updated_ctx)."""
    # First, substitute variables
    cmd_sub = _sub_vars(cmd, ctx)

    # ── API calls ────────────────────────────────────────────────────────────

    if "curl" in cmd_sub and ("-X POST" in cmd_sub or '"POST' in cmd_sub or "'POST" in cmd_sub):
        path = _extract_api_path(cmd_sub)
        if path:
            body_str = _extract_json_body(cmd_sub)
            if body_str:
                body_str = _sub_vars(body_str, ctx)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    body = body_str
                result = await api_post(path, body)
                ctx = {**ctx, "_last": result}
                return "", ctx

    if "curl" in cmd_sub and ("-X PATCH" in cmd_sub or '"PATCH' in cmd_sub):
        path = _extract_api_path(cmd_sub)
        if path:
            body_str = _extract_json_body(cmd_sub)
            if body_str:
                body_str = _sub_vars(body_str, ctx)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    body = body_str
                result = await api_patch(path, body)
                ctx = {**ctx, "_last": result}
                return "", ctx

    if "curl" in cmd_sub and "-X POST" not in cmd_sub and "-X PATCH" not in cmd_sub:
        path = _extract_api_path(cmd_sub)
        if path:
            result = await api_get(path)
            ctx = {**ctx, "_last": result}
            return "", ctx

    # ── Python eval (echo $VAR | python3 -c "...") ─────────────────────────
    py_parse = _parse_python_eval(cmd_sub)
    if py_parse:
        var_name, py_code = py_parse
        source_var = cmd_sub.split("echo")[1].split("|")[0].strip().lstrip("$")
        if source_var.startswith("{") and source_var.endswith("}"):
            source_var = source_var[1:-1]
        source_val = ctx.get(source_var, ctx.get("_last", ""))
        if isinstance(source_val, dict):
            source_text = json.dumps(source_val)
        elif isinstance(source_val, str):
            source_text = source_val
        else:
            source_text = str(source_val)

        # Build a safe namespace for the eval
        try:
            parsed = json.loads(source_text)
        except Exception:
            parsed = source_text

        ns = {"sys": None, "json": json, "sys": __import__("sys")}
        try:
            out = eval(py_code.replace("\\\"", '"'), {"json": json, "sys": __import__("sys")}, {})
        except Exception as e:
            out = str(e)

        ctx = {**ctx, var_name: str(out).strip()}
        return "", ctx

    # ── cat meta.json ──────────────────────────────────────────────────────
    cat_match = re.search(r'cat\s+\$\{?(\w+)\}?/meta\.json', cmd_sub)
    if cat_match:
        dir_var = cat_match.group(1)
        dir_path = ctx.get(dir_var, "")
        if dir_path:
            meta_path = Path(__file__).parent.parent.parent / dir_path / "meta.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                ctx = {**ctx, "META": meta}
                return "", ctx

    # ── Download with curl -L -o ───────────────────────────────────────────
    dl_match = re.search(r'curl\s+(-L\s+)?-o\s+"([^"]+)"\s+"([^"]+)"', cmd_sub)
    if dl_match:
        output_path = Path(dl_match.group(2))
        url = _sub_vars(dl_match.group(3), ctx)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        client = await _get_client()
        r = await client.get(url)
        r.raise_for_status()
        output_path.write_bytes(r.content)
        return "", ctx

    # ── Local commands (ffmpeg, mkdir, ls, etc.) ────────────────────────────
    if any(kw in cmd_sub for kw in ["ffmpeg", "ffprobe", "mkdir", "cp ", "ls ", "echo "]):
        # Filter out the python heredoc style things we handle above
        if "python3" in cmd_sub and "| python3" in cmd_sub:
            return "", ctx  # handled above

        proc = await asyncio.create_subprocess_shell(
            cmd_sub,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        out = stdout.decode() if stdout else ""
        err = stderr.decode() if stderr else ""
        ctx = {**ctx, "_last": out, "_stderr": err}
        return out + ("\n[stderr]: " + err if err else ""), ctx

    return "", ctx


# ─── Output formatter ───────────────────────────────────────────────────────

def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_(no data)_"
    col_widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    lines = []
    lines.append(" | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)))
    lines.append("-|".join("-" * w for w in col_widths))
    for row in rows:
        lines.append(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))
    return "\n".join(lines)


# ─── Skill-specific handlers ─────────────────────────────────────────────────
# These handle complex multi-step skills that need custom Python logic.

async def _handle_status(ctx: dict, args: str) -> str:
    """Implement /fk-status"""
    parts = args.strip().split()
    pid = parts[0] if parts else None

    if not pid:
        # List all projects
        projects = await api_get("/api/projects")
        rows = []
        for p in projects:
            tier = p.get("user_paygate_tier", "?").replace("PAYGATE_TIER_", "")
            rows.append([p["id"][:12], p.get("name", "?"), tier, p.get("status", "?")])
        return _format_table(["ID", "Name", "Tier", "Status"], rows)

    # Full dashboard
    health = await api_health()
    project = await api_get(f"/api/projects/{pid}")
    characters = await api_get(f"/api/projects/{pid}/characters")
    videos_resp = await api_get(f"/api/videos?project_id={pid}")
    videos = videos_resp if isinstance(videos_resp, list) else [videos_resp]
    pending_reqs = await api_get("/api/requests/pending")

    out = [f"**{project.get('name', '?')}** dashboard"]
    out.append(f"- Extension: {'OK' if health.get('extension_connected') else 'OFFLINE'}")
    out.append(f"- Tier: {project.get('user_paygate_tier', '?').replace('PAYGATE_TIER_', '')}")

    # Entities table
    char_rows = []
    for c in characters:
        mid = c.get("media_id", "")
        ready = "✓" if mid and mid.startswith("xxxxxxxx-xxxx-xxxx-xxxx-") else "✗"
        char_rows.append([c.get("name", "?"), c.get("entity_type", "?"), mid[:12] if mid else "-", ready])
    if char_rows:
        out.append("\n**Entities:**")
        out.append(_format_table(["Name", "Type", "media_id", "Ready"], char_rows))

    # Videos & scenes
    for video in videos:
        vid = video["id"]
        ori = video.get("orientation") or "HORIZONTAL"
        out.append(f"\n**Video:** `{vid[:12]}` ({video.get('title', '?')}) — {ori}")
        scenes = await api_get(f"/api/scenes?video_id={vid}")
        scene_rows = []
        for s in sorted(scenes, key=lambda x: x.get("display_order", 0)):
            prefix = ori.lower()
            img = s.get(f"{prefix}_image_status", "?").replace("COMPLETED", "✓").replace("PENDING", "○").replace("PROCESSING", "◐").replace("FAILED", "✗")
            vid_s = s.get(f"{prefix}_video_status", "?").replace("COMPLETED", "✓").replace("PENDING", "○").replace("PROCESSING", "◐").replace("FAILED", "✗")
            up_s = s.get(f"{prefix}_upscale_status", "?").replace("COMPLETED", "✓").replace("PENDING", "○").replace("PROCESSING", "◐").replace("FAILED", "✗")
            prompt = (s.get("prompt", "") or s.get("transition_prompt", "") or "")[:50]
            scene_rows.append([str(s.get("display_order", 0)), prompt, img, vid_s, up_s])
        out.append(_format_table(["#", "Prompt (50)", f"Img({ori[:4]})", f"Vid({ori[:4]})", "4K"], scene_rows))

    # Pending
    if pending_reqs:
        out.append(f"\n**Pending requests:** {len(pending_reqs)}")
        for r in pending_reqs[:10]:
            out.append(f"  - {r.get('type','?')} `{r.get('id','?')[:8]}` {r.get('status','?')}")

    # Suggestions
    ref_missing = any(not (c.get("media_id") or "").startswith("xxxxxxxx") for c in characters)
    vid_done = all(
        (s.get(f"{ori.lower()}_video_status") == "COMPLETED" for s in await api_get(f"/api/scenes?video_id={v['id']}"))
        for v in videos
    )
    img_done = all(
        (s.get(f"{ori.lower()}_image_status") == "COMPLETED" for s in await api_get(f"/api/scenes?video_id={v['id']}"))
        for v in videos
        for s in [await api_get(f"/api/scenes?video_id={v['id']}")]
    )

    if vid_done:
        out.append("\n**Next:** `/fk-concat <vid>`")
    elif img_done:
        out.append(f"\n**Next:** `/fk-gen-videos <pid> <vid>`")
    else:
        out.append(f"\n**Next:** `/fk-gen-refs <pid>` then `/fk-gen-images <pid> <vid>`")

    return "\n".join(out)


async def _handle_gen_images(ctx: dict, args: str) -> str:
    """Implement /fk-gen-images"""
    parts = args.strip().split()
    if len(parts) < 2:
        return "Usage: `/fk-gen-images <project_id> <video_id>`"
    pid, vid = parts[0], parts[1]

    # Step 0: detect orientation
    out_resp = await api_get(f"/api/projects/{pid}/output-dir")
    meta = _read_meta(out_resp["path"] + "/meta.json")
    ORI = meta.get("orientation", "HORIZONTAL")
    ori = ORI.lower()

    # Step 1: pre-check entities
    chars = await api_get(f"/api/projects/{pid}/characters")
    missing_chars = [c["name"] for c in chars if not (c.get("media_id") or "").startswith("xxxxxxxx-xxxx-xxxx-xxxx-")]
    if missing_chars:
        return f"⚠ ABORT: Missing refs for: {', '.join(missing_chars)}. Run `/fk-gen-refs {pid}` first."

    # Step 2: get scenes, classify waves
    scenes = await api_get(f"/api/scenes?video_id={vid}")
    img_field = f"{ori}_image_status"
    mid_field = f"{ori}_image_media_id"

    pending = []
    for s in scenes:
        if s.get(img_field) != "COMPLETED" or not (s.get(mid_field) or "").startswith("xxxxxxxx-xxxx-xxxx-xxxx-"):
            pending.append(s)

    if not pending:
        return "✓ All scene images already complete."

    # Classify by wave
    root_scenes = [s for s in pending if s.get("chain_type") == "ROOT" or not s.get("parent_scene_id")]
    cont_scenes = [s for s in pending if s.get("chain_type") == "CONTINUATION"]

    if root_scenes:
        batch = [{"type": "GENERATE_IMAGE", "scene_id": s["id"], "project_id": pid, "video_id": vid, "orientation": ORI}
                 for s in root_scenes]
        resp = await api_post("/api/requests/batch", {"requests": batch})
        await poll_batch_status(vid, "GENERATE_IMAGE")
        # Refresh scenes
        scenes = await api_get(f"/api/scenes?video_id={vid}")

    # Wave 2+ for continuations
    if cont_scenes:
        # Filter to those whose parent now has a completed image
        scene_map = {s["id"]: s for s in scenes}
        ready_cont = []
        for s in cont_scenes:
            parent_id = s.get("parent_scene_id")
            parent = scene_map.get(parent_id, {})
            if parent.get(img_field) == "COMPLETED":
                ready_cont.append(s)

        if ready_cont:
            batch = [{"type": "EDIT_IMAGE", "scene_id": s["id"], "project_id": pid, "video_id": vid, "orientation": ORI}
                     for s in ready_cont]
            await api_post("/api/requests/batch", {"requests": batch})
            await poll_batch_status(vid, "EDIT_IMAGE")

    # Step 4: verify
    scenes = await api_get(f"/api/scenes?video_id={vid}")
    rows = []
    for s in sorted(scenes, key=lambda x: x.get("display_order", 0)):
        mid = s.get(mid_field, "")
        status = s.get(img_field, "?")
        rows.append([
            str(s.get("display_order", 0)),
            (s.get("prompt", "") or "")[:50],
            s.get("chain_type", "?"),
            status.replace("COMPLETED", "✓").replace("PENDING", "○").replace("PROCESSING", "◐").replace("FAILED", "✗"),
            (mid[:12] if mid else "-"),
        ])

    out = ["**Image generation submitted.** Results:\n"]
    out.append(_format_table(["#", "Prompt(50)", "Chain", "Status", "media_id"], rows))

    # Download images to output dir
    out_dir = Path(__file__).parent.parent.parent / out_resp["path"]
    await _download_scene_media(pid, scenes, "img", ORI, out_dir)

    out.append("\n✓ All done. Run `/fk-gen-videos <pid> <vid>` to generate videos.")
    return "\n".join(out)


async def _handle_gen_videos(ctx: dict, args: str) -> str:
    """Implement /fk-gen-videos"""
    parts = args.strip().split()
    if len(parts) < 2:
        return "Usage: `/fk-gen-videos <project_id> <video_id>`"
    pid, vid = parts[0], parts[1]

    # Detect orientation
    out_resp = await api_get(f"/api/projects/{pid}/output-dir")
    meta = _read_meta(out_resp["path"] + "/meta.json")
    ORI = meta.get("orientation", "HORIZONTAL")
    ori = ORI.lower()
    vid_field = f"{ori}_video_status"
    mid_field = f"{ori}_video_media_id"
    img_field = f"{ori}_image_status"

    scenes = await api_get(f"/api/scenes?video_id={vid}")

    # Pre-check
    missing = [s["id"] for s in scenes
               if not (s.get(mid_field) or "").startswith("xxxxxxxx-xxxx-xxxx-xxxx-")
               or s.get(img_field) != "COMPLETED"]
    if missing:
        return f"⚠ ABORT: {len(missing)} scenes missing images. Run `/fk-gen-images {pid} {vid}` first."

    pending = [s for s in scenes if s.get(vid_field) != "COMPLETED" or not (s.get(mid_field) or "").startswith("xxxxxxxx")]
    if not pending:
        return "✓ All videos already complete."

    batch = [{"type": "GENERATE_VIDEO", "scene_id": s["id"], "project_id": pid, "video_id": vid, "orientation": ORI}
             for s in pending]
    await api_post("/api/requests/batch", {"requests": batch})
    await poll_batch_status(vid, "GENERATE_VIDEO", interval=15.0, timeout=900.0)

    scenes = await api_get(f"/api/scenes?video_id={vid}")
    rows = []
    for s in sorted(scenes, key=lambda x: x.get("display_order", 0)):
        mid = s.get(mid_field, "")
        status = s.get(vid_field, "?")
        rows.append([
            str(s.get("display_order", 0)),
            status.replace("COMPLETED", "✓").replace("PENDING", "○").replace("PROCESSING", "◐").replace("FAILED", "✗"),
            (mid[:12] if mid else "-"),
        ])

    out = ["**Video generation submitted.** Results:\n"]
    out.append(_format_table(["#", "Status", "media_id"], rows))

    # Download videos to output dir
    out_dir = Path(__file__).parent.parent.parent / out_resp["path"]
    await _download_scene_media(pid, scenes, "4k", ORI, out_dir)

    out.append("\n✓ All done. Run `/fk-concat <vid>` to merge.")
    return "\n".join(out)


async def _handle_doctor(ctx: dict, args: str) -> str:
    """Implement /fk-doctor"""
    args = args.strip()
    out = ["**FlowKit Doctor**\n"]

    health = await api_health()
    out.append(f"Extension: {'OK' if health.get('extension_connected') else 'OFFLINE'}")

    if not args:
        # Triage mode
        failures = await api_get("api/requests?status=FAILED&limit=20")
        processing = await api_get("api/requests?status=PROCESSING")
        if failures:
            out.append(f"\n**{len(failures)} failed requests:**")
            for r in failures[:5]:
                out.append(f"  - `{r.get('type','?')} {r.get('id','?')[:8]}`: {r.get('error_message', '?')[:80]}")
        else:
            out.append("\n✓ No failed requests.")
        if processing:
            out.append(f"\n**{len(processing)} processing:** {[r['id'][:8] for r in processing]}")
        return "\n".join(out)

    if args.startswith("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"):
        # Single request
        req = await api_get(f"/api/requests/{args}")
        out.append(f"\n**Request:** {req.get('type','?')}")
        out.append(f"**Status:** {req.get('status','?')}")
        out.append(f"**Retries:** {req.get('retry_count','0')}")
        err = req.get("error_message", "")
        if err:
            out.append(f"**Error:** {err[:200]}")
        # Quick diagnosis
        if "not found" in err.lower():
            out.append("→ Likely expired `media_id`. Try `/fk-fix-uuids` or re-upload.")
        elif "unsafe" in err.lower():
            out.append("→ Safety filter triggered. Rewrite prompt avoiding real people/brands.")
        elif "quota" in err.lower():
            out.append("→ Credits exhausted. Wait for daily reset.")
        elif "access_denied" in err.lower():
            out.append("→ Tier mismatch. Check `/fk-status` for tier.")
        elif not err:
            out.append("→ No error. Still processing — wait and check again.")
        return "\n".join(out)

    # Error string lookup
    err_lower = args.lower()
    if "not found" in err_lower:
        return "**`not found`** → media_id expired. Recovery: auto-requeue if retry_count < 5, else re-upload via `/fk-upload-image`."
    if "unsafe" in err_lower:
        return "**`UNSAFE_GENERATION`** → Safety filter. Fix: use alias names + physical descriptions in prompts."
    if "quota" in err_lower:
        return "**`QUOTA`** → Daily credits exhausted. Wait for reset or upgrade tier."
    if "captcha" in err_lower:
        return "**`CAPTCHA`** → Open a Google Flow tab at labs.google/fx/tools/flow and reload the extension."
    if "extension" in err_lower and "connect" in err_lower:
        return "**Extension offline** → Start `python -m agent.main`. Reload Chrome extension at chrome://extensions."
    return f"Unknown error pattern: `{args}`. Run `/fk-status` for full diagnostics."


async def _handle_gen_refs(ctx: dict, args: str) -> str:
    """Implement /fk-gen-refs"""
    parts = args.strip().split()
    if not parts:
        return "Usage: `/fk-gen-refs <project_id>`"
    pid = parts[0]

    chars = await api_get(f"/api/projects/{pid}/characters")
    pending = [c for c in chars if not (c.get("media_id") or "").startswith("xxxxxxxx-xxxx-xxxx-xxxx-")]
    if not pending:
        return "✓ All reference images already ready."

    batch = [{"type": "GENERATE_CHARACTER_IMAGE", "character_id": c["id"], "project_id": pid}
             for c in pending]
    await api_post("/api/requests/batch", {"requests": batch})

    await poll_batch_status(video_id=None, req_type="GENERATE_CHARACTER_IMAGE", interval=10.0)
    chars = await api_get(f"/api/projects/{pid}/characters")
    rows = []
    for c in chars:
        mid = c.get("media_id", "")
        ready = "✓" if mid and mid.startswith("xxxxxxxx-xxxx-xxxx-xxxx-") else "○"
        rows.append([c.get("name", "?"), c.get("entity_type", "?"), (mid[:12] if mid else "pending"), ready])
    out = ["**Reference images submitted.**\n"]
    out.append(_format_table(["Name", "Type", "media_id", "Ready"], rows))
    out.append("\n✓ Done. Run `/fk-gen-images <pid> <vid>` next.")
    return "\n".join(out)


async def _handle_concat(ctx: dict, args: str) -> str:
    """Implement /fk-concat — downloads videos, normalizes, merges."""
    parts = args.strip().split()
    if not parts:
        return "Usage: `/fk-concat <video_id> [--with-tts]`"
    vid = parts[0]
    with_tts = "--with-tts" in args

    # Get video + project info
    video = await api_get(f"/api/videos/{vid}")
    pid = video.get("project_id")
    out_resp = await api_get(f"/api/projects/{pid}/output-dir")
    meta = _read_meta(out_resp["path"] + "/meta.json")
    ORI = meta.get("orientation", "HORIZONTAL")
    ori = ORI.lower()
    slug = out_resp.get("slug", "output")
    out_dir = Path(__file__).parent.parent.parent / out_resp["path"]

    scenes = await api_get(f"/api/scenes?video_id={vid}")
    scenes = sorted(scenes, key=lambda s: s.get("display_order", 0))

    # Download videos
    for scene in scenes:
        vid_url = scene.get(f"{ori}_video_url") or scene.get(f"{ori}_upscale_url")
        mid = scene.get(f"{ori}_video_media_id", "")
        idx3 = f"{scene.get('display_order', 0):03d}"
        canonical = out_dir / "4k" / f"scene_{idx3}_{scene['id']}.mp4"
        if canonical.exists():
            continue
        if not vid_url:
            return f"⚠ No video for scene {scene['id'][:8]}. Run `/fk-gen-videos {pid} {vid}` first."
        (out_dir / "4k").mkdir(parents=True, exist_ok=True)
        client = await _get_client()
        r = await client.get(vid_url)
        r.raise_for_status()
        canonical.write_bytes(r.content)

    # Normalize with ffmpeg
    (out_dir / "norm").mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        idx3 = f"{scene.get('display_order', 0):03d}"
        src = out_dir / "4k" / f"scene_{idx3}_{scene['id']}.mp4"
        dst = out_dir / "norm" / f"scene_{idx3}_{scene['id']}.mp4"
        if dst.exists():
            continue
        w, h = 1920, 1080
        if ORI == "VERTICAL":
            w, h = 1080, 1920
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
            "-r", "24", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(dst),
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()

    # Build concat list
    concat_file = out_dir / "norm" / "concat.txt"
    concat_content = []
    for scene in scenes:
        idx3 = f"{scene.get('display_order', 0):03d}"
        f = out_dir / "norm" / f"scene_{idx3}_{scene['id']}.mp4"
        if f.exists():
            concat_content.append(f"file '{f}'")
    concat_file.write_text("\n".join(concat_content), encoding="utf-8")

    final = out_dir / f"{slug}_final.mp4"
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
           "-c", "copy", "-movflags", "+faststart", str(final)]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()

    size = final.stat().st_size if final.exists() else 0
    
    # Update video record with thumbnail and status
    first_scene = scenes[0] if scenes else {}
    thumbnail_url = first_scene.get(f"{ori}_image_url")
    update_data = {"status": "COMPLETED"}
    if thumbnail_url:
        update_data["thumbnail_url"] = thumbnail_url
    await api_patch(f"/api/videos/{vid}", update_data)

    # Trigger UI refresh
    from agent.services.event_bus import event_bus
    await event_bus.emit("project_updated", {"id": pid})

    out = [f"**Concat complete:** `{final}`"]
    out.append(f"Scenes: {len(scenes)} | Size: {size / 1024 / 1024:.1f} MB")
    out.append(f"Orientation: {ORI} | Quality: {ORI == 'VERTICAL' and '1080x1920' or '1920x1080'}")
    if with_tts:
        out.append("Note: TTS narration requested — ensure TTS files exist in `tts/` dir.")
    return "\n".join(out)


async def _handle_switch_project(ctx: dict, args: str) -> str:
    """Implement /fk-switch-project"""
    parts = args.strip().split()
    if not parts:
        projects = await api_get("/api/projects")
        rows = [[p["id"][:12], p.get("name", "?"), p.get("user_paygate_tier", "?").replace("PAYGATE_TIER_", "")]
                for p in projects]
        return "**Projects:**\n" + _format_table(["ID", "Name", "Tier"], rows)
    pid = parts[0]
    project = await api_get(f"/api/projects/{pid}")
    return f"Switched to: **{project.get('name', pid)}** (`{pid}`)"


async def _handle_health(ctx: dict, args: str) -> str:
    """Implement /fk-health check"""
    try:
        health = await api_health()
        ext = "OK" if health.get("extension_connected") else "OFFLINE"
        return f"**Server:** OK | **Extension:** {ext}"
    except Exception as e:
        return f"**Server:** ERROR — {e}"


# ─── Skill routing ──────────────────────────────────────────────────────────

_HANDLERS = {
    "fk-status": _handle_status,
    "fk-doctor": _handle_doctor,
    "fk-gen-images": _handle_gen_images,
    "fk-gen-videos": _handle_gen_videos,
    "fk-gen-refs": _handle_gen_refs,
    "fk-concat": _handle_concat,
    "fk-switch-project": _handle_switch_project,
    "fk-health": _handle_health,
}


def list_skills() -> list[dict]:
    """Return list of available skill names and their file paths."""
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for f in sorted(SKILLS_DIR.glob("fk-*.md")):
        if f.name == "README.md":
            continue
        name = f.stem  # "fk-gen-images"
        # Parse usage line
        usage = ""
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.startswith("Usage:"):
                    usage = line.replace("Usage:", "").strip()
                    break
        except Exception:
            pass
        skills.append({"name": name, "file": str(f.relative_to(SKILLS_DIR),), "usage": usage})
    return skills


class SkillContentResult:
    """Marker class: skill has no handler, return content for LLM injection."""
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content


async def execute_skill(name: str, args: str) -> str | SkillContentResult:
    """Execute a skill by name with args.

    - If a Python handler exists in _HANDLERS → execute directly, return text.
    - If no handler → return SkillContentResult so the caller (chat endpoint)
      can inject the skill content into the LLM conversation for orchestration.
      This mirrors how Claude CLI SDK works: the LLM reads the skill file and
      follows the instructions interactively.
    """
    # Normalize: ensure fk- prefix
    if not name.startswith("fk-"):
        name = f"fk-{name}"

    # Direct Python handler (gen-images, gen-videos, concat, etc.)
    if name in _HANDLERS:
        return await _HANDLERS[name]({}, args)

    # LLM-orchestrated skill (create-project, research, etc.)
    skill_file = SKILLS_DIR / f"{name}.md"
    if not skill_file.exists():
        return f"❌ Skill `{name}` not found. Use `/fk-list` to see available skills."

    content = skill_file.read_text(encoding="utf-8")
    return SkillContentResult(name, content)


def detect_skill_command(message: str) -> tuple[str, str] | None:
    """Detect /fk-* command in message. Returns (skill_name, args) or None.
    skill_name is the part AFTER fk- (e.g. 'gen-images')."""
    m = re.search(r'/fk-([\w-]+)(?:\s+(.+))?', message.strip())
    if m:
        return m.group(1), m.group(2) or ""
    return None
