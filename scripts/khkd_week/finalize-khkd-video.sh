#!/bin/bash
# Finalize KHKD video: download 4K videos -> TTS -> trim+mix+concat
# Usage: ./finalize-khkd-video.sh <slug>

set -euo pipefail

SLUG="${1:?Usage: $0 <slug>}"
OUTDIR="output/${SLUG}"
IDS_FILE="${OUTDIR}/ids.json"
[ -f "$IDS_FILE" ] || { echo "Missing $IDS_FILE"; exit 1; }

PID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['project_id'])")
VID=$(python3 -c "import json; print(json.load(open('$IDS_FILE'))['video_id'])")
REF_AUDIO="output/_shared/tts_templates/Anh_Khoi_TTS.wav"
REF_TEXT="Năm hai nghìn không trăm hai mươi tư, thế giới thay đổi mãi mãi. Các quốc gia hưng thịnh và sụp đổ, anh hùng xuất hiện từ bóng tối, và những người bình thường đối mặt với thử thách phi thường."
SPEED="0.95"

mkdir -p "${OUTDIR}/tts" "${OUTDIR}/trimmed" "${OUTDIR}/img"

# Get scenes
SCENES_JSON=$(curl -s "http://127.0.0.1:8100/api/scenes?video_id=$VID")

# Generate TTS for each scene
echo "=== TTS gen ==="
echo "$SCENES_JSON" | python3 -c "
import sys, json, subprocess, os
scenes = sorted(json.load(sys.stdin), key=lambda s: s['display_order'])
ref_audio = '${REF_AUDIO}'
ref_text = '''${REF_TEXT}'''
outdir = '${OUTDIR}'

for s in scenes:
    idx3 = f\"{s['display_order']:03d}\"
    sid = s['id']
    out_path = f\"{outdir}/tts/scene_{idx3}_{sid}.wav\"
    if os.path.exists(out_path):
        print(f\"[skip] scene {idx3} TTS exists\")
        continue
    text = (s.get('narrator_text') or '').strip()
    if not text:
        print(f\"[warn] scene {idx3} no narrator_text\")
        continue
    payload = json.dumps({
        'text': text,
        'ref_audio': ref_audio,
        'ref_text': ref_text,
        'speed': float('${SPEED}'),
        'output_path': out_path,
    }, ensure_ascii=False)
    r = subprocess.run(
        ['curl','-s','-m','120','-X','POST','http://127.0.0.1:8100/api/tts/generate',
         '-H','Content-Type: application/json','-d',payload],
        capture_output=True, text=True
    )
    print(f\"[tts] scene {idx3}: {r.stdout[:80]}\")
"

# Download videos (4K if available, else regular) + images
echo "=== Download videos ==="
echo "$SCENES_JSON" | python3 -c "
import sys, json, subprocess, os
from urllib.request import urlretrieve
scenes = sorted(json.load(sys.stdin), key=lambda s: s['display_order'])
outdir = '${OUTDIR}'

for s in scenes:
    idx3 = f\"{s['display_order']:03d}\"
    sid = s['id']
    out_video = f\"{outdir}/trimmed/scene_{idx3}_{sid}_raw.mp4\"
    if os.path.exists(out_video):
        print(f\"[skip] scene {idx3} video exists\")
        continue
    url = s.get('vertical_upscale_url') or s.get('vertical_video_url')
    if not url:
        print(f\"[warn] scene {idx3} no video url\")
        continue
    print(f\"[dl] scene {idx3}...\")
    urlretrieve(url, out_video)
    sz = os.path.getsize(out_video)
    print(f\"[ok] scene {idx3}: {sz//1024}KB\")
"

# Trim+mix each scene, then concat
echo "=== Trim+mix+concat ==="
python3 - <<PYEOF
import os, json, subprocess

outdir = '${OUTDIR}'
slug = '${SLUG}'
scenes_json = subprocess.run(
    ['curl','-s',f'http://127.0.0.1:8100/api/scenes?video_id=${VID}'],
    capture_output=True, text=True
).stdout
scenes = sorted(json.loads(scenes_json), key=lambda s: s['display_order'])

trim_list = []
for s in scenes:
    idx3 = f"{s['display_order']:03d}"
    sid = s['id']
    raw = f"{outdir}/trimmed/scene_{idx3}_{sid}_raw.mp4"
    tts = f"{outdir}/tts/scene_{idx3}_{sid}.wav"
    trimmed = f"{outdir}/trimmed/scene_{idx3}_{sid}.mp4"

    if not os.path.exists(raw):
        print(f"[skip] {idx3} no raw video")
        continue

    # TTS duration + 0.5s buffer
    if os.path.exists(tts):
        tts_dur = float(subprocess.run(
            ['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0',tts],
            capture_output=True, text=True
        ).stdout.strip())
        cut_dur = round(tts_dur + 0.5, 2)
        # Single ffmpeg pass: -ss 1 (skip frame 1), -t cut_dur, mix audio
        cmd = [
            'ffmpeg','-y','-ss','1','-i',raw,'-i',tts,
            '-t',str(cut_dur),
            '-filter_complex',
            '[0:a]volume=0.3[bg];[1:a]volume=1.5[fg];[bg][fg]amix=inputs=2:duration=first[aout]',
            '-map','0:v','-map','[aout]',
            '-c:v','libx264','-preset','medium','-crf','18',
            '-r','24','-pix_fmt','yuv420p',
            '-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
            trimmed
        ]
    else:
        # No TTS: just re-encode trimmed
        cmd = [
            'ffmpeg','-y','-ss','1','-i',raw,
            '-c:v','libx264','-preset','medium','-crf','18',
            '-r','24','-pix_fmt','yuv420p',
            '-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
            trimmed
        ]
    print(f"[trim] {idx3}...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERR] {idx3}: {r.stderr[-300:]}")
        continue
    trim_list.append(trimmed)

# concat list
concat_txt = f"{outdir}/concat.txt"
with open(concat_txt,'w') as f:
    for t in trim_list:
        f.write(f"file '{os.path.basename(t)}'\n")
# concat
final = f"{outdir}/{slug}_narrator_cut.mp4"
cmd = ['ffmpeg','-y','-f','concat','-safe','0',
       '-i','trimmed/'+os.path.basename(concat_txt),
       '-c','copy', f"../../{final}"]
# easier: switch to outdir
os.makedirs(f"{outdir}/trimmed", exist_ok=True)
# Write concat.txt inside trimmed/
concat_inside = f"{outdir}/trimmed/concat.txt"
with open(concat_inside,'w') as f:
    for t in trim_list:
        f.write(f"file '{os.path.basename(t)}'\n")
r = subprocess.run(
    ['ffmpeg','-y','-f','concat','-safe','0','-i',concat_inside,'-c','copy',final],
    capture_output=True, text=True
)
if r.returncode == 0:
    sz = os.path.getsize(final)
    print(f"[OK] Final: {final} ({sz//1024//1024}MB)")
else:
    print(f"[ERR] concat: {r.stderr[-500:]}")
PYEOF

echo "=== Done: ${OUTDIR}/${SLUG}_narrator_cut.mp4 ==="
