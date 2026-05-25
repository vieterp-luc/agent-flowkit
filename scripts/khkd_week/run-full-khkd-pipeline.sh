#!/bin/bash
# Full pipeline: create-project (if needed) -> refs -> images W1+W2 -> videos -> finalize
# Usage: ./run-full-khkd-pipeline.sh <spec.json>

set -euo pipefail

SPEC="${1:?Usage: $0 <spec.json>}"
SLUG=$(python3 -c "import json; print(json.load(open('$SPEC'))['slug'])")
IDS="output/${SLUG}/ids.json"

# Step 1: Create project if not exists
if [ ! -f "$IDS" ]; then
  echo "=== CREATE PROJECT ==="
  python3 scripts/khkd_week/create-khkd-project.py "$SPEC"
fi

PID=$(python3 -c "import json; print(json.load(open('$IDS'))['project_id'])")
VID=$(python3 -c "import json; print(json.load(open('$IDS'))['video_id'])")
SCENE_IDS=$(python3 -c "
import json
ids = json.load(open('$IDS'))['scene_ids']
print(','.join(ids[str(i)] for i in range(5)))
")
S0=$(echo $SCENE_IDS | cut -d, -f1)
S1=$(echo $SCENE_IDS | cut -d, -f2)
S2=$(echo $SCENE_IDS | cut -d, -f3)  # CONTINUATION
S3=$(echo $SCENE_IDS | cut -d, -f4)
S4=$(echo $SCENE_IDS | cut -d, -f5)

poll() {
  local PATH_ARG="$1" TYPE="$2" MAX="$3"
  for i in $(seq 1 $MAX); do
    sleep 30
    local ST=$(curl -s "http://127.0.0.1:8100/api/requests/batch-status?${PATH_ARG}&type=${TYPE}")
    echo "  poll $i: $ST"
    local D=$(echo "$ST" | python3 -c "import sys,json; print(json.load(sys.stdin).get('done'))")
    if [ "$D" = "True" ]; then return 0; fi
  done
  echo "TIMEOUT polling $TYPE"
  return 1
}

# Step 2: Refs (if not done)
NEED_REFS=$(curl -s "http://127.0.0.1:8100/api/projects/$PID/characters" | python3 -c "
import sys,json
items = json.load(sys.stdin)
todo = [c['id'] for c in items if not c.get('media_id')]
print(','.join(todo))
")
if [ -n "$NEED_REFS" ]; then
  echo "=== REFS ==="
  REQS=$(python3 -c "
import json
pid='$PID'; ids='$NEED_REFS'.split(',')
print(json.dumps({'requests':[{'type':'GENERATE_CHARACTER_IMAGE','character_id':i,'project_id':pid} for i in ids]}))
")
  curl -s -X POST "http://127.0.0.1:8100/api/requests/batch" -H "Content-Type: application/json" -d "$REQS" > /dev/null
  poll "project_id=$PID" "GENERATE_CHARACTER_IMAGE" 8
fi

# Step 3: Wave 1 ROOT images
echo "=== IMAGES W1 ==="
curl -s -X POST "http://127.0.0.1:8100/api/requests/batch" -H "Content-Type: application/json" \
  -d "{\"requests\":[
    {\"type\":\"GENERATE_IMAGE\",\"scene_id\":\"$S0\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_IMAGE\",\"scene_id\":\"$S1\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_IMAGE\",\"scene_id\":\"$S3\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_IMAGE\",\"scene_id\":\"$S4\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"}
  ]}" > /dev/null
poll "video_id=$VID" "GENERATE_IMAGE" 8

# Step 4: Wave 2 CONTINUATION
echo "=== IMAGES W2 ==="
curl -s -X POST "http://127.0.0.1:8100/api/requests/batch" -H "Content-Type: application/json" \
  -d "{\"requests\":[{\"type\":\"EDIT_IMAGE\",\"scene_id\":\"$S2\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"}]}" > /dev/null
poll "video_id=$VID" "EDIT_IMAGE" 6

# Step 5: All 5 video gens
echo "=== VIDEOS ==="
curl -s -X POST "http://127.0.0.1:8100/api/requests/batch" -H "Content-Type: application/json" \
  -d "{\"requests\":[
    {\"type\":\"GENERATE_VIDEO\",\"scene_id\":\"$S0\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_VIDEO\",\"scene_id\":\"$S1\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_VIDEO\",\"scene_id\":\"$S2\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_VIDEO\",\"scene_id\":\"$S3\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"},
    {\"type\":\"GENERATE_VIDEO\",\"scene_id\":\"$S4\",\"project_id\":\"$PID\",\"video_id\":\"$VID\",\"orientation\":\"VERTICAL\"}
  ]}" > /dev/null
poll "video_id=$VID" "GENERATE_VIDEO" 12

# Step 6: Finalize (TTS + concat)
echo "=== FINALIZE ==="
bash scripts/khkd_week/finalize-khkd-video.sh "$SLUG"

echo "=== DONE: $SLUG ==="
curl -s http://127.0.0.1:8100/api/flow/credits | python3 -c "import sys,json; print('Credits remaining:', json.load(sys.stdin).get('credits'))"
