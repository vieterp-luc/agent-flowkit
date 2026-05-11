#!/usr/bin/env bash
# Test harness for Ken Burns FFmpeg helper
# Generates test images via ImageMagick, applies all 8 motion presets,
# concatenates 4 clips with crossfade, then verifies output via ffprobe.

set -euo pipefail

OUT_DIR="/tmp/ken-burns-test"
mkdir -p "$OUT_DIR"

echo "=== Ken Burns Test Harness ==="
echo "Output dir: $OUT_DIR"

# --- 1. Generate test images ---
echo ""
echo "--- Generating test images ---"

if command -v convert &>/dev/null; then
  # Landscape 1920x1080
  convert -size 1920x1080 \
    gradient:"#1a237e-#e91e63" \
    -gravity Center \
    -pointsize 80 -fill white \
    -annotate 0 "Ken Burns Test\nLandscape 16:9" \
    "$OUT_DIR/test-landscape.jpg"

  # Portrait 1080x1920
  convert -size 1080x1920 \
    gradient:"#004d40-#ff6f00" \
    -gravity Center \
    -pointsize 80 -fill white \
    -annotate 0 "Ken Burns Test\nPortrait 9:16" \
    "$OUT_DIR/test-portrait.jpg"

  # Square 1080x1080
  convert -size 1080x1080 \
    gradient:"#311b92-#00bcd4" \
    -gravity Center \
    -pointsize 70 -fill white \
    -annotate 0 "Ken Burns Test\nSquare 1:1" \
    "$OUT_DIR/test-square.jpg"

  echo "  Images created via ImageMagick."
else
  # Fallback: download a CC0 test image
  echo "  ImageMagick not found — downloading fallback test image..."
  curl -sL "https://picsum.photos/1920/1080" -o "$OUT_DIR/test-landscape.jpg"
  curl -sL "https://picsum.photos/1080/1920" -o "$OUT_DIR/test-portrait.jpg"
  curl -sL "https://picsum.photos/1080/1080" -o "$OUT_DIR/test-square.jpg"
fi

# Alias for convenience
LANDSCAPE="$OUT_DIR/test-landscape.jpg"
PORTRAIT="$OUT_DIR/test-portrait.jpg"

# --- 2. Apply all 8 motion presets ---
echo ""
echo "--- Applying 8 motion presets (1920x1080, 4s each) ---"

PRESETS=("zoom_in" "zoom_out" "pan_left" "pan_right" "pan_up" "pan_down" "parallax" "static")

for PRESET in "${PRESETS[@]}"; do
  OUT="$OUT_DIR/preset-${PRESET}.mp4"
  echo -n "  $PRESET ... "

  if [ "$PRESET" = "static" ]; then
    # Static: 2s freeze
    ffmpeg -y -loop 1 -i "$LANDSCAPE" \
      -t 2 \
      -vf "scale=1920:1080,fps=30" \
      -c:v libx264 -preset fast -crf 18 \
      -pix_fmt yuv420p -r 30 \
      -movflags +faststart -an \
      "$OUT" 2>/dev/null
  else
    FRAMES=$((4 * 30))
    W=1920
    H=1080

    case "$PRESET" in
      zoom_in)
        VF="scale=$((W*2)):$((H*2)),zoompan=z='min(zoom+0.0015,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
      zoom_out)
        VF="scale=$((W*2)):$((H*2)),zoompan=z='if(lte(on,1),1.2,max(zoom-0.0015,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
      pan_left)
        VF="scale=$((W*2)):$((H*2)),zoompan=z=1.2:x='iw*0.05+(iw*0.6)*on/${FRAMES}':y='ih*0.2':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
      pan_right)
        VF="scale=$((W*2)):$((H*2)),zoompan=z=1.2:x='iw*0.65-(iw*0.6)*on/${FRAMES}':y='ih*0.2':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
      pan_up)
        VF="scale=$((W*2)):$((H*2)),zoompan=z=1.2:x='iw*0.2':y='ih*0.5-(ih*0.3)*on/${FRAMES}':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
      pan_down)
        VF="scale=$((W*2)):$((H*2)),zoompan=z=1.2:x='iw*0.2':y='ih*0.2+(ih*0.3)*on/${FRAMES}':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
      parallax)
        VF="scale=$((W*2)):$((H*2)),zoompan=z='min(zoom+0.001,1.15)':x='iw*0.05+(iw*0.3)*on/${FRAMES}':y='ih*0.5-(ih*0.2)*on/${FRAMES}':d=${FRAMES}:s=${W}x${H}:fps=30" ;;
    esac

    ffmpeg -y -loop 1 -i "$LANDSCAPE" \
      -t 4 -vf "$VF" \
      -c:v libx264 -preset fast -crf 18 \
      -pix_fmt yuv420p -r 30 \
      -movflags +faststart -an \
      "$OUT" 2>/dev/null
  fi

  if [ -f "$OUT" ]; then
    echo "OK"
  else
    echo "FAILED"
  fi
done

# --- 3. Test text overlay (bold_caption) ---
echo ""
echo "--- Text overlay test (bold_caption) ---"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TEXT_OUT="$OUT_DIR/text-overlay-bold-caption.mp4"
FRAMES_4=$((4 * 30))
W=1920; H=1080

if [ -f "$FONT" ]; then
  FONT_CLAUSE="fontfile='${FONT}':"
else
  FONT_CLAUSE=""
fi

ffmpeg -y -loop 1 -i "$LANDSCAPE" \
  -t 4 \
  -vf "scale=$((W*2)):$((H*2)),zoompan=z='min(zoom+0.0015,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${FRAMES_4}:s=${W}x${H}:fps=30,drawtext=${FONT_CLAUSE}text='Atomic Habits - James Clear':fontsize=72:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.82" \
  -c:v libx264 -preset fast -crf 18 \
  -pix_fmt yuv420p -r 30 \
  -movflags +faststart -an \
  "$TEXT_OUT" 2>/dev/null \
  && echo "  bold_caption overlay: OK" || echo "  bold_caption overlay: FAILED"

# --- 4. Concat 4 clips with xfade ---
echo ""
echo "--- Concat 4 clips with xfade=0.5s ---"
CONCAT_OUT="$OUT_DIR/concat-4clips.mp4"
XFADE=0.5
DUR=4.0

# Clips: zoom_in, pan_left, zoom_out, pan_right
C1="$OUT_DIR/preset-zoom_in.mp4"
C2="$OUT_DIR/preset-pan_left.mp4"
C3="$OUT_DIR/preset-zoom_out.mp4"
C4="$OUT_DIR/preset-pan_right.mp4"

# Calculate xfade offsets
# offset_1 = dur_0 - xfade = 4.0 - 0.5 = 3.5
# offset_2 = offset_1 + dur_1 - xfade = 3.5 + 4.0 - 0.5 = 7.0
# offset_3 = offset_2 + dur_2 - xfade = 7.0 + 4.0 - 0.5 = 10.5
FILTER="[0:v][1:v]xfade=transition=fade:duration=${XFADE}:offset=3.500[v01];\
[v01][2:v]xfade=transition=fade:duration=${XFADE}:offset=7.000[v012];\
[v012][3:v]xfade=transition=fade:duration=${XFADE}:offset=10.500[vout]"

ffmpeg -y \
  -i "$C1" -i "$C2" -i "$C3" -i "$C4" \
  -filter_complex "$FILTER" \
  -map "[vout]" \
  -c:v libx264 -preset fast -crf 18 \
  -pix_fmt yuv420p -r 30 \
  -movflags +faststart -an \
  "$CONCAT_OUT" 2>/dev/null \
  && echo "  Concat: OK" || echo "  Concat: FAILED"

# --- 5. Verify outputs with ffprobe ---
echo ""
echo "--- ffprobe verification ---"

verify() {
  local file="$1"
  local label="$2"
  if [ ! -f "$file" ]; then
    echo "  [$label] MISSING: $file"
    return
  fi
  local info
  info=$(ffprobe -v quiet \
    -show_entries stream=width,height,r_frame_rate \
    -show_entries format=duration \
    -of csv=p=0 "$file" 2>/dev/null | tr '\n' ' ')
  echo "  [$label] $info"
}

for PRESET in "${PRESETS[@]}"; do
  verify "$OUT_DIR/preset-${PRESET}.mp4" "$PRESET"
done
verify "$TEXT_OUT" "text-overlay"
verify "$CONCAT_OUT" "concat-4clips"

echo ""
echo "=== Test complete. Review clips in $OUT_DIR ==="
echo "Open with: open $OUT_DIR  (macOS)"
