#!/usr/bin/env python3
"""dub_video.py — Faithful multi-voice AI dub + Vietnamese subtitle for Chinese video.

Pipeline (image & length kept 100% intact — video is never cut or stretched):
  video → extract audio → faster-whisper transcribe (zh)
        → pyannote diarize (speaker per segment)
        → Claude translate zh→vi (cultivation glossary)
        → OmniVoice multi-voice TTS (one voice per character)
        → atempo-fit + numpy dub-track assembly anchored at original timestamps
        → ffmpeg mix (ducked original audio + dub) + burn VN subtitle → output.

Transcribe + translate run under this interpreter (faster-whisper). Diarization
and TTS run as python3.10 subprocesses (torch / pyannote / omnivoice live there).

First run writes dub_cache.json (segments/translations/diarization) and
voicemap.json (speaker→voice). Edit voicemap.json and re-run to re-voice fast —
the cache skips transcription, translation and diarization.

Usage:
  python3 dub_video.py --video in.mp4 --output out/final.mp4
  python3 dub_video.py --video in.mp4 --output out/final.mp4 --voices single
  python3 dub_video.py --video in.mp4 --output out/final.mp4 --fresh   # rebuild cache
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
from sub_video import (  # noqa: E402  reuse the proven transcribe/translate/sub code
    extract_audio, transcribe, translate_batch, probe_size, write_ass, write_srt,
)

TEMPLATES_JSON = BASE_DIR / "output" / "_shared" / "tts_templates" / "templates.json"
TTS_MODEL = os.environ.get("TTS_MODEL", "k2-fsa/OmniVoice")
TTS_SR = int(os.environ.get("TTS_SAMPLE_RATE", "24000"))
PY310 = os.environ.get("TTS_PYTHON_BIN", "python3.10")

# Best-guess gender pools — voicemap.json is editable so a wrong guess is cheap to fix.
MALE_POOL = ["Bao_Trung_TTS", "Anh_Khoi_TTS", "Minh_Quan_TTS", "Manh_Dung_TTS",
             "Hai_KC_TTS", "Thang_QC_TTS"]
FEMALE_POOL = ["Nguyet_Nga_TTS", "Ngoc_Huyen_TTS", "Hong_Hanh_podcast_TTS"]

# Domain glossary appended to the zh→vi translation prompt (tu-tiên / kiếm hiệp).
CULTIVATION_GLOSSARY = """- Đây là phim tu tiên/kiếm hiệp Trung Quốc. Giữ NGUYÊN các thuật ngữ Hán-Việt quen thuộc, KHÔNG dịch nghĩa đen: Sư tôn, Sư phụ, Đồ nhi, Sư huynh, Sư đệ, Sư tỷ, Sư muội, Trưởng lão, Tông môn, Tông chủ, Luyện khí, Trúc cơ, Kim đan, Nguyên anh, Hóa thần, Độ kiếp, Phi thăng, Linh thạch, Linh khí, Pháp bảo, Pháp khí, Đan dược, Công pháp, Tâm pháp, Khí vận chi tử, Thiên kiêu, Phế vật, Phàm nhân, Tu sĩ, Tán tu.
- Dòng "hệ thống thông báo" (vd bắt đầu bằng tiếng chuông, "Đinh!", "Phát hiện...", "Kích hoạt...", "Khen thưởng..."): dịch ngắn gọn, dứt khoát, giữ chất game/hệ thống.
- Xưng hô dùng đại từ cổ trang hợp bối cảnh (ta/ngươi/hắn/nàng/y/tại hạ/chư vị) thay cho tôi/bạn/anh/cô hiện đại."""


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def run(cmd, timeout=900):
    """Run a command, abort with stderr tail on failure."""
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        sys.exit(f"[error] {cmd[0]} failed:\n{(r.stderr or r.stdout)[-1000:]}")
    return r


def ffprobe_duration(path) -> float:
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def has_audio_stream(path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "quiet", "-select_streams", "a:0",
                        "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def read_wav_pcm16(path) -> np.ndarray:
    """Read a mono PCM-16 WAV as float32 in [-1, 1]."""
    with wave.open(str(path), "rb") as w:
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def write_wav_pcm16(path, samples: np.ndarray, sr: int):
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# --------------------------------------------------------------------------- #
# diarization + speaker assignment
# --------------------------------------------------------------------------- #
def run_diarize(wav: Path, hf_token: str):
    """Return (turns, speakers). Empty lists when diarization is unavailable."""
    if not hf_token:
        print("[diarize] no HF token — falling back to single voice", file=sys.stderr)
        return [], []
    env = {**os.environ, "HF_TOKEN": hf_token}
    try:
        r = subprocess.run([PY310, str(SCRIPT_DIR / "dub_diarize.py"), str(wav)],
                           capture_output=True, text=True, timeout=3600, env=env)
    except subprocess.TimeoutExpired:
        print("[diarize] timed out — falling back to single voice", file=sys.stderr)
        return [], []
    out = (r.stdout or "").strip().splitlines()
    data = {}
    if out:
        try:
            data = json.loads(out[-1])
        except json.JSONDecodeError:
            data = {}
    if "error" in data or "turns" not in data:
        err = data.get("error") or (r.stderr or "")[-300:]
        print(f"[diarize] unavailable ({err}) — falling back to single voice",
              file=sys.stderr)
        return [], []
    print(f"[diarize] {len(data['speakers'])} speakers, {len(data['turns'])} turns",
          file=sys.stderr)
    return data["turns"], data["speakers"]


def assign_speakers(segments: list, turns: list):
    """Tag each transcript segment with the speaker it overlaps most."""
    default = turns[0]["speaker"] if turns else "SPEAKER_00"
    for seg in segments:
        best, best_ov = default, 0.0
        for t in turns:
            ov = min(seg["end"], t["end"]) - max(seg["start"], t["start"])
            if ov > best_ov:
                best_ov, best = ov, t["speaker"]
        seg["speaker"] = best


# --------------------------------------------------------------------------- #
# voice mapping
# --------------------------------------------------------------------------- #
def load_templates() -> dict:
    if not TEMPLATES_JSON.exists():
        sys.exit(f"TTS templates not found: {TEMPLATES_JSON}")
    return json.loads(TEMPLATES_JSON.read_text(encoding="utf-8"))


def resolve_voice(voice: str, templates: dict, fallback: str):
    tmpl = templates.get(voice) or templates.get(fallback)
    if not tmpl:
        sys.exit(f"Voice template '{voice}' (and fallback '{fallback}') not found")
    return tmpl["audio_path"], tmpl.get("text", "")


def load_voicemap(path: Path) -> dict:
    """Load speaker→voice overrides. Accepts {spk: voice} or {spk: {voice: ...}}."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for k, v in raw.items():
        if k.startswith("_"):
            continue
        out[k] = v["voice"] if isinstance(v, dict) else v
    return out


def build_voice_map(speakers: list, existing: dict, fallback: str) -> dict:
    """Assign a voice template to each speaker (gender-aware, round-robin)."""
    vmap, mi, fi = {}, 0, 0
    for sp in speakers:
        spk = sp["speaker"]
        if spk in existing:
            vmap[spk] = existing[spk]
            continue
        if sp.get("gender") == "female":
            vmap[spk] = FEMALE_POOL[fi % len(FEMALE_POOL)]
            fi += 1
        else:  # male or unknown → male pool (most donghua leads are male)
            vmap[spk] = MALE_POOL[mi % len(MALE_POOL)]
            mi += 1
    if not vmap:
        vmap["SPEAKER_00"] = fallback
    return vmap


def write_voicemap(path: Path, vmap: dict, speakers: list, segments: list):
    line_counts = {}
    for seg in segments:
        spk = seg.get("speaker", "SPEAKER_00")
        line_counts[spk] = line_counts.get(spk, 0) + 1
    info = {s["speaker"]: s for s in speakers}
    doc = {"_note": "Sửa 'voice' (tên template TTS) rồi chạy lại skill — cache giữ nguyên."}
    for spk, voice in vmap.items():
        meta = info.get(spk, {})
        doc[spk] = {
            "voice": voice,
            "gender": meta.get("gender", "unknown"),
            "speaking_time": meta.get("total", 0.0),
            "lines": line_counts.get(spk, 0),
        }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
# TTS + dub-track assembly
# --------------------------------------------------------------------------- #
def run_tts_batch(items: list, work: Path) -> dict:
    """Generate every dialogue clip via the python3.10 OmniVoice batch script."""
    if not items:
        return {}
    items_json = work / "tts_items.json"
    items_json.write_text(json.dumps({
        "model": TTS_MODEL, "sample_rate": TTS_SR, "items": items,
    }, ensure_ascii=False), encoding="utf-8")
    timeout = 600 + len(items) * 45
    r = subprocess.run([PY310, str(SCRIPT_DIR / "dub_tts_batch.py"), str(items_json)],
                       capture_output=True, text=True, timeout=timeout)
    lines = (r.stdout or "").strip().splitlines()
    if not lines:
        sys.exit(f"[tts] no output:\n{(r.stderr or '')[-800:]}")
    try:
        results = json.loads(lines[-1])
    except json.JSONDecodeError:
        sys.exit(f"[tts] bad output:\n{(r.stderr or r.stdout)[-800:]}")
    return {res["index"]: res for res in results}


def fit_clip(src: str, target: float, out: Path, max_atempo: float) -> float:
    """Convert clip to PCM-16; compress with atempo when longer than its window."""
    dur = ffprobe_duration(src)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src]
    if target > 0.3 and dur > target * 1.05:
        factor = min(dur / target, max_atempo)
        if factor > 1.01:
            cmd += ["-filter:a", f"atempo={factor:.4f}"]
    cmd += ["-ar", str(TTS_SR), "-ac", "1", "-c:a", "pcm_s16le", str(out)]
    run(cmd, timeout=120)
    return ffprobe_duration(out)


def assemble_dub_track(placed: list, total_dur: float, out_wav: Path):
    """Sum every fitted clip into one full-length track at its original timestamp."""
    n = int(total_dur * TTS_SR) + TTS_SR
    track = np.zeros(n, dtype=np.float32)
    for p in placed:
        clip = read_wav_pcm16(p["clip_path"])
        a = int(p["start"] * TTS_SR)
        b = min(a + len(clip), n)
        track[a:b] += clip[:b - a]
    peak = float(np.max(np.abs(track))) if track.size else 0.0
    if peak > 1.0:
        track /= peak
    write_wav_pcm16(out_wav, track[:int(total_dur * TTS_SR)], TTS_SR)


def mix_and_burn(video: Path, dub_wav: Path, ass: Path, output: Path,
                 duck: float, burn_sub: bool):
    """Final render: ducked original audio + dub, optional burned VN subtitle."""
    if has_audio_stream(video):
        audio_fc = (
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={duck}[bg];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[fg];"
            f"[bg][fg]amix=inputs=2:duration=first:normalize=0[aout]"
        )
    else:
        audio_fc = "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[aout]"

    if burn_sub:
        ass_esc = str(ass).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        video_fc = f"[0:v]ass={ass_esc}[vout];"
        vmap, vcodec = "[vout]", ["-c:v", "libx264", "-preset", "medium",
                                  "-crf", "20", "-pix_fmt", "yuv420p"]
    else:
        video_fc, vmap, vcodec = "", "0:v", ["-c:v", "copy"]

    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(video), "-i", str(dub_wav),
        "-filter_complex", video_fc + audio_fc,
        "-map", vmap, "-map", "[aout]",
        *vcodec, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(output),
    ], timeout=3600)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="medium", help="Whisper model")
    ap.add_argument("--src-lang", default="zh")
    ap.add_argument("--voices", choices=["multi", "single"], default="multi")
    ap.add_argument("--voice", default="Bao_Trung_TTS",
                    help="Voice for single mode / fallback")
    ap.add_argument("--voicemap", default=None, help="Explicit speaker→voice JSON")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--duck", type=float, default=0.12,
                    help="Original-audio volume kept under the dub (0=mute)")
    ap.add_argument("--max-atempo", type=float, default=1.7)
    ap.add_argument("--no-sub", action="store_true", help="Skip burning VN subtitle")
    ap.add_argument("--fresh", action="store_true", help="Ignore dub_cache.json")
    ap.add_argument("--hf-token", default=None)
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        sys.exit(f"Video not found: {video}")
    output = Path(args.output).resolve()
    work = output.parent
    work.mkdir(parents=True, exist_ok=True)
    cache_path = work / "dub_cache.json"
    voicemap_path = Path(args.voicemap).resolve() if args.voicemap else work / "voicemap.json"
    hf_token = (args.hf_token or os.environ.get("HF_TOKEN")
                or os.environ.get("HUGGINGFACE_TOKEN") or "").strip()

    total_dur = ffprobe_duration(video)
    if total_dur <= 0:
        sys.exit("Cannot read video duration")
    w, h = probe_size(video)
    print(f"[probe] {w}x{h}, {total_dur:.1f}s")

    # --- transcribe + diarize + translate (cached) --------------------------
    if cache_path.exists() and not args.fresh:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        segments = cache["segments"]
        translations = cache["translations"]
        speakers = cache.get("speakers", [])
        print(f"[cache] reused {len(segments)} segments ({cache_path.name})")
    else:
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / "audio.wav"
            extract_audio(video, wav)
            segments = transcribe(wav, args.model, args.src_lang)
            if not segments:
                sys.exit("No speech detected")
            turns, speakers = ([], [])
            if args.voices == "multi":
                turns, speakers = run_diarize(wav, hf_token)
        assign_speakers(segments, turns)
        translations = translate_batch(segments, "Vietnamese",
                                       extra_rules=CULTIVATION_GLOSSARY)
        cache_path.write_text(json.dumps({
            "segments": segments, "translations": translations, "speakers": speakers,
        }, ensure_ascii=False), encoding="utf-8")
        print(f"[cache] wrote {cache_path.name}")

    if not speakers:  # single voice or diarization unavailable
        speakers = [{"speaker": "SPEAKER_00", "total": round(total_dur, 1),
                     "gender": "unknown"}]
        for seg in segments:
            seg.setdefault("speaker", "SPEAKER_00")

    # --- voice map ----------------------------------------------------------
    if args.voices == "single":
        vmap = {sp["speaker"]: args.voice for sp in speakers}
    else:
        vmap = build_voice_map(speakers, load_voicemap(voicemap_path), args.voice)
    write_voicemap(voicemap_path, vmap, speakers, segments)
    print(f"[voices] {', '.join(f'{k}→{v}' for k, v in vmap.items())}")

    # --- TTS ----------------------------------------------------------------
    templates = load_templates()
    tts_dir = work / "tts_dub"
    tts_dir.mkdir(exist_ok=True)
    items = []
    for i, (seg, vn) in enumerate(zip(segments, translations)):
        if not (vn or "").strip():
            continue
        voice = vmap.get(seg.get("speaker", "SPEAKER_00"), args.voice)
        ref_audio, ref_text = resolve_voice(voice, templates, args.voice)
        items.append({
            "index": i, "text": vn.strip(), "ref_audio": ref_audio,
            "ref_text": ref_text, "speed": args.speed,
            "output": str(tts_dir / f"clip_{i:04d}.wav"),
        })
    print(f"[tts] generating {len(items)} dialogue clips...")
    results = run_tts_batch(items, work)

    # --- fit + assemble dub track ------------------------------------------
    fit_dir = work / "tts_fit"
    fit_dir.mkdir(exist_ok=True)
    placed, failed = [], 0
    for i, seg in enumerate(segments):
        res = results.get(i)
        if not res or not res.get("ok"):
            if results.get(i):
                failed += 1
            continue
        nxt = segments[i + 1]["start"] if i + 1 < len(segments) else total_dur
        window = max(nxt - seg["start"], 0.5)
        fitted = fit_dir / f"fit_{i:04d}.wav"
        fit_clip(res["path"], window, fitted, args.max_atempo)
        placed.append({"start": seg["start"], "clip_path": str(fitted)})
    if not placed:
        sys.exit("No dub clips produced — check TTS output")
    print(f"[dub] placed {len(placed)} clips ({failed} TTS failures)")

    dub_wav = work / "dub_track.wav"
    assemble_dub_track(placed, total_dur, dub_wav)

    # --- subtitle + final render -------------------------------------------
    ass_path = work / "dub_sub.ass"
    if not args.no_sub:
        write_ass(segments, translations, ass_path, w, h, vn_only=True)
    write_srt(segments, translations, output.with_suffix(".srt"))
    mix_and_burn(video, dub_wav, ass_path, output, args.duck, burn_sub=not args.no_sub)

    out_dur = ffprobe_duration(output)
    print("\n" + "=" * 56)
    print(f"✓ Output    : {output}")
    print(f"  Duration  : {out_dur:.1f}s (source {total_dur:.1f}s)")
    print(f"  Speakers  : {len(speakers)} | dialogue lines: {len(items)}")
    print(f"  Voicemap  : {voicemap_path}")
    print(f"  Subtitle  : {'burned VN' if not args.no_sub else 'soft .srt only'}")
    print("=" * 56)


if __name__ == "__main__":
    main()
