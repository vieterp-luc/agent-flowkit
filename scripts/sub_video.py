#!/usr/bin/env python3
"""
sub_video.py — Transcribe + translate + burn dual subtitles onto a video.

Pipeline:
  video.mp4 → extract audio → faster-whisper (zh transcribe + timestamps)
            → Claude translate zh→vi (batch) → write .ass dual-line
            → ffmpeg burn → output.mp4

Usage:
  python3 sub_video.py --video /path/in.mp4 --output /path/out.mp4
  python3 sub_video.py --video in.mp4 --output out.mp4 --model medium --src-lang zh

Args:
  --video        Source video path (required)
  --output       Output video path (default: <video>_subbed.mp4)
  --model        Whisper model: tiny|base|small|medium|large-v3 (default: medium)
  --src-lang     Source language code for Whisper (default: zh)
  --tgt-lang     Target language label (default: Vietnamese)
  --keep-srt     Also save .srt next to output (optional)
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_audio(video: Path, out_wav: Path):
    """Extract 16kHz mono WAV (Whisper-friendly)."""
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(out_wav)
    ], check=True, capture_output=True)


def transcribe(audio: Path, model_name: str, src_lang: str):
    """Return list of {start, end, text} segments."""
    from faster_whisper import WhisperModel
    print(f"[whisper] loading model={model_name}", file=sys.stderr)
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    print(f"[whisper] transcribing lang={src_lang}", file=sys.stderr)
    segments, info = model.transcribe(
        str(audio), language=src_lang, vad_filter=True, beam_size=5
    )
    out = []
    for seg in segments:
        text = seg.text.strip()
        if text:
            out.append({"start": seg.start, "end": seg.end, "text": text})
    print(f"[whisper] {len(out)} segments, audio duration={info.duration:.1f}s",
          file=sys.stderr)
    return out


def _translate_chunk(texts: list, tgt_lang: str, extra_rules: str = "") -> list:
    """Translate one chunk of lines via Claude. Returns list of same length.

    extra_rules: optional extra bullet lines appended to the prompt (e.g. a
    domain glossary). Each line should already start with '- '.
    """
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    extra = ("\n" + extra_rules.strip()) if extra_rules.strip() else ""
    prompt = f"""Translate the following Chinese movie/animation dialogue lines into natural {tgt_lang}.

Rules:
- Preserve emotion and tone (anger, sarcasm, surprise, etc.)
- Keep the SAME number of lines ({len(texts)}), in order
- Each translation should be roughly the same length as the original
- Use casual spoken Vietnamese — match the tone of the original (rude/funny/casual etc.)
- If a line is unclear/garbled (ASR noise), make a best-guess short translation{extra}
- Do NOT add commentary, explanations, markdown, or code fences
- Output ONLY a raw JSON array of strings, nothing else
- Example: ["dòng 1", "dòng 2"]

Input lines:
{numbered}"""

    stream_msg = json.dumps({
        "type": "user",
        "message": {"role": "user", "content": [{"type": "text", "text": prompt}]}
    })
    claude_bin = shutil.which("claude") or "claude"
    r = subprocess.run(
        [claude_bin, "-p", "--input-format", "stream-json",
         "--output-format", "stream-json", "--verbose",
         "--model", "claude-haiku-4-5-20251001"],
        input=stream_msg, capture_output=True, text=True, timeout=180
    )
    raw = ""
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get("type") == "assistant":
                for block in obj.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        raw += block["text"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if "```" in cleaned:
        import re
        m = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
        if m:
            cleaned = m.group(1)

    s = cleaned.find("[")
    e = cleaned.rfind("]") + 1
    if s >= 0 and e > s:
        try:
            arr = json.loads(cleaned[s:e])
            if len(arr) < len(texts):
                arr += [""] * (len(texts) - len(arr))
            return arr[:len(texts)]
        except json.JSONDecodeError as ex:
            print(f"[translate] parse error: {ex}", file=sys.stderr)
            print(f"[translate] raw head: {raw[:300]!r}", file=sys.stderr)
    else:
        print(f"[translate] no array brackets found", file=sys.stderr)
        print(f"[translate] raw head: {raw[:300]!r}", file=sys.stderr)
    return [""] * len(texts)


def translate_batch(segments: list, tgt_lang: str, chunk_size: int = 30,
                    extra_rules: str = "") -> list:
    """Translate segments in chunks to fit Claude output limits.

    extra_rules: optional domain glossary passed through to each chunk.
    """
    if not segments:
        return []
    texts = [s["text"] for s in segments]
    all_out = []
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        print(f"[translate] chunk {i//chunk_size + 1}: lines {i+1}-{i+len(chunk)}",
              file=sys.stderr)
        out = _translate_chunk(chunk, tgt_lang, extra_rules)
        all_out.extend(out)
    miss = sum(1 for x in all_out if not x)
    print(f"[translate] done: {len(all_out)} lines, {miss} empty",
          file=sys.stderr)
    return all_out


def ts(seconds: float) -> str:
    """ASS timestamp: H:MM:SS.cc (centiseconds)."""
    cs = int(round(seconds * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(segments: list, translations: list, out_ass: Path,
              video_w: int, video_h: int, vn_only: bool = False):
    """Write ASS with VN bottom (large) + CN top (small).

    vn_only: when True, emit only the Vietnamese line (skip the CN top line) —
    used for dubbed videos where the CN text is redundant.
    """
    fs_vn = max(24, int(video_h * 0.06))
    fs_cn = max(16, int(video_h * 0.038))
    margin_v_vn = max(20, int(video_h * 0.04))
    margin_v_cn = max(20, int(video_h * 0.04))

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_w}
PlayResY: {video_h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: VN,Arial,{fs_vn},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.4,1.0,2,40,40,{margin_v_vn},1
Style: CN,Arial,{fs_cn},&H00FFFF80,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.6,0.8,8,40,40,{margin_v_cn},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def escape(s: str) -> str:
        return s.replace("\n", " ").replace("{", "(").replace("}", ")").strip()

    lines = []
    for seg, vn in zip(segments, translations):
        start = ts(seg["start"])
        end = ts(seg["end"])
        cn_text = escape(seg["text"])
        vn_text = escape(vn) if vn else ""
        if cn_text and not vn_only:
            lines.append(f"Dialogue: 0,{start},{end},CN,,0,0,0,,{cn_text}")
        if vn_text:
            lines.append(f"Dialogue: 1,{start},{end},VN,,0,0,0,,{vn_text}")

    out_ass.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def burn(video: Path, ass: Path, output: Path):
    """ffmpeg burn ASS subtitles, copy audio."""
    ass_escaped = str(ass).replace(":", "\\:").replace("'", "\\'")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video),
        "-vf", f"ass={ass_escaped}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output)
    ], check=True, capture_output=True)


def probe_size(video: Path) -> tuple[int, int]:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True
    )
    parts = r.stdout.strip().split(",")
    return (int(parts[0]), int(parts[1])) if len(parts) == 2 else (852, 480)


def write_srt(segments: list, translations: list, out_srt: Path):
    def ts_srt(t: float) -> str:
        ms = int(round(t * 1000))
        h, rem = divmod(ms, 3600000)
        m, rem = divmod(rem, 60000)
        s, ms = divmod(rem, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, (seg, vn) in enumerate(zip(segments, translations), 1):
        lines.append(str(i))
        lines.append(f"{ts_srt(seg['start'])} --> {ts_srt(seg['end'])}")
        text = vn or seg["text"]
        lines.append(text)
        lines.append("")
    out_srt.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--output", default=None)
    ap.add_argument("--model", default="medium")
    ap.add_argument("--src-lang", default="zh")
    ap.add_argument("--tgt-lang", default="Vietnamese")
    ap.add_argument("--keep-srt", action="store_true")
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        sys.exit(f"Video not found: {video}")
    output = Path(args.output).resolve() if args.output else \
        video.with_name(video.stem + "_subbed.mp4")

    w, h = probe_size(video)
    print(f"[probe] {w}x{h}", file=sys.stderr)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        wav = td / "audio.wav"
        ass = td / "subs.ass"

        extract_audio(video, wav)
        segments = transcribe(wav, args.model, args.src_lang)
        if not segments:
            sys.exit("No speech detected")

        translations = translate_batch(segments, args.tgt_lang)
        write_ass(segments, translations, ass, w, h)

        if args.keep_srt:
            write_srt(segments, translations, output.with_suffix(".srt"))

        burn(video, ass, output)

    print(f"\n✓ Output: {output}")


if __name__ == "__main__":
    main()
