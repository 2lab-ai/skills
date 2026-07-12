#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# verify-scenes.sh — Render each scene as a still image for review
#
# Takes a video workspace dir (output of build-from-script.sh Step 1+2)
# and renders a PNG per scene at the scene's midpoint frame.
#
# Usage:
#   ./scripts/verify-scenes.sh <workspace_dir> [output_dir]
#
# Output:
#   <output_dir>/scene-001.png
#   <output_dir>/scene-002.png
#   ...
#   <output_dir>/manifest.json  (scene metadata for review)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

WORKSPACE="${1:?Usage: verify-scenes.sh <workspace_dir> [output_dir]}"
OUTPUT_DIR="${2:-/tmp/scene-verify}"

# Colors
BLUE='\033[34m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; NC='\033[0m'
info()    { echo -e "${BLUE}[verify]${NC} $1"; }
success() { echo -e "${GREEN}[verify]${NC} $1"; }
warn()    { echo -e "${YELLOW}[verify]${NC} $1"; }
error()   { echo -e "${RED}[verify]${NC} $1"; }

# Validate workspace
if [ ! -f "$WORKSPACE/public/render-config.json" ]; then
  error "render-config.json not found in $WORKSPACE/public/"
  error "Run build-from-script.sh first (Steps 1-2), or pass the workspace dir."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Parse render-config to get scene frame ranges
RENDER_CONFIG="$WORKSPACE/public/render-config.json"

# Extract scene info: id, type, startFrame, endFrame, narration
python3 -c "
import json, sys

config = json.load(open('$RENDER_CONFIG'))
scenes = config.get('scenes', [])
fps = config.get('fps', 30)
total_frames = config.get('totalDurationInFrames', 0)

manifest = []
cumulative = 0

# Calculate frame ranges from tts-metadata
tts_path = '$WORKSPACE/public/tts-metadata.json'
try:
    tts_data = json.load(open(tts_path))
    tts_map = {t['sceneId']: t for t in tts_data}
except:
    tts_map = {}

for i, scene in enumerate(scenes):
    sid = scene.get('id', f's{i+1:03d}')
    stype = scene.get('type', 'unknown')
    narr = scene.get('narration', '')[:80]

    # Get duration from tts metadata
    tts = tts_map.get(sid, {})
    dur_ms = tts.get('durationMs', 3000)
    dur_frames = int((dur_ms / 1000) * fps)

    start_frame = cumulative
    end_frame = cumulative + dur_frames
    mid_frame = start_frame + dur_frames // 2

    manifest.append({
        'index': i + 1,
        'id': sid,
        'type': stype,
        'narration': narr,
        'startFrame': start_frame,
        'endFrame': end_frame,
        'midFrame': mid_frame,
        'durationMs': dur_ms,
    })
    cumulative = end_frame

# Write manifest
json.dump(manifest, open('$OUTPUT_DIR/manifest.json', 'w'), indent=2, ensure_ascii=False)

# Print for shell consumption
for s in manifest:
    print(f\"{s['index']}|{s['id']}|{s['type']}|{s['midFrame']}|{s['narration']}\")
" > "$OUTPUT_DIR/scene_list.txt"

SCENE_COUNT=$(wc -l < "$OUTPUT_DIR/scene_list.txt")
info "Found $SCENE_COUNT scenes to verify"
echo ""

# Browser detection
BROWSER_EXEC=""
if command -v chromium-browser &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium-browser)"
elif command -v chromium &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium)"
elif command -v google-chrome &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v google-chrome)"
fi

# Render each scene as a still
cd "$WORKSPACE"
export NODE_OPTIONS="--max-old-space-size=8192"

while IFS='|' read -r idx sid stype mid_frame narr; do
  OUTFILE="$OUTPUT_DIR/scene-$(printf '%03d' "$idx").png"
  info "  [$idx/$SCENE_COUNT] $sid ($stype) @ frame $mid_frame"

  npx remotion still src/Root.tsx VideoComposition "$OUTFILE" \
    --frame "$mid_frame" \
    --image-format png \
    --log error \
    $BROWSER_EXEC 2>/dev/null

  if [ -f "$OUTFILE" ]; then
    SIZE=$(du -h "$OUTFILE" | cut -f1)
    success "    → $OUTFILE ($SIZE)"
  else
    warn "    → FAILED to render frame $mid_frame"
  fi
done < "$OUTPUT_DIR/scene_list.txt"

echo ""
success "═══════════════════════════════════════════"
success "  Scene verification images ready!"
success "  Directory: $OUTPUT_DIR"
success "  Manifest:  $OUTPUT_DIR/manifest.json"
success "  Images:    $OUTPUT_DIR/scene-*.png"
success "═══════════════════════════════════════════"
