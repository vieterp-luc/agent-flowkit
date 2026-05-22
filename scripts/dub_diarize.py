#!/usr/bin/env python3.10
"""dub_diarize.py — Speaker diarization for dub_video.py.

Runs under python3.10 (torch + pyannote available there). Called as a
subprocess by dub_video.py. Reads the HuggingFace token from the environment
(HF_TOKEN / HUGGINGFACE_TOKEN / HF_HUB_TOKEN) — the diarization model is gated.

Usage:
  python3.10 dub_diarize.py <audio_16k_mono.wav>

Output (stdout, JSON):
  {"turns":    [{"start","end","speaker"}, ...],
   "speakers": [{"speaker","total","gender","f0"}, ...]}
On failure: {"error": "..."} and exit code 1.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

# v4 community model is the current recommendation; 3.1 kept as fallback.
MODELS = [
    os.environ.get("PYANNOTE_MODEL", "pyannote/speaker-diarization-community-1"),
    "pyannote/speaker-diarization-3.1",
]


def hf_token() -> str:
    for key in ("HF_TOKEN", "HUGGINGFACE_TOKEN", "HF_HUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val.strip()
    return ""


def estimate_f0(samples: np.ndarray, sr: int) -> float:
    """Median fundamental frequency (Hz) via per-frame autocorrelation.

    Returns 0.0 when no voiced frame is found.
    """
    if samples.size < sr // 4:
        return 0.0
    frame = int(0.04 * sr)          # 40 ms windows
    hop = frame // 2
    lo = int(sr / 300)              # 300 Hz upper bound
    hi = int(sr / 70)               # 70 Hz lower bound
    f0s = []
    for i in range(0, len(samples) - frame, hop):
        win = samples[i:i + frame].astype(np.float64)
        win -= win.mean()
        energy = np.sqrt(np.mean(win ** 2))
        if energy < 0.01:           # silence / unvoiced
            continue
        corr = np.correlate(win, win, mode="full")[frame - 1:]
        if corr[0] <= 0:
            continue
        seg = corr[lo:hi]
        if seg.size == 0:
            continue
        peak = int(np.argmax(seg)) + lo
        if corr[peak] / corr[0] < 0.3:   # weak periodicity → unvoiced
            continue
        f0s.append(sr / peak)
    return float(np.median(f0s)) if f0s else 0.0


def speaker_gender(audio: np.ndarray, sr: int, turns: list, speaker: str) -> tuple:
    """Concatenate up to ~8 s of a speaker's audio → (gender, f0)."""
    chunks = []
    budget = 8.0
    for t in turns:
        if t["speaker"] != speaker:
            continue
        a, b = int(t["start"] * sr), int(t["end"] * sr)
        chunks.append(audio[a:b])
        budget -= (t["end"] - t["start"])
        if budget <= 0:
            break
    if not chunks:
        return "unknown", 0.0
    f0 = estimate_f0(np.concatenate(chunks), sr)
    if f0 <= 0:
        return "unknown", 0.0
    return ("male" if f0 < 165 else "female"), round(f0, 1)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: dub_diarize.py <audio.wav>"}))
        sys.exit(1)
    audio_path = sys.argv[1]
    token = hf_token()
    if not token:
        print(json.dumps({"error": "no HF token (set HF_TOKEN) — model is gated"}))
        sys.exit(1)

    try:
        import torch
        from pyannote.audio import Pipeline
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"error": f"pyannote import failed: {e}"}))
        sys.exit(1)

    pipeline = None
    last_err = ""
    for model in MODELS:
        try:
            pipeline = Pipeline.from_pretrained(model, token=token)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{model}: {e}"
    if pipeline is None:
        print(json.dumps({"error": f"cannot load diarization model — {last_err}"}))
        sys.exit(1)

    pipeline.to(torch.device("cpu"))

    try:
        diarization = pipeline(audio_path)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"error": f"diarization failed: {e}"}))
        sys.exit(1)

    turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        turns.append({
            "start": round(float(turn.start), 3),
            "end": round(float(turn.end), 3),
            "speaker": str(speaker),
        })
    turns.sort(key=lambda t: t["start"])

    audio, sr = sf.read(audio_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    totals = {}
    for t in turns:
        totals[t["speaker"]] = totals.get(t["speaker"], 0.0) + (t["end"] - t["start"])

    speakers = []
    for spk in sorted(totals, key=lambda s: -totals[s]):
        gender, f0 = speaker_gender(audio, sr, turns, spk)
        speakers.append({
            "speaker": spk,
            "total": round(totals[spk], 1),
            "gender": gender,
            "f0": f0,
        })

    print(json.dumps({"turns": turns, "speakers": speakers}))


if __name__ == "__main__":
    main()
