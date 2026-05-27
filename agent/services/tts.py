"""OmniVoice TTS service — persistent parallel workers for maximum performance."""
import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, List

from agent.config import TTS_MODEL, TTS_SAMPLE_RATE, TTS_DEVICE

logger = logging.getLogger(__name__)

# Default to python3.10 (has torch/torchaudio/omnivoice); override with TTS_PYTHON_BIN if needed
PYTHON_BIN = os.environ.get("TTS_PYTHON_BIN", "python3.10")

# Persistent script template for TTS generation
_TTS_PERSISTENT_SCRIPT = """
import sys, json, torch, numpy as np, random, logging, time
import soundfile as sf
from pathlib import Path

# Silence basic logs
logging.getLogger('torch').setLevel(logging.ERROR)

args_init = json.loads(sys.argv[1])
model_name = args_init["model"]
device = args_init.get("device", "cpu")

try:
    from omnivoice import OmniVoice
    # Force float32 to avoid noise on MPS
    model = OmniVoice.from_pretrained(model_name, device_map=device, dtype=torch.float32)
    print("READY", flush=True)
except Exception as e:
    print(json.dumps({"ok": False, "error": f"INIT_FAILED: {str(e)}"}), flush=True)
    sys.exit(1)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        item = json.loads(line)
        if item.get("type") == "EXIT":
            break
            
        seed = item.get("seed", 42)
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

        kwargs = {"text": item["text"]}
        if item.get("ref_audio") and item.get("ref_text"):
            kwargs["ref_audio"] = item["ref_audio"]
            kwargs["ref_text"] = item["ref_text"]
        elif item.get("instruct"):
            kwargs["instruct"] = item["instruct"]
        if item.get("speed") and item["speed"] != 1.0:
            kwargs["speed"] = item["speed"]

        audio = model.generate(**kwargs)
        output_path = item["output"]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        wav = audio[0]
        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()
        if wav.ndim > 1:
            wav = wav[0]
        wav = wav.astype(np.float32)
        sf.write(output_path, wav, item.get("sample_rate", 24000))

        info = sf.info(output_path)
        print(json.dumps({"ok": True, "path": output_path, "duration": info.duration}), flush=True)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), flush=True)
"""

class TTSWorker:
    """A single persistent TTS worker process."""
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self._proc: Optional[subprocess.Popen] = None
        self._ready = False
        self._lock = asyncio.Lock()

    async def ensure_started(self):
        if self._proc and self._proc.poll() is None and self._ready:
            return

        async with self._lock:
            if self._proc and self._proc.poll() is None and self._ready:
                return

            if self._proc:
                try: self._proc.terminate()
                except: pass

            logger.info("Starting TTS Worker #%d (model: %s, device: %s)...", self.worker_id, TTS_MODEL, TTS_DEVICE)
            args_init = {"model": TTS_MODEL, "device": TTS_DEVICE}
            
            self._proc = subprocess.Popen(
                [PYTHON_BIN, "-c", _TTS_PERSISTENT_SCRIPT, json.dumps(args_init)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            def wait_ready():
                line = self._proc.stdout.readline().strip()
                return line == "READY"

            loop = asyncio.get_event_loop()
            self._ready = await loop.run_in_executor(None, wait_ready)
            if self._ready:
                logger.info("TTS Worker #%d ready.", self.worker_id)
            else:
                logger.error("TTS Worker #%d failed to start.", self.worker_id)
                self._proc = None

    async def run_task(self, task: dict) -> dict:
        await self.ensure_started()
        if not self._proc:
            return {"ok": False, "error": "Worker failed to start"}

        # Note: Worker-level lock ensures only one task per process
        async with self._lock:
            try:
                self._proc.stdin.write(json.dumps(task) + "\n")
                self._proc.stdin.flush()
                
                loop = asyncio.get_event_loop()
                line = await loop.run_in_executor(None, self._proc.stdout.readline)
                if not line:
                    self._ready = False
                    return {"ok": False, "error": "Worker died"}
                
                return json.loads(line.strip())
            except Exception as e:
                self._ready = False
                return {"ok": False, "error": str(e)}

class TTSManager:
    """Manages a pool of persistent TTS workers."""
    def __init__(self, num_workers: int = 2):
        self.num_workers = num_workers
        self.workers: List[TTSWorker] = [TTSWorker(i) for i in range(num_workers)]
        self._worker_queue = asyncio.Queue()
        self._initialized = False

    async def _ensure_initialized(self):
        if self._initialized:
            return
        for w in self.workers:
            self._worker_queue.put_nowait(w)
        self._initialized = True

    async def run_task(self, task: dict) -> dict:
        await self._ensure_initialized()
        # Get next available worker from queue
        worker = await self._worker_queue.get()
        try:
            return await worker.run_task(task)
        finally:
            # Put worker back into pool
            self._worker_queue.put_nowait(worker)

# Singleton manager with 2 workers (safe for 16GB RAM)
_manager = TTSManager(num_workers=2)

async def generate_speech(
    text: str,
    output_path: str,
    instruct: Optional[str] = None,
    ref_audio: Optional[str] = None,
    ref_text: Optional[str] = None,
    speed: float = 1.0,
) -> str:
    """Generate speech for text via a worker from the pool. Returns path to WAV file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    task = {
        "text": text,
        "output": output_path,
        "sample_rate": TTS_SAMPLE_RATE,
        "speed": speed,
    }
    if instruct:
        task["instruct"] = instruct
    if ref_audio:
        task["ref_audio"] = ref_audio
    if ref_text:
        task["ref_text"] = ref_text

    result = await _manager.run_task(task)

    if not result.get("ok"):
        raise RuntimeError(f"TTS failed: {result.get('error', 'unknown')}")

    logger.info("TTS saved to %s (duration: %.2fs)", output_path, result.get("duration", 0))
    return output_path

async def generate_video_narration(
    scenes: list[dict],
    output_dir: str,
    instruct: Optional[str] = None,
    ref_audio: Optional[str] = None,
    ref_text: Optional[str] = None,
    speed: float = 1.0,
) -> list[dict]:
    """Generate narration WAVs for scenes in parallel using the worker pool.
    
    Returns list of result dicts.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    async def process_scene(scene: dict):
        scene_id = scene.get("id")
        display_order = scene.get("display_order", 0)
        narrator_text = scene.get("narrator_text")

        if not narrator_text:
            return {
                "scene_id": scene_id,
                "display_order": display_order,
                "narrator_text": None,
                "audio_path": None,
                "duration": None,
                "status": "SKIPPED",
                "error": None,
            }

        wav_path = str(out_dir / f"scene_{display_order:03d}_{scene_id}.wav")
        # Skip if WAV already exists and is non-trivial (>1KB)
        if Path(wav_path).exists() and Path(wav_path).stat().st_size > 1024:
            return {
                "scene_id": scene_id,
                "display_order": display_order,
                "narrator_text": narrator_text,
                "audio_path": wav_path,
                "duration": _wav_duration(wav_path),
                "status": "COMPLETED",
                "error": None,
            }

        task = {
            "text": narrator_text,
            "output": wav_path,
            "sample_rate": TTS_SAMPLE_RATE,
            "speed": speed,
            "instruct": instruct,
            "ref_audio": ref_audio,
            "ref_text": ref_text,
        }

        r = await _manager.run_task(task)
        
        if r.get("ok"):
            return {
                "scene_id": scene_id,
                "display_order": display_order,
                "narrator_text": narrator_text,
                "audio_path": r.get("path"),
                "duration": r.get("duration"),
                "status": "COMPLETED",
                "error": None,
            }
        else:
            return {
                "scene_id": scene_id,
                "display_order": display_order,
                "narrator_text": narrator_text,
                "audio_path": None,
                "duration": None,
                "status": "FAILED",
                "error": r.get("error", "worker error"),
            }

    # Process all scenes in parallel (manager will throttle via worker queue)
    results = await asyncio.gather(*(process_scene(s) for s in scenes))
    return list(results)

def _wav_duration(path: str) -> float | None:
    try:
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except Exception:
        return None
