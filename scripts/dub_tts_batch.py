#!/usr/bin/env python3.10
"""dub_tts_batch.py — Multi-voice OmniVoice TTS batch for dub_video.py.

Runs under python3.10 (torch + omnivoice). Loads the model ONCE and generates
every dialogue clip — each item carries its own reference voice, so a single
run can render multiple characters. Called as a subprocess by dub_video.py.

Usage:
  python3.10 dub_tts_batch.py <items.json>

items.json:
  {"model": "k2-fsa/OmniVoice", "sample_rate": 24000,
   "items": [{"index": 0, "text": "...", "ref_audio": "/path.wav",
              "ref_text": "...", "speed": 1.0, "output": "/out/clip_000.wav"}]}

Output (stdout, JSON):
  [{"index", "ok", "path", "duration", "error"}]
"""
import json
import random
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch


def main():
    if len(sys.argv) < 2:
        print(json.dumps([{"index": -1, "ok": False, "error": "no items file"}]))
        sys.exit(1)

    args = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    # Deterministic prosody — same seed convention as agent/services/tts.py
    seed = args.get("seed", 42)
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    from omnivoice import OmniVoice

    device = "cpu"
    dtype = torch.float32
    if torch.backends.mps.is_available():
        device = "mps"
        # dtype = torch.float16 # OmniVoice might prefer float32 for stability
    
    print(f"[tts] using device={device}", file=sys.stderr)

    model = OmniVoice.from_pretrained(
        args["model"], device_map=device, dtype=dtype
    )
    sample_rate = args["sample_rate"]

    results = []
    for i, item in enumerate(args["items"]):
        out = Path(item["output"])
        if out.exists() and out.stat().st_size > 0:
            # Skip generation, just read duration
            try:
                wav, sr = sf.read(str(out))
                results.append({
                    "index": item["index"],
                    "ok": True,
                    "path": str(out),
                    "duration": round(len(wav) / sr, 3),
                })
                # print(f"[tts] {i+1}/{len(args['items'])}: (skipped) {item['text'][:30]}...", file=sys.stderr)
                continue
            except Exception:
                pass

        print(f"[tts] {i+1}/{len(args['items'])}: {item['text'][:30]}...", file=sys.stderr)
        try:
            kwargs = {"text": item["text"]}
            if item.get("ref_audio") and item.get("ref_text"):
                kwargs["ref_audio"] = item["ref_audio"]
                kwargs["ref_text"] = item["ref_text"]
            elif item.get("instruct"):
                kwargs["instruct"] = item["instruct"]
            speed = item.get("speed", 1.0)
            if speed and speed != 1.0:
                kwargs["speed"] = speed

            audio = model.generate(**kwargs)
            wav = audio[0]
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()
            if wav.ndim > 1:
                wav = wav[0]
            wav = wav.astype(np.float32)

            out = Path(item["output"])
            out.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(out), wav, sample_rate)

            results.append({
                "index": item["index"],
                "ok": True,
                "path": str(out),
                "duration": round(len(wav) / sample_rate, 3),
            })
        except Exception as e:  # noqa: BLE001
            results.append({
                "index": item["index"],
                "ok": False,
                "error": str(e),
            })

    print(json.dumps(results))


if __name__ == "__main__":
    main()
